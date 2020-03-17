# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import copy
import re


def get_view_builder(req):
    base_url = req.application_url
    return ViewBuilder(base_url)


class ViewBuilder(object):
    def __init__(self, base_url):
        """Initialize ViewBuilder.

        :param base_url: url of the root wsgi application
        """
        self.base_url = base_url

    def build_versions(self, versions):
        views = [self._build_version(versions[key])
                 for key in sorted(list(versions.keys()))]
        return dict(versions=views)

    def _build_version(self, version):
        view = copy.deepcopy(version)
        return view

    def _get_base_url_without_version(self):
        """Get the base URL with out the /v1 suffix."""
        return re.sub('v[1-9]+/?$', '', self.base_url)
