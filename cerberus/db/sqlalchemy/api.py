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
import threading

from oslo.config import cfg

from cerberus.common import exception
from cerberus.db.sqlalchemy import migration
from cerberus.db.sqlalchemy import models
from cerberus.openstack.common.db import exception as db_exc
from cerberus.openstack.common.db.sqlalchemy import session as db_session
from cerberus.openstack.common import log


CONF = cfg.CONF

LOG = log.getLogger(__name__)


_ENGINE_FACADE = None
_LOCK = threading.Lock()


_FACADE = None


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade(
            CONF.database.connection,
            **dict(CONF.database.iteritems())
        )
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.
    :param session: if present, the session to use
    """
    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


def db_sync(engine, version=None):
    """Migrate the database to `version` or the most recent version."""
    return migration.db_sync(engine, version=version)


def db_version(engine):
    """Display the current database version."""
    return migration.db_version(engine)


def _security_report_create(values):
    try:
        security_report_ref = models.SecurityReport()
        security_report_ref.update(values)
        security_report_ref.save()
    except db_exc.DBDuplicateEntry as e:
        LOG.exception(e)
        raise exception.ReportExists(id=values['id'])
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()
    return security_report_ref


def security_report_create(values):
    return _security_report_create(values)


def _security_report_update_last_report_date(report_id, date):
    try:
        session = get_session()
        report = model_query(models.SecurityReport, read_deleted="no",
                             session=session).filter(models.SecurityReport.id
                                                     == report_id).first()
        report.last_report_date = date
        report.save(session)
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def security_report_update_last_report_date(report_id, date):
    _security_report_update_last_report_date(report_id, date)


def _security_report_update_ticket_id(report_id, ticket_id):
    try:
        session = get_session()
        report = model_query(models.SecurityReport, read_deleted="no",
                             session=session).filter(models.SecurityReport.id
                                                     == report_id).first()
        report.ticket_id = ticket_id
        report.save(session)
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def security_report_update_ticket_id(report_id, ticket_id):
    _security_report_update_ticket_id(report_id, ticket_id)


def _security_report_get_all(project_id=None):
    try:
        session = get_session()
        if project_id is None:
            return model_query(models.SecurityReport, read_deleted="no",
                               session=session).all()
        else:
            return model_query(models.SecurityReport, read_deleted="no",
                               session=session).\
                filter(models.SecurityReport.project_id == project_id).all()
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def security_report_get_all(project_id=None):
    return _security_report_get_all(project_id=project_id)


def _security_report_get(id):
    try:
        session = get_session()
        return model_query(models.SecurityReport, read_deleted="no",
                           session=session).filter(models.SecurityReport.
                                                   id == id).first()
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def security_report_get(id):
    return _security_report_get(id)


def _security_report_get_from_report_id(report_id):
    try:
        session = get_session()
        return model_query(models.SecurityReport,
                           read_deleted="no",
                           session=session).filter(
            models.SecurityReport.report_id == report_id).first()
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def security_report_get_from_report_id(report_id):
    return _security_report_get_from_report_id(report_id)


def _plugin_info_create(values):
    try:
        plugin_info_ref = models.PluginInfo()
        plugin_info_ref.update(values)
        plugin_info_ref.save()
    except db_exc.DBDuplicateEntry:
        raise exception.PluginInfoExists(id=values['id'])
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()
    return plugin_info_ref


def plugin_info_create(values):
    return _plugin_info_create(values)


def _plugins_info_get():
    try:
        session = get_session()
        return model_query(models.PluginInfo,
                           read_deleted="no",
                           session=session).all()
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def plugins_info_get():
    return _plugins_info_get()


def _plugin_info_get(name):
    try:
        session = get_session()

        return model_query(models.PluginInfo,
                           read_deleted="no",
                           session=session).filter(models.PluginInfo.name ==
                                                   name).first()
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def plugin_info_get(name):
    return _plugin_info_get(name)


def _plugin_info_get_from_uuid(plugin_id):
    try:
        session = get_session()
        return model_query(models.PluginInfo,
                           read_deleted="no",
                           session=session).filter(models.PluginInfo.uuid ==
                                                   plugin_id).first()
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def plugin_info_get_from_uuid(plugin_id):
    return _plugin_info_get_from_uuid(plugin_id)


def _plugin_version_update(plugin_id, version):
    try:
        session = get_session()
        plugin = model_query(models.PluginInfo, read_deleted="no",
                             session=session).filter(models.PluginInfo.id ==
                                                     plugin_id).first()
        plugin.version = version
        plugin.save(session)
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def plugin_version_update(plugin_id, version):
    _plugin_version_update(plugin_id, version)


def _security_alarm_create(values):
    try:
        security_alarm_ref = models.SecurityAlarm()
        security_alarm_ref.update(values)
        security_alarm_ref.save()
    except db_exc.DBDuplicateEntry as e:
        LOG.exception(e)
        raise exception.AlarmExists(id=values['id'])
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()
    return security_alarm_ref


def security_alarm_create(values):
    return _security_alarm_create(values)


def _security_alarm_get_all():
    try:
        session = get_session()
        return model_query(models.SecurityAlarm, read_deleted="no",
                           session=session).all()
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def security_alarm_get_all():
    return _security_alarm_get_all()


def _security_alarm_get(alarm_id):
    try:
        session = get_session()
        return model_query(models.SecurityAlarm,
                           read_deleted="no",
                           session=session).filter(
            models.SecurityAlarm.alarm_id == alarm_id).first()
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def security_alarm_get(alarm_id):
    return _security_alarm_get(alarm_id)


def _security_alarm_update_ticket_id(alarm_id, ticket_id):
    try:
        session = get_session()
        alarm = model_query(models.SecurityAlarm,
                            read_deleted="no",
                            session=session).filter(
            models.SecurityAlarm.alarm_id == alarm_id).first()
        alarm.ticket_id = ticket_id

        alarm.save(session)
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def security_alarm_update_ticket_id(alarm_id, ticket_id):
    _security_alarm_update_ticket_id(alarm_id, ticket_id)


def _create_task(values):
    try:
        task_ref = models.Task()
        task_ref.update(values)
        task_ref.save()
    except db_exc.DBDuplicateEntry as e:
        LOG.exception(e)
        raise exception.TaskExists(id=values['uuid'])
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()
    return task_ref


def create_task(values):
    return _create_task(values)


def _delete_task(task_id):
    try:
        session = get_session()
        task = model_query(models.Task, read_deleted="no",
                           session=session).filter_by(uuid=task_id)
        task.delete()
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def delete_task(task_id):
    _delete_task(task_id)


def _update_state_task(task_id, running):
    try:
        session = get_session()
        task = model_query(models.Task, read_deleted="no",
                           session=session).filter_by(uuid=task_id).first()
        task.running = running
        task.save(session)
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def update_state_task(task_id, running):
    _update_state_task(task_id, running)


def _get_all_tasks():
    try:
        session = get_session()
        return model_query(models.Task, read_deleted="no",
                           session=session).all()
    except Exception as e:
        LOG.exception(e)
        raise exception.DBException()


def get_all_tasks():
    return _get_all_tasks()
