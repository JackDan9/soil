# Copyright 2020 Soil, Inc.
# Copyright 2011 OpenStack Foundation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

from oslo_config import cfg
from oslo_log import log as logging
from oslo_middleware import request_id
from oslo_serialization import jsonutils
import webob.dec
import webob.exc

from soil.api.server import wsgi
from soil import context
from soil.wsgi import common as base_wsgi

auth_opts = [
    cfg.StrOpt(
        'auth_strategy',
        default='keystone',
        choices=['keystone', 'noauth'],
        help='The strategy to use for auth.')
]

CONF = cfg.CONF
CONF.register_opts(auth_opts)

LOG = logging.getLogger(__name__)


def pipeline_factory(loader, global_conf, **local_conf):
    """A paste pipeline replica that keys off of auth_strategy."""
    pipeline = local_conf[CONF.auth_strategy]
    pipeline = pipeline.split()
    filters = [loader.get_filter(n) for n in pipeline[:-1]]
    app = loader.get_app(pipeline[-1])
    filters.reverse()
    for filter in filters:
        app = filter(app)
    return app


class InjectContext(base_wsgi.Middleware):
    """Add a 'soil.context' to WSGI environ."""

    def __init__(self, context, *args, **kwargs):
        self.context = context
        super(InjectContext, self).__init__(*args, **kwargs)

    @webob.dec.wsgify(RequestClass=base_wsgi.Request)
    def __call__(self, req):
        req.environ['soil.context'] = self.context
        return self.application


class SoilKeystoneContext(base_wsgi.Middleware):
    """Make a request context from keystone headers."""

    @webob.dec.wsgify(RequestClass=base_wsgi.Request)
    def __call__(self, req):
        user_id = req.headers.get('X_USER')
        user_id = req.headers.get('X_USER_ID', user_id)
        if user_id is None:
            LOG.debug("Neither X_USER_ID nor X_USER found in request")
            return webob.exc.HTTPUnauthorized()
        # get the roles
        roles = [r.strip() for r in req.headers.get('X_ROLE', '').split(',')]
        if 'X_TENANT_ID' in req.headers:
            # This is the new header since Keystone went to ID/Name
            project_id = req.headers['X_TENANT_ID']
        else:
            # This is for legacy compatibility
            project_id = req.headers['X_TENANT']

        project_name = req.headers.get('X_TENANT_NAME')

        req_id = req.environ.get(request_id.ENV_REQUEST_ID)

        # Get the auth token
        auth_token = req.headers.get('X_AUTH_TOKEN',
                                     req.headers.get('X_STORAGE_TOKEN'))

        service_catalog = None
        if req.headers.get('X_SERVICE_CATALOG') is not None:
            try:
                catalog_header = req.headers.get('X_SERVICE_CATALOG')
                service_catalog = jsonutils.loads(catalog_header)
            except ValueError:
                raise webob.exc.HTTPInternalServerError(
                    explanation=_('Invalid service catalog json.'))

        ctx = context.RequestContext(user_id,
                                     project_id,
                                     project_name=project_name,
                                     roles=roles,
                                     auth_token=auth_token,
                                     service_catalog=service_catalog,
                                     request_id=req_id)

        req.environ['soil.context'] = ctx
        return self.application


class NoAuthMiddleware(base_wsgi.Middleware):
    """Return a fake token if one isn't specified."""

    @webob.dec.wsgify(RequestClass=wsgi.Request)
    def __call__(self, req):
        if 'X-Auth-Token' not in req.headers:
            user_id = req.headers.get('X-Auth-User', 'admin')
            project_id = req.headers.get('X-Auth-Project-Id', 'admin')
            os_url = os.path.join(req.url, project_id)
            res = webob.Response()
            # NOTE(vish): This is expecting and returning Auth(1.1), whereas
            #             keystone uses 2.0 auth.  We should probably allow
            #             2.0 auth here as well.
            res.headers['X-Auth-Token'] = '%s:%s' % (user_id, project_id)
            res.headers['X-Server-Management-Url'] = os_url
            res.content_type = 'text/plain'
            res.status = '204'
            return res

        token = req.headers['X-Auth-Token']
        user_id, _sep, project_id = token.partition(':')
        project_id = project_id or user_id
        remote_address = getattr(req, 'remote_address', '127.0.0.1')
        ctx = context.RequestContext(user_id,
                                     project_id,
                                     is_admin=True,
                                     remote_address=remote_address)

        req.environ['soil.context'] = ctx
        return self.application
