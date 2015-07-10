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

from oslo.config import cfg

from cerberus.openstack.common.gettextutils import _  # noqa

keystone_opts = [
    cfg.StrOpt('auth_strategy', default='keystone',
               help=_('The strategy to use for authentication.'))
]

OPTS = [
    cfg.StrOpt('timeout',
               default=20,
               help='The timeout to use if agents do not reply to asynchronous'
                    ' requests made by the api')
]

CONF = cfg.CONF
CONF.register_opts(keystone_opts)
CONF.register_opts(OPTS, group='api_opts')
