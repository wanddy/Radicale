# This file is part of Radicale Server - Calendar Server
# Copyright © 2008 Nicolas Kandel
# Copyright © 2008 Pascal Halter
# Copyright © 2008-2017 Guillaume Ayoub
# Copyright © 2017-2018 Unrud <unrud@outlook.com>
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Radicale.  If not, see <http://www.gnu.org/licenses/>.

"""
Authentication module.

Authentication is based on usernames and passwords. If something more
advanced is needed an external WSGI server or reverse proxy can be used
(see ``remote_user`` or ``http_x_remote_user`` backend).

Take a look at the class ``BaseAuth`` if you want to implement your own.

"""

from importlib import import_module

from radicale.log import logger

INTERNAL_TYPES = ("none", "remote_user", "http_x_remote_user", "htpasswd")


def load(configuration):
    """Load the authentication manager chosen in configuration."""
    auth_type = configuration.get("auth", "type")
    if auth_type in INTERNAL_TYPES:
        module = "radicale.auth.%s" % auth_type
    else:
        module = auth_type
    try:
        class_ = import_module(module).Auth
    except Exception as e:
        raise RuntimeError("Failed to load authentication module %r: %s" %
                           (module, e)) from e
    logger.info("Authentication type is %r", auth_type)
    return class_(configuration)


class BaseAuth:
    def __init__(self, configuration):
        self.configuration = configuration

    def get_external_login(self, environ):
        """Optionally provide the login and password externally.

        ``environ`` a dict with the WSGI environment

        If ``()`` is returned, Radicale handles HTTP authentication.
        Otherwise, returns a tuple ``(login, password)``. For anonymous users
        ``login`` must be ``""``.

        """
        return ()

    def login(self, login, password):
        """Check credentials and map login to internal user

        ``login`` the login name

        ``password`` the password

        Returns the user name or ``""`` for invalid credentials.

        """

        raise NotImplementedError
