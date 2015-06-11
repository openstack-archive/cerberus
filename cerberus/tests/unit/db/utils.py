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

from cerberus.common import loopingcall
from cerberus.db.sqlalchemy import models


def fake_function():
    pass


def get_test_security_report(**kwargs):
    return {
        'uuid': kwargs.get('uuid', 1),
        'plugin_id': kwargs.get('plugin_id',
                                '228df8e8-d5f4-4eb9-a547-dfc649dd1017'),
        'report_id': kwargs.get('report_id', '1234'),
        'component_id': kwargs.get('component_id',
                                   '422zb9d5-c5g3-8wy9-a547-hhc885dd8548'),
        'component_type': kwargs.get('component_type', 'instance'),
        'component_name': kwargs.get('component_name', 'instance-test'),
        'project_id': kwargs.get('project_id',
                                 '28c6f9e6add24c29a589a9967432fede'),
        'title': kwargs.get('title', 'test-security-report'),
        'description': kwargs.get('description',
                                  'no fear, this is just a test'),
        'security_rating': kwargs.get('security_rating', 5.1),
        'vulnerabilities': kwargs.get('vulnerabilities', 'vulns'),
        'vulnerabilities_number': kwargs.get('vulnerabilities_number', 1),
        'last_report_date': kwargs.get('last_report_date',
                                       '2015-01-01T00:00:00')
    }


def get_security_report_model(**kwargs):
    security_report = models.SecurityReport()
    security_report.uuid = kwargs.get('uuid', 1)
    security_report.plugin_id = kwargs.get(
        'plugin_id',
        '228df8e8-d5f4-4eb9-a547-dfc649dd1017'
    )
    security_report.report_id = kwargs.get('report_id', '1234')
    security_report.component_id = kwargs.get(
        'component_id',
        '422zb9d5-c5g3-8wy9-a547-hhc885dd8548')
    security_report.component_type = kwargs.get('component_type', 'instance')
    security_report.component_name = kwargs.get('component_name',
                                                'instance-test')
    security_report.project_id = kwargs.get('project_id',
                                            '28c6f9e6add24c29a589a9967432fede')
    security_report.title = kwargs.get('title', 'test-security-report')
    security_report.description = kwargs.get('description',
                                             'no fear, this is just a test')
    security_report.security_rating = kwargs.get('security_rating',
                                                 float('5.1'))
    security_report.vulnerabilities = kwargs.get('vulnerabilities', 'vulns')
    security_report.vulnerabilities_number = kwargs.get(
        'vulnerabilities_number', 1)
    security_report.last_report_date = kwargs.get(
        'last_report_date',
        datetime.datetime(2015, 1, 1)
    )
    return security_report


def get_test_plugin(**kwargs):
    return {
        'id': kwargs.get('id', 1),
        'provider': kwargs.get('provider', 'provider'),
        'tool_name': kwargs.get('tool_name', 'toolbox'),
        'type': kwargs.get('type', 'tool_whatever'),
        'description': kwargs.get('description', 'This is a tool'),
        'uuid': kwargs.get('uuid', '490cc562-9e60-46a7-9b5f-c7619aca2e07'),
        'version': kwargs.get('version', '0.1a'),
        'name': kwargs.get('name', 'tooly'),
        'subscribed_events': kwargs.get('subscribed_events',
                                        ["compute.instance.updated"]),
        'methods': kwargs.get('methods', [])
    }


def get_plugin_model(**kwargs):
    plugin = models.PluginInfo()
    plugin.id = kwargs.get('id', 1)
    plugin.provider = kwargs.get('provider', 'provider')
    plugin.tool_name = kwargs.get('tool_name', 'toolbox')
    plugin.type = kwargs.get('type', 'tool_whatever')
    plugin.description = kwargs.get('description', 'This is a tool')
    plugin.uuid = kwargs.get('uuid', '490cc562-9e60-46a7-9b5f-c7619aca2e07')
    plugin.version = kwargs.get('version', '0.1a')
    plugin.name = kwargs.get('name', 'tooly')
    return plugin


def get_rpc_plugin(**kwargs):
    return {
        'name': kwargs.get('name', 'tooly'),
        'subscribed_events': kwargs.get('subscribed_events',
                                        ["compute.instance.updated"]),
        'methods': kwargs.get('methods', [])
    }


def get_test_task(**kwargs):
    return {
        'id': kwargs.get('task_id', 1),
        'type': kwargs.get('task_type', 'unique'),
        'name': kwargs.get('task_name', 'No Name'),
        'period': kwargs.get('task_period', ''),
        'persistent': False,
    }


def get_recurrent_task_object(**kwargs):
    return(loopingcall.CerberusFixedIntervalLoopingCall(fake_function,
                                                        **kwargs))


def get_recurrent_task_model(**kwargs):
    task = models.Task()
    task.id = kwargs.get('id', 1)
    task.name = kwargs.get('name', 'this_task')
    task.method = kwargs.get('method', 'method')
    task.type = kwargs.get('type', 'recurrent')
    task.period = kwargs.get('period', 10)
    task.plugin_id = kwargs.get('plugin_id',
                                '490cc562-9e60-46a7-9b5f-c7619aca2e07')
    task.uuid = kwargs.get('uuid', '500cc562-5c50-89t4-5fc8-c7619aca3n29')


def get_test_security_alarm(**kwargs):
    return {
        'id': kwargs.get('id', 1),
        'plugin_id': kwargs.get('plugin_id',
                                '228df8e8-d5f4-4eb9-a547-dfc649dd1017'),
        'alarm_id': kwargs.get('alarm_id', '1234'),
        'timestamp': kwargs.get('timestamp', '2015-01-01T00:00:00'),
        'status': kwargs.get('status', 'new'),
        'severity': kwargs.get('severity', 'CRITICAL'),
        'component_id': kwargs.get('component_id',
                                   '422zb9d5-c5g3-8wy9-a547-hhc885dd8548'),
        'summary': kwargs.get('summary', 'test-security-alarm'),
        'description': kwargs.get('description',
                                  'no fear, this is just a test')

    }


def get_security_alarm_model(**kwargs):
    security_alarm = models.SecurityAlarm()
    security_alarm.id = kwargs.get('id', 1)
    security_alarm.plugin_id = kwargs.get(
        'plugin_id',
        '228df8e8-d5f4-4eb9-a547-dfc649dd1017'
    )
    security_alarm.alarm_id = kwargs.get('alarm_id', '1234')
    security_alarm.timestamp = kwargs.get(
        'timestamp',
        datetime.datetime(2015, 1, 1)
    )
    security_alarm.status = kwargs.get('status', 'new')
    security_alarm.severity = kwargs.get('severity', 'CRITICAL')
    security_alarm.component_id = kwargs.get(
        'component_id',
        '422zb9d5-c5g3-8wy9-a547-hhc885dd8548')
    security_alarm.summary = kwargs.get('summary', 'test-security-alarm')
    security_alarm.description = kwargs.get('description',
                                            'no fear, this is just a test')
    return security_alarm
