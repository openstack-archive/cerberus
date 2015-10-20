=============================
Enabling cerberus in DevStack
=============================

1. Download Devstack::

    git clone https://git.openstack.org/openstack-dev/devstack
    cd devstack

2. Add this repo as an external repository into your ``local.conf`` file::

    [[local|localrc]]
    enable_plugin cerberus https://git.openstack.org/openstack/cerberus

3. Run ``stack.sh``.
