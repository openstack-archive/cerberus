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

import abc
import fnmatch
import json
import six

import oslo.messaging

from cerberus.openstack.common import log
from cerberus.openstack.common import loopingcall
from cerberus.openstack.common import threadgroup


LOG = log.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class PluginBase(object):
    """
    Base class for all plugins
    """

    TOOL_NAME = ""
    TYPE = ""
    PROVIDER = ""
    DESCRIPTION = ""

    _name = None

    _uuid = None

    _event_groups = {
        'INSTANCE': [
            'compute.instance.created',
            'compute.instance.deleted'
            'compute.instance.updated'
        ],
        'NETWORK': [
            'network.created',
        ],
        'PROJECT': [
            'project.created'
        ]
    }

    def __init__(self, description=None, provider=None, type=None,
                 tool_name=None):
        self._subscribedEvents = []
        self._name = "{0}.{1}".format(self.__class__.__module__,
                                      self.__class__.__name__)

    def subscribe_event(self, event):
        if not (event in self._subscribedEvents):
            self._subscribedEvents.append(event)

    def register_manager(self, manager):
        """
        Enables the plugin to add tasks to the  manager
        :param manager: the task manager to add tasks to
        """
        self.manager = manager

    @staticmethod
    def _handle_event_type(subscribed_events, event_type):
        """Check whether event_type should be handled.

        It is according to event_type_to_handle.l
        """
        return any(map(lambda e: fnmatch.fnmatch(event_type, e),
                       subscribed_events))

    @staticmethod
    def get_targets(conf):
        """Return a sequence of oslo.messaging.Target

        Sequence defining the exchange and topics to be connected for this
        plugin.
        """
        return [oslo.messaging.Target(topic=topic)
                for topic in conf.notification_topics]

    @abc.abstractmethod
    def process_notification(self, ctxt, publisher_id, event_type, payload,
                             metadata):
        pass

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        # Check if event is registered for plugin
        if self._handle_event_type(self._subscribedEvents, event_type):
            self.process_notification(ctxt, publisher_id, event_type, payload,
                                      metadata)
    '''
    http://stackoverflow.com/questions/3378949/
    python-decorators-and-class-inheritance
    http://stackoverflow.com/questions/338101/
    python-function-attributes-uses-and-abuses
    '''
    @staticmethod
    def webmethod(func):
        func.is_webmethod = True
        return func


class PluginEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, PluginBase):
            return super(PluginEncoder, self).default(obj)
        methods = [method for method in dir(obj)
                   if hasattr(getattr(obj, method), 'is_webmethod')]
        return {'name': obj._name,
                'subscribed_events': obj._subscribedEvents,
                'methods': methods}


class FixedIntervalLoopingCallEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, loopingcall.FixedIntervalLoopingCall):
            return super(FixedIntervalLoopingCallEncoder, self).default(obj)
        if obj._running is True:
            state = 'running'
        else:
            state = 'stopped'
        return {'id': obj.kw.get('task_id', None),
                'name': obj.kw.get('task_name', None),
                'period': obj.kw.get('task_period', None),
                'type': obj.kw.get('task_type', None),
                'plugin_id': obj.kw.get('plugin_id', None),
                'persistent': obj.kw.get('persistent', 'False'),
                'state': state}


class ThreadEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, threadgroup.Thread):
            return super(ThreadEncoder, self).default(obj)
        return {'id': obj.kw.get('task_id', None),
                'name': obj.kw.get('task_name', None),
                'type': obj.kw.get('task_type', None),
                'plugin_id': obj.kw.get('plugin_id', None),
                'persistent': obj.kw.get('persistent', False),
                'state': 'running'}
