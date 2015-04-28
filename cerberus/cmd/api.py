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

import sys

from oslo.config import cfg

from cerberus.api import app
from cerberus.common import config
from cerberus.openstack.common import log


CONF = cfg.CONF
CONF.import_opt('auth_strategy', 'cerberus.api')
LOG = log.getLogger(__name__)


def main():
    argv = sys.argv
    config.parse_args(argv)
    log.setup(cfg.CONF, 'cerberus')
    server = app.build_server()
    log.set_defaults(cfg.CONF.default_log_levels)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    LOG.info("cerberus-api starting...")

if __name__ == '__main__':
    main()
