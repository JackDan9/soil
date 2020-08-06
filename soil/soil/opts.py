# Copyright 2019 Open Source Community, Inc.

import copy
import itertools

from soil.api import extensions
from soil.api.middleware import auth
from soil.engine import manager
from soil import service
from soil.wsgi import server


def list_opts():
  """Entry point for oslo-config-generator"""
  return [('DEFAULT', itertools.chain(
    copy.deepcopy(auth.auth_opts),
    copy.deepcopy(extensions.extension_opts),
    copy.deepcopy(manager.engine_opts),
    copy.deepcopy(server.wsgi_opts)
  ))]