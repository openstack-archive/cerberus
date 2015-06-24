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

from cerberus.openstack.common.gettextutils import _  # noqa


class InvalidOperation(Exception):

    def __init__(self, description):
        super(InvalidOperation, self).__init__(description)


class PluginNotFound(InvalidOperation):

    def __init__(self, uuid):
        super(PluginNotFound, self).__init__("Plugin %s does not exist"
                                             % str(uuid))


class TaskPeriodNotInteger(InvalidOperation):

    def __init__(self):
        super(TaskPeriodNotInteger, self).__init__(
            "The period of the task must be provided as an integer"
        )


class TaskNotFound(InvalidOperation):

    def __init__(self, _id):
        super(TaskNotFound, self).__init__(
            _('Task %s does not exist') % _id
        )


class TaskDeletionNotAllowed(InvalidOperation):
    def __init__(self, _id):
        super(TaskDeletionNotAllowed, self).__init__(
            _("Deletion of task %s is not allowed because either it "
              "does not exist or it is not recurrent") % _id
        )


class TaskStartNotAllowed(InvalidOperation):
    def __init__(self, _id):
        super(TaskStartNotAllowed, self).__init__(
            _("Starting task %s is not allowed because either it "
              "does not exist or it is not recurrent") % _id
        )


class TaskStartNotPossible(InvalidOperation):
    def __init__(self, _id):
        super(TaskStartNotPossible, self).__init__(
            _("Starting task %s is not possible because it is running") % _id
        )


class MethodNotString(InvalidOperation):

    def __init__(self):
        super(MethodNotString, self).__init__(
            "Method must be provided as a string"
        )


class MethodNotCallable(InvalidOperation):

    def __init__(self, method, name):
        super(MethodNotCallable, self).__init__(
            "Method named %s is not callable by plugin %s"
            % (str(method), str(name))
        )


class TaskObjectNotProvided(InvalidOperation):

    def __init__(self):
        super(TaskObjectNotProvided, self).__init__(
            "Task object not provided in request"
        )


class PluginIdNotProvided(InvalidOperation):

    def __init__(self):
        super(PluginIdNotProvided, self).__init__(
            "Plugin id not provided in request"
        )


class MethodNotProvided(InvalidOperation):

    def __init__(self):
        super(MethodNotProvided, self).__init__(
            "Method not provided in request"
        )


class PolicyEnforcementError(Exception):

    def __init__(self):
        super(PolicyEnforcementError, self).__init__(
            "Policy enforcement error"
        )


class DbError(Exception):

    def __init__(self, description):
        super(DbError, self).__init__(description)
