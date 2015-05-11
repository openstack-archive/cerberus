#######################################
Cerberus installation and configuration
#######################################


Install from source
===================

There is no release of Cerberus as of now, the installation can be done from
the git repository.

Retrieve and install Cerberus :

::

    git clone git://git.openstack.org/stackforge/cerberus
    cd cerberus
    python setup.py install

This procedure installs the ``cerberus`` python library and a few
executables:

* ``cerberus-api``: API service
* ``cerberus-agent``: Task management service

Install a sample configuration file :

::

    mkdir /etc/cerberus
    cp etc/cerberus/cerberus.conf.sample /etc/cerberus/cerberus.conf

Configure Cerberus
==================

Edit :file:`/etc/cerberus/cerberus.conf` to configure Cerberus.

The following shows the basic configuration items:

.. code-block:: ini

    [DEFAULT]
    verbose = True
    log_dir = /var/log/cerberus

    rabbit_host = RABBIT_HOST
    rabbit_userid = openstack
    rabbit_password = RABBIT_PASSWORD

    [auth]
    username = cerberus
    password = CERBERUS_PASSWORD
    tenant = service
    region = RegionOne
    url = http://localhost:5000/v2.0

    [keystone_authtoken]
    username = cerberus
    password = CERBERUS_PASSWORD
    project_name = service
    region = RegionOne
    auth_url = http://localhost:5000/v2.0
    auth_plugin = password

    [database]
    connection = mysql://cerberus:CERBERUS_DBPASS@localhost/cerberus

Setup the database and storage backend
======================================

MySQL/MariaDB is the recommended database engine. To setup the database, use
the ``mysql`` client:

::

    mysql -uroot -p << EOF
    CREATE DATABASE cerberus;
    GRANT ALL PRIVILEGES ON cerberus.* TO 'cerberus'@'localhost' IDENTIFIED BY 'CERBERUS_DBPASS';
    EOF

Run the database synchronisation scripts:

::

    cerberus-dbsync upgrade

Init the storage backend:

::

    cerberus-storage-init

Setup Keystone
==============

Cerberus uses Keystone for authentication.

To integrate Cerberus to Keystone, run the following commands (as OpenStack
administrator):

::

    keystone user-create --name cerberus --pass CERBERUS_PASS
    keystone user-role-add --user cerberus --role admin --tenant service

Create the ``Security`` service and its endpoints:

::

    keystone service-create --name Cerberus --type security
    keystone endpoint-create --service-id SECURITY_SERVICE_ID \
        --publicurl http://localhost:8300 \
        --adminurl http://localhost:8300 \
        --internalurl http://localhost:8300

Start Cerberus
==============

Start the API and processing services :

::

    cerberus-api --config-file /etc/cerberus/cerberus.conf
    cerberus-agent --config-file /etc/cerberus/cerberus.conf
