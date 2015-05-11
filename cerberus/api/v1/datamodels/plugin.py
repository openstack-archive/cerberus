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
#

from cerberus.api.v1.datamodels import base
from wsme import types as wtypes


class PluginResource(base.Base):
    """Type describing a plugin.

    """

    name = wtypes.text
    """Name of the plugin."""

    id = wtypes.IntegerType()
    """Id of the plugin."""

    uuid = wtypes.text
    """Uuid of the plugin."""

    methods = [wtypes.text]
    """Hook methods."""

    version = wtypes.text
    """Version of the plugin."""

    provider = wtypes.text
    """Provider of the plugin."""

    subscribed_events = [wtypes.text]
    """Subscribed events of the plugin."""

    type = wtypes.text
    """Type of the plugin."""

    tool_name = wtypes.text
    """Tool name of the plugin."""

    description = wtypes.text
    """Description of the plugin."""

    def as_dict(self):
        return self.as_dict_from_keys(['name', 'id', 'uuid', 'methods',
                                       'version', 'provider',
                                       'subscribed_events', 'type',
                                       'tool_name', 'description'])

    def __init__(self, initial_data):
        super(PluginResource, self).__init__()
        for key in initial_data:
            setattr(self, key, initial_data[key])


class PluginResourceCollection(base.Base):
    """A list of Plugins."""

    plugins = [PluginResource]
