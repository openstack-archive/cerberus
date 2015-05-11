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

from cerberus.api.v1.datamodels import base
from wsme import types as wtypes


class TaskResource(base.Base):
    """ Representation of a task.
    """
    name = wtypes.wsattr(wtypes.text, default="unknown")
    """Name of the task."""

    period = wtypes.IntegerType()
    """Period if periodic."""

    method = wtypes.wsattr(wtypes.text, mandatory=True)
    """Hook methods."""

    state = wtypes.wsattr(wtypes.text)
    """Running or not."""

    id = wtypes.IntegerType()
    """Associated task id."""

    plugin_id = wtypes.wsattr(wtypes.text, mandatory=True)
    """Associated plugin id."""

    type = wtypes.wsattr(wtypes.text, default="unique")
    """Type of the task."""

    persistent = wtypes.wsattr(wtypes.text, default="false")
    """If task must persist."""

    def as_dict(self):
        return self.as_dict_from_keys(['name', 'period', 'method', 'state',
                                       'id', 'plugin_id', 'type',
                                       'persistent'])

    def __init__(self, initial_data=None):
        super(TaskResource, self).__init__()
        if initial_data is not None:
            for key in initial_data:
                setattr(self, key, initial_data[key])


class TaskResourceCollection(base.Base):
    """A list of Tasks."""

    tasks = [TaskResource]
