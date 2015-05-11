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

from cerberus.api.v1.datamodels import base
from wsme import types as wtypes


class SecurityAlarmResource(base.Base):
    """ Representation of a security report.
    """

    id = wtypes.IntegerType()
    """Security report id."""

    plugin_id = wtypes.wsattr(wtypes.text)
    """Associated plugin id."""

    report_id = wtypes.wsattr(wtypes.text)
    """Associated report id."""

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
    """Associated report id."""

    vulnerabilities_number = wtypes.IntegerType()
    """Total of Vulnerabilities."""

    last_report_date = datetime.datetime
    """Last report date."""

    ticket_id = wtypes.wsattr(wtypes.text, mandatory=True)
    """Associated ticket id."""

    def as_dict(self):
        return self.as_dict_from_keys(
            ['id', 'plugin_id', 'report_id', 'component_id',
             'component_type', 'component_name', 'project_id',
             'title', 'description', 'security_rating',
             'vulnerabilities', 'vulnerabilities_number',
             'last_report_date', 'ticket_id']
        )

    def __init__(self, initial_data=None):
        super(SecurityAlarmResource, self).__init__()
        if initial_data is not None:
            for key in initial_data:
                setattr(self, key, initial_data[key])


class SecurityAlarmResourceCollection(base.Base):
    """A list of Security reports."""

    security_reports = [SecurityAlarmResource]
