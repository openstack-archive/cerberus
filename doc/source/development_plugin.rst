===============
Writing plugins
===============

This documentation gives you some clues on how to write a new plugin for
Cerberus if you wish to integrate a security component which is not covered by
an existing plugin.

Cerberus manager
================

The cerberus manager is implemented in ``cerberus/manager.py``. The cerberus
manager loads all plugins defined in the namespace ``cerberus.plugins``.
It is also responsible of tasks management.

Plugins
=======

Cerberus manager makes use of stevedore to load extensions dynamically.
Plugins can:

    * subscribe to notifications sent through AMQP.
    * define a callable method (@webmethod) which will be invoked either once or periodically thanks to a task.

Notifications
-------------

Plugins must implement the method ``process_notification(self, ctxt, publisher_id, event_type, payload, metadata):``
which receives an event message the plugin subscribed to.

For example, the ``test_plugin`` plugin listens to one event:

    * image.update

Tasks
-----

For a plugin to be invoked through a task, it must implement a method with
decorator ``@webmethod``

For example, the ``test_plugin`` plugin defines one callable method:

    * get_security_reports


Adding new plugins
------------------

Cerberus needs to be easy to extend and configure so it can be tuned for each
installation. A plugin system based on setuptools entry points makes it easy
to add new monitors in the agents. In particular, Cerberus uses Stevedore, and
you should put your entry point definitions in the entry_points.txt file of
your Cerberus egg.
Alternatively, you can put your entry point definitions in the setup.cfg file
before installing Cerberus
Installing a plugin automatically activates it the next time the cerberus
manager starts.