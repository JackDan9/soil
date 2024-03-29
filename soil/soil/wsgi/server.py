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

"""Methods for working with eventlet WSGI servers."""

from __future__ import print_function

import os
import socket
import ssl

import eventlet
import eventlet.wsgi
import greenlet
from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import service
from oslo_utils import excutils

from soil import exception
from soil.i18n import _, _LE, _LW, _LI


wsgi_opts = [
    cfg.StrOpt('api_paste_config',
               default="/etc/soil/api-paste.ini",
               help='File name for the paste.deploy config for soil-api'),
    cfg.IntOpt('tcp_keepidle',
               default=600,
               help="Sets the value of TCP_KEEPIDLE in seconds for each "
                    "server socket. Not supported on OS X."),
    cfg.StrOpt('ssl_ca_file',
               default=None,
               help="CA certificate file to use to verify "
                    "connecting clients"),
    cfg.StrOpt('ssl_cert_file',
               default=None,
               help="Certificate file to use when starting "
                    "the server securely"),
    cfg.StrOpt('ssl_key_file',
               default=None,
               help="Private key file to use when starting "
                    "the server securely"),
    cfg.IntOpt('max_header_line',
               default=16384,
               help="Maximum line size of message headers to be accepted. "
                    "max_header_line may need to be increased when using "
                    "large tokens (typically those generated by the "
                    "Keystone v3 API with big service catalogs)."),
    cfg.IntOpt('client_socket_timeout',
               default=900,
               help="Timeout for client connections\' socket operations. "
                    "If an incoming connection is idle for this number of "
                    "seconds it will be closed. A value of \'0\' means "
                    "wait forever."),
    cfg.BoolOpt('wsgi_keep_alive',
                default=True,
                help='If False, closes the client socket connection '
                     'explicitly. Setting it to True to maintain backward '
                     'compatibility. Recommended setting is set it to False.'),
]

CONF = cfg.CONF
CONF.register_opts(wsgi_opts)

LOG = logging.getLogger(__name__)


