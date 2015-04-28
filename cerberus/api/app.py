#
#   Copyright (c) 2014 EUROGICIEL
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
import pecan
from wsgiref import simple_server

from oslo.config import cfg

import auth
from cerberus.api import config as api_config
from cerberus.api import hooks
from cerberus.openstack.common import log as logging

LOG = logging.getLogger(__name__)

auth_opts = [
    cfg.StrOpt('api_paste_config',
               default="api_paste.ini",
               help="Configuration file for WSGI definition of API."
               ),
]

api_opts = [
    cfg.StrOpt('host_ip',
               default="0.0.0.0",
               help="Host serving the API."
               ),
    cfg.IntOpt('port',
               default=8300,
               help="Host port serving the API."
               ),
]

CONF = cfg.CONF
CONF.register_opts(auth_opts)
CONF.register_opts(api_opts, group='api')


def get_pecan_config():
    # Set up the pecan configuration
    filename = api_config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)


def setup_app(pecan_config=None, extra_hooks=None):

    if not pecan_config:
        pecan_config = get_pecan_config()

    app_hooks = [hooks.ConfigHook(),
                 hooks.DBHook(),
                 hooks.ContextHook(pecan_config.app.acl_public_routes),
                 hooks.NoExceptionTracebackHook()]

    if pecan_config.app.enable_acl:
        app_hooks.append(hooks.AuthorizationHook(
            pecan_config.app.member_routes))

    pecan.configuration.set_config(dict(pecan_config), overwrite=True)

    app = pecan.make_app(
        pecan_config.app.root,
        static_root=pecan_config.app.static_root,
        template_path=pecan_config.app.template_path,
        debug=CONF.debug,
        force_canonical=getattr(pecan_config.app, 'force_canonical', True),
        hooks=app_hooks,
        guess_content_type_from_ext=False
    )

    if pecan_config.app.enable_acl:
        strategy = auth.strategy(CONF.auth_strategy)
        return strategy.install(app,
                                cfg.CONF,
                                pecan_config.app.acl_public_routes)

    return app


def build_server():
    # Create the WSGI server and start it
    host = CONF.api.host_ip
    port = CONF.api.port

    server_cls = simple_server.WSGIServer
    handler_cls = simple_server.WSGIRequestHandler

    pecan_config = get_pecan_config()
    pecan_config.app.enable_acl = (CONF.auth_strategy == 'keystone')

    app = setup_app(pecan_config=pecan_config)

    srv = simple_server.make_server(
        host,
        port,
        app,
        server_cls,
        handler_cls)

    return srv
