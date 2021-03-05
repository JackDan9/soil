# Copyright 2020 Soil, Inc.

import base64
import functools

import webob.exc

from soil.db import api as db_api
from soil.utils.crypto_rsa import RSALicense


def verify_license_signature(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        license = db_api.license_get()
        rsa = RSALicense()
        is_signature_correct = rsa.verify_license_signature(license)
        if is_signature_correct:
            return func(*args, **kwargs)
        else:
            return webob.exc.HTTPForbidden("License Signature has been destroyed")
    return wrapper


# check_provider_nums 
def check_provider_nums(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        license = db_api.license_get()
        license_message = _parse_license_message(license.license)
        provider_nums = license_message.get('provider_nums')
        used_providers = len(db_api.vcenter_get_all())

        # if provider_nums is 0, that means we don't limit providers in license
        if used_providers < int(provider_nums) or int(provider_nums) == 0:
            return func(*args, **kwargs)
        else:
            return webob.exc.HTTPForbidden("The number of allowed providers "
                                           "has reached the upper limit")
    return wrapper


def _parse_license_message(license):
    license = eval(base64.b64decode(license))
    message = [i.strip() for i in license.get('message', '').split(',')]
    message_dict = {}
    for m in message:
        key, value = m.split(':', 1)
        message_dict[key] = value
    return message_dict
