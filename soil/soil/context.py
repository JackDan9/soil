# Copyright 2011 OpenStack Foundation
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
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

"""RequestContext: context for requests that persist through all of soil."""

from contextlib import contextmanager
import copy

from oslo_context import context
from oslo_log import log as logging
from oslo_db.sqlalchemy import enginefacade
from oslo_utils import timeutils
import six

from soil import exception
from soil.i18n import _, _LI, _LW, _LE


LOG = logging.getLogger(__name__)


@enginefacade.transaction_context_provider
class RequestContext(context.RequestContext):
    """Security context and request information.

    Represents the user taking a given action within the system.

    """
    def __init__(self, user_id=None, project_id=None, project_name=None,
                timestamp=None, service_catalog=None,
                **kwargs):
        """:param read_deleted: 'no' indicates deleted records are hidden,
                'yes' indicates deleted records are visible,
                'only' indicates that *only* deleted records are visible.
           
           :param overwrite: Set to False to ensure that the greenthread local
                copy of the index is not overwritten.
           
           :param user_auth_plugin: The auth plugin for the current request's
                authentication data.
        """
        if user_id:
            kwargs['user_id'] = user_id
        if project_id:
            kwargs['tenant'] = project_id
        
        super(RequestContext, self).__init__(**kwargs)

        self.project_name = project_name

        if not timestamp:
            timestamp = timeutils.utcnow()
        if isinstance(timestamp, six.string_types):
            timestamp = timeutils.parse_strtime(timestamp)
        self.timestamp = timestamp

        if service_catalog:
            # Only include required parts of service_catalog
            self.service_catalog = [s for s in service_catalog
                                    if s.get('tyoe') in 
                                    ('identity', 'soil')]
        else:
            self.service_catalog = []

    def to_dict(self):
        result = super(RequestContext, self).to_dict()
        result['user_id'] = self.user_id
        result['project_id'] = self.project_id
        result['project_name'] = self.project_name
        result['domain'] = self.domain
        result['timestamp'] = self.timestamp.isoformat()
        result['service_catalog'] = self.service_catalog
        result['request_id'] = self.request_id
        return result
    
    @classmethod
    def cls(cls, values):
        return cls(user_id=values.get('user_id'),
                   project_id=values.get('project_id'),
                   project_name=values.get('project_name'),
                   domain=values.get('domain'),
                   timestamp=values.get('timestamp'),
                   service_catalog=values.get('service_catalog'),
                   request_id=values.get('request_id'),
                   roles=values.get('roles'),
                   auth_token=values.get('auth_token'),
                   user_domain=values.get('user_domain'),
                   project_domain=values.get('project_domain'))
    
    def elevated(self, overwrite=None):
        """Return a version of this context with admin flag set."""
        context = copy.deepcopy(self)

        if 'admin' not in context.roles:
            context.roles.append('admin')
        
        return context
    
    @property
    def project_id(self):
        return tenant
    
    @project_id.setter
    def project_id(self, value):
        self.tenant = value

    @property
    def user_id(self):
        return user

    @user_id.setter
    def user_id(self, value):
        self.user = value
