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

"""
SQLAlchemy models for cerberus data.
"""

from sqlalchemy import Boolean, Column, String, Integer, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base

from oslo.config import cfg

from cerberus.common import serialize
from cerberus.openstack.common.db.sqlalchemy import models


CONF = cfg.CONF
BASE = declarative_base()


class CerberusBase(models.SoftDeleteMixin,
                   models.TimestampMixin,
                   models.ModelBase):

    metadata = None

    def save(self, session=None):
        from cerberus.db.sqlalchemy import api

        if session is None:
            session = api.get_session()

        super(CerberusBase, self).save(session=session)


class PluginInfo(BASE, CerberusBase):
    """Plugin info"""

    __tablename__ = 'plugin_info'
    __table_args__ = ()

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255))
    name = Column(String(255))
    version = Column(String(255))
    provider = Column(String(255))
    type = Column(String(255))
    description = Column(String(255))
    tool_name = Column(String(255))


class PluginInfoJsonSerializer(serialize.JsonSerializer):
    """Plugin info serializer"""

    __attributes__ = ['id', 'uuid', 'name', 'version', 'provider',
                      'type', 'description', 'tool_name']
    __required__ = ['id']
    __attribute_serializer__ = dict(created_at='date', deleted_at='date',
                                    acknowledged_at='date')
    __object_class__ = PluginInfo


class SecurityReport(BASE, CerberusBase):
    """Security Report"""

    __tablename__ = 'security_report'
    __table_args__ = ()

    id = Column(Integer, primary_key=True)
    plugin_id = Column(String(255))
    report_id = Column(String(255), unique=True)
    component_id = Column(String(255))
    component_type = Column(String(255))
    component_name = Column(String(255))
    project_id = Column(String(255))
    title = Column(String(255))
    description = Column(String(255))
    security_rating = Column(Float)
    vulnerabilities = Column(Text)
    vulnerabilities_number = Column(Integer)
    last_report_date = Column(DateTime)
    ticket_id = Column(String(255))


class SecurityReportJsonSerializer(serialize.JsonSerializer):
    """Security report serializer"""

    __attributes__ = ['id', 'title', 'description', 'plugin_id', 'report_id',
                      'component_id', 'component_type', 'component_name',
                      'project_id', 'security_rating', 'vulnerabilities',
                      'vulnerabilities_number', 'last_report_date',
                      'ticket_id', 'deleted', 'created_at', 'deleted_at',
                      'updated_at']
    __required__ = ['id', 'title', 'component_id']
    __attribute_serializer__ = dict(created_at='date', deleted_at='date',
                                    acknowledged_at='date')
    __object_class__ = SecurityReport


class SecurityAlarm(BASE, CerberusBase):
    """Security alarm coming from Security Information and Event Manager
     for example
     """

    __tablename__ = 'security_alarm'
    __table_args__ = ()

    id = Column(Integer, primary_key=True)
    plugin_id = Column(String(255))
    alarm_id = Column(String(255), unique=True)
    timestamp = Column(DateTime)
    status = Column(String(255))
    severity = Column(String(255))
    project_id = Column(String(255))
    component_id = Column(String(255))
    summary = Column(String(255))
    description = Column(String(255))
    ticket_id = Column(String(255))


class SecurityAlarmJsonSerializer(serialize.JsonSerializer):
    """Security report serializer"""

    __attributes__ = ['id', 'plugin_id', 'alarm_id', 'timestamp', 'status',
                      'severity', 'project_id', 'component_id', 'summary',
                      'description', 'ticket_id', 'deleted', 'created_at',
                      'deleted_at', 'updated_at']
    __required__ = ['id', 'title']
    __attribute_serializer__ = dict(created_at='date', deleted_at='date',
                                    acknowledged_at='date')
    __object_class__ = SecurityAlarm


class Task(BASE, CerberusBase):
    """Tasks for security purposes (e.g: daily scans...)
    """
    __tablename__ = 'task'
    __table_args__ = ()

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    method = Column(String(255))
    type = Column(String(255))
    period = Column(Integer)
    plugin_id = Column(String(255))
    running = Column(Boolean)
    uuid = Column(String(255))


class TaskJsonSerializer(serialize.JsonSerializer):
    """Security report serializer"""

    __attributes__ = ['id', 'name', 'method', 'type', 'period',
                      'plugin_id', 'running', 'uuid', 'deleted', 'created_at',
                      'deleted_at', 'updated_at']
    __required__ = ['id', ]
    __attribute_serializer__ = dict(created_at='date', deleted_at='date',
                                    acknowledged_at='date')
    __object_class__ = Task
