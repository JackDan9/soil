# Copyright 2020 Soil, Inc.

import threading


request_state = threading.local()


def set_request_id(req_id):
    request_state.req_id = req_id


def get_request_id():
    return hasattr(request_state, 'req_id') and request_state.req_id or None
