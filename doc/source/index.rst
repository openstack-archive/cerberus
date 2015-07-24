.. cerberus documentation master file, created by
   sphinx-quickstart on Wed May 14 23:05:42 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==============================================
Welcome to Cerberus's developer documentation!
==============================================

Introduction
============

Cerberus is a Security As A Service project aimed at integrating security tools
inside Openstack.

Cerberus offers a framework to integrate **security components** (scanners of
vulnerabilities, behavior analysis, IPS, IDS, SIEM) in order to propagate
changes of the platform to them and to collect security reports and security
alarms.

Installation
============

.. toctree::
   :maxdepth: 1

   installation


Architecture
============

.. toctree::
   :maxdepth: 1

   arch


API References
==============

.. toctree::
   :maxdepth: 1

   webapi/root
   webapi/v1


Plugin development
==================

.. toctree::
   :maxdepth: 1

   development_plugin


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
