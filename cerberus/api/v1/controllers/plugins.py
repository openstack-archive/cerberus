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

import json
import pecan
from webob import exc

from oslo import messaging

from cerberus.api.v1.controllers import base
from cerberus.common import errors
from cerberus import db
from cerberus.db.sqlalchemy import models
from cerberus.openstack.common import log


LOG = log.getLogger(__name__)

_ENFORCER = None


class PluginsController(base.BaseController):

    def list_plugins(self):
        """ List all the plugins installed on system """

        # Get information about plugins loaded by Cerberus
        try:
            plugins = self._plugins()
        except messaging.RemoteError as e:
            LOG.exception(e)
            raise
        try:
            # Get information about plugins stored in db
            db_plugins_info = db.plugins_info_get()
        except Exception as e:
            LOG.exception(e)
            raise
        plugins_info = []
        for plugin_info in db_plugins_info:
            plugins_info.append(models.PluginInfoJsonSerializer().
                                serialize(plugin_info))
        plugins_full_info = []
        for plugin in plugins:
            for plugin_info in plugins_info:
                if (plugin.get('name') == plugin_info.get('name')):
                    plugins_full_info.append(dict(plugin.items()
                                             + plugin_info.items()))
        return plugins_full_info

    def _plugins(self):
        """ Get a list of plugins loaded by Cerberus Manager """
        ctx = pecan.request.context.to_dict()
        try:
            plugins = self.client.call(ctx, 'get_plugins')
        except messaging.RemoteError as e:
            LOG.exception(e)
            raise
        plugins_ = []
        for plugin in plugins:
            plugin_ = json.loads(plugin)
            plugins_.append(plugin_)
        return plugins_

    @pecan.expose("json")
    def get_all(self):
        """ Get a list of plugins loaded by Cerberus manager
        :return: a list of plugins loaded by Cerberus manager
        :raises:
            HTTPServiceUnavailable: an error occurred in Cerberus Manager or
            the service is unavailable
            HTTPNotFound: any other error
        """

        # Get information about plugins loaded by Cerberus
        try:
            plugins = self.list_plugins()
        except messaging.RemoteError:
            raise exc.HTTPServiceUnavailable()
        except Exception as e:
            LOG.exception(e)
            raise exc.HTTPNotFound()
        return {'plugins': plugins}

    def get_plugin(self, uuid):
        """ Get information about plugin loaded by Cerberus"""
        try:
            plugin = self._plugin(uuid)
        except messaging.RemoteError:
            raise
        except errors.PluginNotFound:
            raise
        try:
            # Get information about plugin stored in db
            db_plugin_info = db.plugin_info_get_from_uuid(uuid)
            plugin_info = models.PluginInfoJsonSerializer().\
                serialize(db_plugin_info)
        except Exception as e:
            LOG.exception(e)
            raise
        return dict(plugin_info.items() + plugin.items())

    def _plugin(self, uuid):
        """ Get a specific plugin thanks to its identifier """
        ctx = pecan.request.context.to_dict()
        try:
            plugin = self.client.call(ctx, 'get_plugin_from_uuid', uuid=uuid)
        except messaging.RemoteError as e:
            LOG.exception(e)
            raise

        if plugin is None:
            LOG.exception('Plugin %s not found.' % uuid)
            raise errors.PluginNotFound(uuid)
        return json.loads(plugin)

    @pecan.expose("json")
    def get_one(self, uuid):
        """ Get details of a specific plugin whose identifier is uuid
        :param uuid: the identifier of the plugin
        :return: details of a specific plugin
        :raises:
            HTTPServiceUnavailable: an error occurred in Cerberus Manager or
            the service is unavailable
            HTTPNotFound: Plugin is not found. Also any other error
        """
        try:
            plugin = self.get_plugin(uuid)
        except messaging.RemoteError:
            raise exc.HTTPServiceUnavailable()
        except errors.PluginNotFound:
            raise exc.HTTPNotFound()
        except Exception as e:
            LOG.exception(e)
            raise exc.HTTPNotFound()
        return {'plugin': plugin}
