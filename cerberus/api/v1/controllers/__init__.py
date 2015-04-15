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

from pecan import rest

from cerberus.api.v1.controllers import alerts as alerts_api
from cerberus.api.v1.controllers import plugins as plugins_api
from cerberus.api.v1.controllers import security_reports as \
    security_reports_api
from cerberus.api.v1.controllers import tasks as tasks_api


class V1Controller(rest.RestController):
    """API version 1 controller. """
    alerts = alerts_api.AlertsController()
    plugins = plugins_api.PluginsController()
    security_reports = security_reports_api.SecurityReportsController()
    tasks = tasks_api.TasksController()
