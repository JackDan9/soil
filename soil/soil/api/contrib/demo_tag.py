# Copyright 2020 Soil, Inc.

import webob.exc

from soil.api import extensions
from soil.api.server import wsgi
from soil.i18n import _


class DemoTagController(wsgi.Controller):

    @staticmethod
    def _extract_tag(body):
        tag = None
        attr = "%s:tag" % Demo_tag.alias
        try:
            if attr in body:
                tag = body[attr]
        except ValueError as e:
            msg = _("malformed demo attribute %s", str(e))
            raise webob.exc.HTTPBadRequest(explanation=msg)

        return tag

    @wsgi.extends
    def create(self, req, body):
        tag = self._extract_tag(body)
        if tag:
            body["state"] = str(tag) + ":" + body["state"]
        yield


class Demo_tag(extensions.ExtensionDescriptor):
    """pass arbitrary key/value pairs to the demo"""
    name = "DemoTag"
    alias = "DEMO_TAG"
    updated = "2020-12-23T17:51:35-05:00"

    def get_controller_extensions(self):
        controller = DemoTagController()
        extension = extensions.ControllerExtension(self, "demos", controller)
        return [extension]
