#
# Copyright (c) 2015 EUROGICIEL
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
import uuid

from cerberus.api.v1.datamodels import base
from wsme import types as wtypes


class SecurityReportResource(base.Base):
    """ Representation of a security report.
    """

    uuid = wtypes.wsattr(wtypes.text)
    """Security report id."""

    plugin_id = wtypes.wsattr(wtypes.text)
    """Associated plugin id."""

    report_id = wtypes.wsattr(wtypes.text)
    """Associated report id provided by plugin."""

    component_id = wtypes.wsattr(wtypes.text)
    """Associated component id."""

    component_type = wtypes.wsattr(wtypes.text)
    """Component type."""

    component_name = wtypes.wsattr(wtypes.text)
    """Component name."""

    project_id = wtypes.wsattr(wtypes.text)
    """Associated project id."""

    title = wtypes.wsattr(wtypes.text)
    """Title of report."""

    description = wtypes.wsattr(wtypes.text)
    """Description."""

    security_rating = float
    """Security rating."""

    vulnerabilities = wtypes.wsattr(wtypes.text)
    """Vulnerabilities."""

    vulnerabilities_number = wtypes.IntegerType()
    """Total of Vulnerabilities."""

    last_report_date = datetime.datetime
    """Last report date."""

    ticket_id = wtypes.wsattr(wtypes.text, mandatory=True)
    """Associated ticket id."""

    def as_dict(self):
        return self.as_dict_from_keys(
            ['uuid', 'plugin_id', 'report_id', 'component_id',
             'component_type', 'component_name', 'project_id',
             'title', 'description', 'security_rating',
             'vulnerabilities', 'vulnerabilities_number',
             'last_report_date', 'ticket_id']
        )

    def __init__(self, initial_data=None):
        super(SecurityReportResource, self).__init__()
        if initial_data is not None:
            for key in initial_data:
                setattr(self, key, initial_data[key])

    @classmethod
    def sample(cls):
        sample = cls(initial_data={
            'uuid': uuid.uuid4(),
            'security_rating': float(7.4),
            'component_name': 'openstack-server',
            'component_id': 'a1d869a1-6ab0-4f02-9e56-f83034bacfcb',
            'component_type': 'instance',
            'vulnerabilities_number': '2',
            'description': 'security report',
            'title': 'Security report',
            'last_report_date': datetime.datetime(2015, 5, 6, 16, 19, 29),
            'project_id': '510c7f4ed14243f09df371bba2561177',
            'plugin_id': '063d4206-5afc-409c-a4d1-c2a469299d37',
            'report_id': 'fea4b170-ed46-4a50-8b91-ed1c6876be7d',
            'vulnerabilities': '{"443": {"archived": "false", '
                               '"protocol": "tcp", "family": "Web Servers", '
                               '"iface_id": 329, '
                               '"plugin": "1.3.6.1.4.1.25623.1.0.10386",'
                               '"ip": "192.168.100.3", "id": 443,'
                               '"output": "Summary": "Remote web server does'
                               ' not reply with 404 error code"}}'})
        return sample


class SecurityReportResourceCollection(base.Base):
    """A list of Security reports."""

    security_reports = [SecurityReportResource]