class Server(service.ServiceBase):
    """Server class to manage a WSGI server, serving a WSGI application."""

    default_pool_size = 1000

    def __init__(self, name, app, host=None, port=None, pool_size=None,
                 protocol=eventlet.wsgi.HttpProtocol, backlog=128,
                 use_ssl=False):
        """Initialize, but do not start, a WSGI server.

        :param name: Pretty name for logging.
        :param app: The WSGI application to serve.
        :param host: IP address to serve the application.
        :param port: Port number to server the application.
        :param pool_size: Maximum number of eventlets to spawn concurrently.
        :returns: None

        """
        # Allow operators to customize http requests max header line size.
        eventlet.wsgi.MAX_HEADER_LINE = CONF.max_header_line
        self.client_socket_timeout = CONF.client_socket_timeout or None
        self.name = name
        self.app = app
        self._host = host or "0.0.0.0"
        self._port = port or 0
        self._server = None
        self._socket = None
        self._protocol = protocol
        self.pool_size = pool_size or self.default_pool_size
        self._pool = eventlet.GreenPool(self.pool_size)
        self._logger = logging.getLogger("soil.%s.wsgi.server" % self.name)
        self._use_ssl = use_ssl

        if backlog < 1:
            raise exception.InvalidInput(
                reason='The backlog must be more than 1')

        bind_addr = (host, port)
        # TODO(dims): eventlet's green dns/socket module does not actually
        # support IPv6 in getaddrinfo(). We need to get around this in the
        # future or monitor upstream for a fix
        try:
            info = socket.getaddrinfo(bind_addr[0],
                                      bind_addr[1],
                                      socket.AF_UNSPEC,
                                      socket.SOCK_STREAM)[0]
            family = info[0]
            bind_addr = info[-1]
        except Exception:
            family = socket.AF_INET

        try:
            self._socket = eventlet.listen(bind_addr, family, backlog=backlog)
        except EnvironmentError:
            LOG.error(_LE("Could not bind to %(host)s:%(port)s"),
                      {'host': host, 'port': port})
            raise

        (self._host, self._port) = self._socket.getsockname()[0:2]
        LOG.info(_LI("%(name)s listening on %(_host)s:%(_port)s"),
                 {'name': self.name, '_host': self._host, '_port': self._port})

    def start(self):
        """Start serving a WSGI application.

        :returns: None
        :raises: soil.exception.InvalidInput

        """
        # The server socket object will be closed after server exits,
        # but the underlying file descriptor will remain open, and will
        # give bad file descriptor error. So duplicating the socket object,
        # to keep file descriptor usable.

        dup_socket = self._socket.dup()
        dup_socket.setsockopt(socket.SOL_SOCKET,
                              socket.SO_REUSEADDR, 1)
        # sockets can hang around forever without keepalive
        dup_socket.setsockopt(socket.SOL_SOCKET,
                              socket.SO_KEEPALIVE, 1)

        # This option isn't available in the OS X version of eventlet
        if hasattr(socket, 'TCP_KEEPIDLE'):
            dup_socket.setsockopt(socket.IPPROTO_TCP,
                                  socket.TCP_KEEPIDLE,
                                  CONF.tcp_keepidle)

        if self._use_ssl:
            try:
                ca_file = CONF.ssl_ca_file
                cert_file = CONF.ssl_cert_file
                key_file = CONF.ssl_key_file

                if cert_file and not os.path.exists(cert_file):
                    raise RuntimeError(
                        _("Unable to find cert_file : %s") % cert_file)

                if ca_file and not os.path.exists(ca_file):
                    raise RuntimeError(
                        _("Unable to find ca_file : %s") % ca_file)

                if key_file and not os.path.exists(key_file):
                    raise RuntimeError(
                        _("Unable to find key_file : %s") % key_file)

                if self._use_ssl and (not cert_file or not key_file):
                    raise RuntimeError(
                        _("When running server in SSL mode, you must "
                          "specify both a cert_file and key_file "
                          "option value in your configuration file"))
                ssl_kwargs = {
                    'server_side': True,
                    'certfile': cert_file,
                    'keyfile': key_file,
                    'cert_reqs': ssl.CERT_NONE,
                }

                if CONF.ssl_ca_file:
                    ssl_kwargs['ca_certs'] = ca_file
                    ssl_kwargs['cert_reqs'] = ssl.CERT_REQUIRED

                dup_socket = eventlet.wrap_ssl(dup_socket,
                                               **ssl_kwargs)
            except Exception:
                with excutils.save_and_reraise_exception():
                    LOG.error(("Failed to start %(name)s on %(host)s"
                               ":%(port)s with SSL support"),
                              {'name': self.name, 'host': self.host,
                               'port': self.port})

        wsgi_kwargs = {
            'func': eventlet.wsgi.server,
            'sock': dup_socket,
            'site': self.app,
            'protocol': self._protocol,
            'custom_pool': self._pool,
            'log': self._logger,
            'debug': False,
            'keepalive': CONF.wsgi_keep_alive,
            'socket_timeout': self.client_socket_timeout
        }

        self._server = eventlet.spawn(**wsgi_kwargs)

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    def stop(self):
        """Stop this server.

        This is not a very nice action, as currently the method by which a
        server is stopped is by killing its eventlet.

        :returns: None

        """
        LOG.info("Stopping WSGI server.")
        if self._server is not None:
            # Resize pool to stop new requests from being processed
            self._pool.resize(0)
            self._server.kill()

    def wait(self):
        """Block, until the server has stopped.

        Waits on the server's eventlet to finish, then returns.

        :returns: None

        """
        try:
            if self._server is not None:
                self._pool.waitall()
                self._server.wait()
        except greenlet.GreenletExit:
            LOG.info("WSGI server has stopped.")

    def reset(self):
        """Reset server greenpool size to default.

        :returns: None

        """
        self._pool.resize(self.pool_size)
