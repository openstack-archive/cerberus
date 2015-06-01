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

from cerberus.openstack.common.db import api as db_api


CONF = cfg.CONF
CONF.import_opt('backend', 'cerberus.openstack.common.db.options',
                group='database')
_BACKEND_MAPPING = {'sqlalchemy': 'cerberus.db.sqlalchemy.api'}

IMPL = db_api.DBAPI(CONF.database.backend, backend_mapping=_BACKEND_MAPPING,
                    lazy=True)
''' JUNO:
IMPL = db_api.DBAPI.from_config(cfg.CONF,
                                backend_mapping=_BACKEND_MAPPING,
                                lazy=True)
'''


def get_instance():
    """Return a DB API instance."""
    return IMPL


def get_engine():
    return IMPL.get_engine()


def get_session():
    return IMPL.get_session()


def db_sync(engine, version=None):
    """Migrate the database to `version` or the most recent version."""
    return IMPL.db_sync(engine, version=version)


def security_report_create(values):
    """Create an instance from the values dictionary."""
    return IMPL.security_report_create(values)


def security_report_update_last_report_date(id, date):
    """Create an instance from the values dictionary."""
    return IMPL.security_report_update_last_report_date(id, date)


def security_report_update_ticket_id(id, ticket_id):
    """Create an instance from the values dictionary."""
    return IMPL.security_report_update_ticket_id(id, ticket_id)


def security_report_get_all(project_id=None):
    """Get all security reports"""
    return IMPL.security_report_get_all(project_id=project_id)


def security_report_get(id):
    """Get security report from its id in database"""
    return IMPL.security_report_get(id)


def security_report_get_from_report_id(report_id):
    """Get security report from its report identifier"""
    return IMPL.security_report_get_from_report_id(report_id)


def security_report_delete(report_id):
    """Delete security report from its report identifier"""
    return IMPL.security_report_delete(report_id)


def plugins_info_get():
    """Get information about plugins stored in db"""
    return IMPL.plugins_info_get()


def plugin_info_get_from_uuid(id):
    """
    Get information about plugin stored in db
    :param id: the uuid of the plugin
    """
    return IMPL.plugin_info_get_from_uuid(id)


def plugin_version_update(id, version):
    return IMPL.plugin_version_update(id, version)


def security_alarm_create(values):
    return IMPL.security_alarm_create(values)


def security_alarm_get_all():
    return IMPL.security_alarm_get_all()


def security_alarm_get(id):
    return IMPL.security_alarm_get(id)


def security_alarm_update_ticket_id(alarm_id, ticket_id):
    """Create an instance from the values dictionary."""
    return IMPL.security_alarm_update_ticket_id(alarm_id, ticket_id)


def create_task(values):
    return IMPL.create_task(values)


def delete_task(id):
    IMPL.delete_task(id)


def update_state_task(id, running):
    IMPL.update_state_task(id, running)


def get_all_tasks():
    return IMPL.get_all_tasks()
