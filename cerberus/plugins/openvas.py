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

from cerberus.client import keystone_client
from cerberus.client import neutron_client
from cerberus.client import nova_client
from cerberus.openstack.common import log
from cerberus.plugins import base
import openvas_lib


LOG = log.getLogger(__name__)


# Register options for the service
OPENVAS_OPTS = [
    cfg.StrOpt('openvas_admin',
               default='admin',
               help='The admin user for rcp server',
               ),
    cfg.StrOpt('openvas_passwd',
               default='admin',
               help='The password for rcp server',
               ),
    cfg.StrOpt('openvas_url',
               default='https://',
               help='Url of rcp server',
               ),
]

opt_group = cfg.OptGroup(name='openvas',
                         title='Options for the OpenVas client')

cfg.CONF.register_group(opt_group)
cfg.CONF.register_opts(OPENVAS_OPTS, opt_group)
cfg.CONF.import_group('openvas', 'cerberus.service')

_FLOATINGIP_UPDATED = 'floatingip.update.end'
_ROLE_ASSIGNMENT_CREATED = 'identity.created.role_assignment'
_ROLE_ASSIGNMENT_DELETED = 'identity.deleted.role_assignment'
_PROJECT_DELETED = 'identity.project.deleted'


class OpenVasPlugin(base.PluginBase):

    def __init__(self):
        self.task_id = None
        super(OpenVasPlugin, self).__init__()
        self.subscribe_event(_ROLE_ASSIGNMENT_CREATED)
        self.subscribe_event(_ROLE_ASSIGNMENT_DELETED)
        self.subscribe_event(_FLOATINGIP_UPDATED)
        self.subscribe_event(_PROJECT_DELETED)
        self.kc = keystone_client.Client()
        self.nc = neutron_client.Client()
        self.nova_client = nova_client.Client()
        self.conf = cfg.CONF.openvas

    @base.PluginBase.webmethod
    def get_security_reports(self, **kwargs):
        security_reports = []
        try:
            scanner = openvas_lib.VulnscanManager(self.conf.openvas_url,
                                                  self.conf.openvas_admin,
                                                  self.conf.openvas_passwd)
            finished_scans = scanner.get_finished_scans
            for scan_key, scan_id in finished_scans.iteritems():
                report_id = scanner.get_report_id(scan_id)
                report = scanner.get_report_html(report_id)

                security_reports.append(report)

        except Exception as e:
            LOG.exception(e)
            pass
        return security_reports

    def process_notification(self, ctxt, publisher_id, event_type, payload,
                             metadata):
        pass
