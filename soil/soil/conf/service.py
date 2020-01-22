# needs:check_deprecation_status


# Copyright 2015 OpenStack Foundation
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

service_opts = [
    cfg.StrOpt(
        'soil_api_listen',
        default="0.0.0.0",
        help=help="""
IP address on which the Soil API will listen.
The Soil API service listens on this IP address for incoming
requests.
"""),
    cfg.PortOpt('soil_api__listen_port',
               default=8087,
               help="""
Port on which the Soil API will listen.
The Soil API service listens on this port number for incoming
requests.
"""),
    cfg.IntOpt('soil_api_workers',
               min=1,
               help="""
Number of workers for Soil API service. The default will be the number
of CPUs available.

Soil API services can be configured to run as multi-process (workers).
This overcomes the problem of reduction in throughput when API request
concurrency increases. Soil API service will run in the specified
number of processes.

Possible Values:

* Any positive integer
* None (default value)
"""),
    cfg.BoolOpt('use_rpc',
                default=False,
                help="""
    Set Soil API services whether to enable RPC service.

    Possible Values:

    * True (Soil API services to enable RPC service.)
    * False (default value Soil API services not to enable RPC service.)
"""),
]


def register_opts(conf):
    conf.register_opts(service_opts)


def list_opts():
    return {'DEFAULT': service_opts}
