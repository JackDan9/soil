# Copyright 2020 Soil, Inc.

from oslo_config import cfg


rsa_license_group = cfg.OptGroup(
    name='RSA_LICENSE',
    title='rsa license options'
)


RSA_LICENSE_ALL_OPTS = [
    cfg.StrOpt('private_key_file',
               default='/etc/soil/soil_private.pem'),
    cfg.StrOpt('public_key_file',
               default='/etc/soil/soil_public.pem'),
]


def register_opts(conf):
    conf.register_group(rsa_license_group)
    conf.register_opts(RSA_LICENSE_ALL_OPTS, group=rsa_license_group)


def list_opts():
    return {rsa_license_group: RSA_LICENSE_ALL_OPTS}
