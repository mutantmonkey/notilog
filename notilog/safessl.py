# Monkey patch amqp to properly verify hostname
#
# Copyright © 2014 mutantmonkey <mutantmonkey@mutantmonkey.in>
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import ssl
from amqp.transport import SSLTransport

def ssl_setup_transport(self):
    """Wrap the socket in an SSL object with sensible defaults and hostname
    checking."""
    if 'ca_certs' in self.sslopts:
        cafile = self.sslopts['ca_certs']
    else:
        cafile = None

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
                                         cafile=cafile)
    if hasattr(self, 'sslopts'):
        self.sock = context.wrap_socket(
            self.sock,
            server_hostname=self.sslopts['server_hostname'])
    else:
        context.check_hostname = False
        self.sock = context.wrap_socket(self.sock)
    self.sock.do_handshake()
    self._quick_recv = self.sock.read
SSLTransport._setup_transport = ssl_setup_transport
