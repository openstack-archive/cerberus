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

import datetime
import json

from cerberus.common import exception as cerberus_exception
from cerberus.common import json_encoders
from cerberus.db import api as db_api
from cerberus.openstack.common import log
from cerberus.plugins import base


LOG = log.getLogger(__name__)


class TestPlugin(base.PluginBase):

    def __init__(self):
        self.task_id = None
        super(TestPlugin, self).__init__()
        super(TestPlugin, self).subscribe_event('image.update')

    def act_short(self, *args, **kwargs):
        LOG.info(str(kwargs.get('task_name', 'unknown')) + " :"
                 + str(datetime.datetime.time(datetime.datetime.now())))

    @base.PluginBase.webmethod
    def get_security_reports(self, **kwargs):
        security_reports = []
        try:
            security_report = {
                'vulns': {'443': {'ip': '192.168.100.3', 'archived': False,
                                  'protocol': 'tcp', 'iface_id': 329,
                                  'family': 'Web Servers',
                                  'plugin': '1.3.6.1.4.1.25623.1.0.10386',
                                  'service_name': 'Apache httpd 2.2.22',
                                  'vuln_state': 'acked', 'port': 80,
                                  'state': 'acked', 'service': '80/tcp',
                                  'service_status': None, 'host_id': 328,
                                  'vuln_id': 443,
                                  'output': "Summary: \nRemote web server does not reply with 404 error code.\n\nInsight: \nThis web server is [mis]configured in that it does not return\n '404 Not Found' error codes when a non-existent file is requested,\n perhaps returning a site map, search page or authentication page\n instead.\n \n OpenVAS enabled some counter measures for that, however they might\n be insufficient. If a great number of security holes are produced\n for this port, they might not all be accurate\n\nReferences: \nNOXREF\nCVE:NOCVE\n\n",  # noqa
                                  'service_id': 337, 'score': 0.0, 'id': 443,
                                  'name': 'No 404 check'},
                          '447': {'ip': '192.168.100.3', 'archived': False,
                                  'protocol': 'tcp', 'iface_id': 329,
                                  'family': 'Denial of Service',
                                  'plugin': '1.3.6.1.4.1.25623.1.0.121035',
                                  'service_name': 'OpenSSH 5.9p1 Debian',
                                  'vuln_state': 'acked', 'port': 22,
                                  'state': 'acked', 'service': '22/tcp',
                                  'service_status': None, 'host_id': 328,
                                  'vuln_id': 447,
                                  'output': "Summary: \nDenial of Service Vulnerability in OpenSSH\n\nInsight: \nThe sshd_config configuration file indicates connection limits:\n - MaxStartups: maximal number of unauthenticated connections (default : 10)\n - LoginGraceTime: expiration duration of unauthenticated connections (default : 2 minutes)\n\nHowever, in this default configuration, an attacker can open 10 TCP sessions on port 22/tcp, and then reopen them every 2 minutes, in order to limit the probability of a legitimate client to access to the service.\n\nNote: MaxStartups supports the 'random early drop' feature, which protects against this type of attack, but it is not enabled by default.\n\nAn unauthenticated attacker can therefore open ten connections to OpenSSH, in order to forbid the access to legitimate users.\n\nThis plugin only check OpenSSH version and not test to exploit this vulnerability.\n\nImpact: \nAttackers to cause a denial of service (connection-slot exhaustion).\n\nReferences: \nURL:http://www.openbsd.org/cgi-bin/cvsweb/src/usr.bin/ssh/sshd_config?r1=1.89#rev1.89\nURL:http://www.openbsd.org/cgi-bin/cvsweb/src/usr.bin/ssh/sshd_config.5?r1=1.156#rev1.156\nURL:http://www.openbsd.org/cgi-bin/cvsweb/src/usr.bin/ssh/servconf.c?r1=1.234#rev1.234\nURL:http://vigilance.fr/vulnerability/OpenSSH-denial-of-service-via-MaxStartups-11256\nCVE:CVE-2010-5107\n\nSolution: \nUpgrade your OpenSSH to 6.2. or modify LoginGraceTime and MaxStartups on server configuration\n\n",  # noqa
                                  'service_id': 333, 'score': 5.0, 'id': 447,
                                  'name': 'Denial of Service in OpenSSH'},
                          '446': {'ip': '192.168.100.3', 'archived': False,
                                  'protocol': 'udp', 'iface_id': 329,
                                  'family': 'Service detection',
                                  'plugin': '1.3.6.1.4.1.25623.1.0.10884',
                                  'service_name': 'NTP v4 (unsynchronized)',
                                  'vuln_state': 'new', 'port': 123,
                                  'state': 'new', 'service': '123/udp',
                                  'service_status': None, 'host_id': 328,
                                  'vuln_id': 446,
                                  'output': 'Summary: \nA NTP (Network Time Protocol) server is listening on this port.\n\nReferences: \nNOXREF\nCVE:NOCVE\n\n',  # noqa
                                  'service_id': 335, 'score': 0.0, 'id': 446,
                                  'name': 'NTP read variables'},
                          '445': {'ip': '192.168.100.3', 'archived': False,
                                  'protocol': 'tcp', 'iface_id': 329,
                                  'family': 'General',
                                  'plugin': '1.3.6.1.4.1.25623.1.0.120008',
                                  'service_name': 'Apache httpd 2.2.22 ',
                                  'vuln_state': 'acked', 'port': 443,
                                  'state': 'acked', 'service': '443/tcp',
                                  'service_status': None, 'host_id': 328,
                                  'vuln_id': 445,
                                  'output': '\nFollowing is a list of the SSL cipher suites supported when connecting to the host.\n\nSupported cipher suites (ORDER IS NOT SIGNIFICANT)\n  SSLv3\n     RSA_WITH_3DES_EDE_CBC_SHA\n     DHE_RSA_WITH_3DES_EDE_CBC_SHA\n     RSA_WITH_AES_128_CBC_SHA\n     DHE_RSA_WITH_AES_128_CBC_SHA\n     RSA_WITH_AES_256_CBC_SHA\n     DHE_RSA_WITH_AES_256_CBC_SHA\n     RSA_WITH_CAMELLIA_128_CBC_SHA\n     DHE_RSA_WITH_CAMELLIA_128_CBC_SHA\n     RSA_WITH_CAMELLIA_256_CBC_SHA\n     DHE_RSA_WITH_CAMELLIA_256_CBC_SHA\n  (TLSv1.0: idem)\n  (TLSv1.1: idem)\n  TLSv1.2\n     RSA_WITH_3DES_EDE_CBC_SHA\n     DHE_RSA_WITH_3DES_EDE_CBC_SHA\n     RSA_WITH_AES_128_CBC_SHA\n     DHE_RSA_WITH_AES_128_CBC_SHA\n     RSA_WITH_AES_256_CBC_SHA\n     DHE_RSA_WITH_AES_256_CBC_SHA\n     RSA_WITH_AES_128_CBC_SHA256\n     RSA_WITH_AES_256_CBC_SHA256\n     RSA_WITH_CAMELLIA_128_CBC_SHA\n     DHE_RSA_WITH_CAMELLIA_128_CBC_SHA\n     DHE_RSA_WITH_AES_128_CBC_SHA256\n     DHE_RSA_WITH_AES_256_CBC_SHA256\n     RSA_WITH_CAMELLIA_256_CBC_SHA\n     DHE_RSA_WITH_CAMELLIA_256_CBC_SHA\n\n',  # noqa
                                  'service_id': 339, 'score': 0.0, 'id': 445,
                                  'name': 'SSL Cipher Suites Supported'},
                          '444': {'ip': '192.168.100.3', 'archived': False,
                                  'protocol': 'tcp', 'iface_id': 329,
                                  'family': 'General',
                                  'plugin': '1.3.6.1.4.1.25623.1.0.120002',
                                  'service_name': 'Apache httpd 2.2.22',
                                  'vuln_state': 'acked', 'port': 443,
                                  'state': 'acked', 'service': '443/tcp',
                                  'service_status': None, 'host_id': 328,
                                  'vuln_id': 444,
                                  'output': '\nA vulnerability exists in SSL 3.0 and TLS 1.0 that could allow information \ndisclosure if an attacker intercepts encrypted traffic served from an affected \nsystem. It is also known as BEAST attack.  \n\nCVSS Severity:\n    CVSS Base Score: 4.3 (AV:N/AC:M/Au:N/C:P/I:N/A:N) \n    Impact Subscore: \n    Exploitability Subscore:\n\nReference:\n    CVE-2011-3389\n \nSolution:\n    Disable usage of CBC ciphers with SSL 3.0 and TLS 1.0 protocols.\n \nNote: \n    This script detects the vulnerability in the SSLv3/TLSv1 protocol implemented \n    in the server. It does not detect the BEAST attack where it exploits the \n    vulnerability at HTTPS client-side.\n\n    The detection at server-side does not necessarily mean your server is \n    vulnerableto the BEAST attack because the attack exploits the vulnerability \n    at client-side, and both SSL/TLS clients and servers can independently employ \n    the split record countermeasure.\n \nSee Also:\n    http://vnhacker.blogspot.com/2011/09/beast.html\n    http://www.openssl.org/~bodo/tls-cbc.txt\n    http://blogs.msdn.com/b/kaushal/archive/2012/01/21/fixing-the-beast.aspx\n \n \n',  # noqa
                                  'service_id': 339, 'score': 4.3, 'id': 444,
                                  'name': 'BEAST Vulnerability'}},
                'host': {'archived': False, 'name': '192.168.100.3',
                         'ifaces': [329], 'scan': True,
                         'cpe': 'cpe:/o:canonical:ubuntu_linux', 'state': 'up',
                         'cpe_title': 'Canonical Ubuntu Linux',
                         'fingerprint': 'Linux Kernel', 'device': 'server',
                         'id': 328},
                'stat': {'ignored': 0, 'entity_id': 328, 'medium': 2,
                         'grade': 7.4, 'vulns': 2, 'archived': 0,
                         'not_scanned': 0, 'high': 0, 'score': 9.3, 'hosts': 1,
                         'trending': 0.0, 'scanned': 1, 'critical': 0,
                         'low': 0},
                'ifaces': {'329': {'archived': False, 'ip': '192.168.100.3',
                                   'state': 'up',
                                   'services': [333, 335, 337, 339],
                                   'host_id': 328, 'id': 329}}}

            report_id = 1
            if (security_report.get('stat'), False):
                vulnerabilities_number = security_report['stat']\
                    .get('vulns', None)
            try:
                db_api.security_report_create(
                    {'title': 'Security report',
                     'plugin_id': self._uuid,
                     'report_id': report_id,
                     'component_id': 'a1d869a1-6ab0-4f02-9e56-f83034bacfcb',
                     'component_type': 'instance',
                     'component_name': 'openstack-test-server',
                     'project_id': '510c7f4ed14243f09df371bba2561177',
                     'description': 'openstack-test-server',
                     'security_rating': security_report['stat']['grade'],
                     'vulnerabilities': json.dumps(
                         security_report['vulns'],
                         cls=json_encoders.DateTimeEncoder),
                     'vulnerabilities_number': vulnerabilities_number}
                )
            except cerberus_exception.DBException as e:
                LOG.exception(e)
                pass
            security_reports.append(security_report)
            db_report_id = db_api.security_report_get_from_report_id(
                report_id).id
            db_api.security_report_update_last_report_date(
                db_report_id, datetime.datetime(2015, 5, 6, 16, 19, 29))
        except Exception as e:
            LOG.exception(e)
            pass
        return security_reports

    def process_notification(self, ctxt, publisher_id, event_type, payload,
                             metadata):

        LOG.info('--> Plugin %(plugin)s managed event %(event)s'
                 'payload %(payload)s'
                 % {'plugin': self._name,
                    'event': event_type,
                    'payload': payload})
        if ('START' in payload['name']and self.task_id is None):
            self.task_id = self.manager.create_task(
                {},
                self._uuid,
                'act_short',
                task_type='recurrent',
                task_period=1,
                task_name='TEST_PLUGIN_START_PAYLOAD')
            LOG.info('Start cycling task id %s', self.task_id)

        if ('STOP' in payload['name']):
            try:
                self.manager._force_delete_recurrent_task(self.task_id)
                LOG.info('Stop cycling task id %s', self.task_id)
                self.task_id = None
            except StopIteration as e:
                LOG.debug('Error when stopping task')
                LOG.exception(e)
        return self._name
