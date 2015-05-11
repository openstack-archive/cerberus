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

from cerberus.common import config
from cerberus import manager
from cerberus.openstack.common import log
from cerberus.openstack.common import service

LOG = log.getLogger(__name__)


def main():

    log.set_defaults(cfg.CONF.default_log_levels)
    argv = sys.argv
    config.parse_args(argv)
    log.setup(cfg.CONF, 'cerberus')
    launcher = service.ProcessLauncher()
    c_manager = manager.CerberusManager()
    launcher.launch_service(c_manager)
    launcher.wait()


if __name__ == '__main__':
    main()
