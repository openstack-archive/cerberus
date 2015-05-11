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

import functools
import json
import kombu
import logging

from oslo.messaging._drivers import amqp as rpc_amqp
from oslo.messaging._drivers import amqpdriver
from oslo.messaging._drivers import common as rpc_common
from oslo.messaging._drivers import impl_rabbit
from oslo.messaging.openstack.common.gettextutils import _  # noqa


LOG = logging.getLogger(__name__)


def _get_queue_arguments(conf):
    """Construct the arguments for declaring a queue.

    If the rabbit_ha_queues option is set, we declare a mirrored queue
    as described here:

      http://www.rabbitmq.com/ha.html

    Setting x-ha-policy to all means that the queue will be mirrored
    to all nodes in the cluster.
    """
    return {'x-ha-policy': 'all'} if conf.rabbit_ha_queues else {}


class CerberusRabbitMessage(dict):

    def __init__(self, raw_message):
        if isinstance(raw_message.payload, unicode):
            message = rpc_common.deserialize_msg(
                json.loads(raw_message.payload))
        else:
            message = rpc_common.deserialize_msg(raw_message.payload)
        super(CerberusRabbitMessage, self).__init__(message)
        self._raw_message = raw_message

    def acknowledge(self):
        self._raw_message.ack()

    def requeue(self):
        self._raw_message.requeue()


class CerberusConsumerBase(impl_rabbit.ConsumerBase):

    def _callback_handler(self, message, callback):
        """Call callback with deserialized message.

        Messages that are processed and ack'ed.
        """

        try:
            callback(CerberusRabbitMessage(message))
        except Exception:
            LOG.exception(_("Failed to process message"
                            " ... skipping it."))
            message.ack()


class CerberusTopicConsumer(CerberusConsumerBase):
    """Consumer class for 'topic'."""

    def __init__(self, conf, channel, topic, callback, tag, exchange_name,
                 name=None, **kwargs):
        """Init a 'topic' queue.

        :param channel: the amqp channel to use
        :param topic: the topic to listen on
        :paramtype topic: str
        :param callback: the callback to call when messages are received
        :param tag: a unique ID for the consumer on the channel
        :param exchange_name: the exchange name to use
        :param name: optional queue name, defaults to topic
        :paramtype name: str

        Other kombu options may be passed as keyword arguments
        """
        # Default options
        options = {'durable': conf.amqp_durable_queues,
                   'queue_arguments': _get_queue_arguments(conf),
                   'auto_delete': conf.amqp_auto_delete,
                   'exclusive': False}
        options.update(kwargs)
        exchange = kombu.entity.Exchange(name=exchange_name,
                                         type='topic',
                                         durable=options['durable'],
                                         auto_delete=options['auto_delete'])
        super(CerberusTopicConsumer, self).__init__(channel,
                                                    callback,
                                                    tag,
                                                    name=name or topic,
                                                    exchange=exchange,
                                                    routing_key=topic,
                                                    **options)


class CerberusConnection(impl_rabbit.Connection):

    def __init__(self, conf, url):
        super(CerberusConnection, self).__init__(conf, url)

    def declare_topic_consumer(self, exchange_name, topic, callback=None,
                               queue_name=None):
        """Create a 'topic' consumer."""
        self.declare_consumer(functools.partial(CerberusTopicConsumer,
                                                name=queue_name,
                                                exchange_name=exchange_name,
                                                ),
                              topic, callback)


class CerberusRabbitDriver(amqpdriver.AMQPDriverBase):

    def __init__(self, conf, url,
                 default_exchange=None,
                 allowed_remote_exmods=None):
        conf.register_opts(impl_rabbit.rabbit_opts)
        conf.register_opts(rpc_amqp.amqp_opts)

        connection_pool = rpc_amqp.get_connection_pool(conf,
                                                       url,
                                                       CerberusConnection)

        super(CerberusRabbitDriver, self).__init__(conf, url,
                                                   connection_pool,
                                                   default_exchange,
                                                   allowed_remote_exmods)
