# Copyright 2011 OpenStack Foundation
#
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

from oslo_config import cfg

extension_opts = [
    cfg.MultiStrOpt(
        "soil_api_extension",
        default=['soil.api.contrib.demo_tag.Demo_tag'],
        help="soil extensions to load."
    )
]


def register_opts(conf):
    conf.register_opts(extension_opts)

def list_opts():
    return {'DEFAULT': extension_opts}
