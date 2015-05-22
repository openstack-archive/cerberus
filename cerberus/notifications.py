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
import socket

from oslo.config import cfg
from oslo import messaging

from cerberus.openstack.common.gettextutils import _
from cerberus.openstack.common import log


notifier_opts = [
    cfg.StrOpt('default_publisher_id',
               default=None,
               help='Default publisher_id for outgoing notifications'),
    cfg.StrOpt('notifier_topic',
               default='notifications',
               help='The topic that Cerberus uses for generating '
                    'notifications')
]

cfg.CONF.register_opts(notifier_opts)
LOG = log.getLogger(__name__)
_notifier = None


def _get_notifier():
    """Return a notifier object.

    If _notifier is None it means that a notifier object has not been set.
    If _notifier is False it means that a notifier has previously failed to
    construct.
    Otherwise it is a constructed Notifier object.
    """
    global _notifier

    if _notifier is None:
        host = cfg.CONF.default_publisher_id or socket.gethostname()
        try:
            transport = messaging.get_transport(cfg.CONF)
            _notifier = messaging.Notifier(transport, "security.%s" % host,
                                           topic=cfg.CONF.notifier_topic)
        except Exception:
            LOG.exception("Failed to construct notifier")
            _notifier = False

    return _notifier


def _reset_notifier():
    global _notifier
    _notifier = None


def send_notification(operation, resource_type, payload):
    """Send notification to inform observers about the affected resource.

    This method doesn't raise an exception when sending the notification fails.

    :param operation: operation being performed (created, updated, or deleted)
    :param resource_type: type of resource being operated on
    :param resource_id: ID of resource being operated on
    """
    context = {}
    service = 'security'
    event_type = '%(service)s.%(resource_type)s.%(operation)s' % {
        'service': service,
        'resource_type': resource_type,
        'operation': operation}

    notifier = _get_notifier()
    if notifier:
        try:
            notifier.info(context, event_type, payload)
        except Exception:
            LOG.exception(_(
                'Failed to send %(event_type)s notification'),
                {'event_type': event_type})
