#
#   Copyright (c) 2015 EUROGICIEL
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

import pecan
from webob import exc

from cerberus.api.v1.controllers import base
from cerberus.common import errors
from cerberus import db
from cerberus.db.sqlalchemy import models
from cerberus.openstack.common import log

LOG = log.getLogger(__name__)


class SecurityReportsController(base.BaseController):

    def list_security_reports(self, project_id=None):
        """ List all the security reports of all projects or just one. """
        try:
            security_reports = db.security_report_get_all(
                project_id=project_id)
        except Exception as e:
            LOG.exception(e)
            raise errors.DbError(
                "Security reports could not be retrieved"
            )
        return security_reports

    @pecan.expose("json")
    def get_all(self):
        """ Get stored security reports.
        :return: list of security reports for one or all projects depending on
        context of the token.
        """
        ctx = pecan.request.context
        try:
            if ctx.is_admin:
                security_reports = self.list_security_reports()
            else:
                security_reports = self.list_security_reports(ctx.tenant_id)
        except errors.DbError:
            raise exc.HTTPNotFound()
        json_security_reports = []
        for security_report in security_reports:
            json_security_reports.append(models.SecurityReportJsonSerializer().
                                         serialize(security_report))
        return {'security_reports': json_security_reports}

    def get_security_report(self, id):
        try:
            security_report = db.security_report_get(id)
        except Exception as e:
            LOG.exception(e)
            raise errors.DbError(
                "Security report %s could not be retrieved" % id
            )
        return security_report

    @pecan.expose("json")
    def get_one(self, id):
        """
        Get security reports in db
        :param req: the HTTP request
        :param resp: the HTTP response
        :return:
        """
        try:
            security_report = self.get_security_report(id)
        except errors.DbError:
            raise exc.HTTPNotFound()
        s_report = models.SecurityReportJsonSerializer().\
            serialize(security_report)

        return {'security_report': s_report}
