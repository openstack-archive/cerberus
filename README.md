==========
Cerberus
==========

Cloud infrastructure security
+++++++++++++++++++++++++++++

Goal
----

The objective is to integrate tools in Openstack platform dedicated
to the security of the infrastructure.


Overview
--------

This project is part of the Secured Virtual Cloud project which purpose
is to secure cloud infrastructure. To achieve this goal, tools such as
scanner of vulnerabilities, behavioral analysis, IPS, IDS, SIEM, ... have
to work with Openstack. This is why Cerberus is done. It offers a framework
to integrate such tools in order to propagate  change of the platform to
them and to collect security reports and security alerts.



Roadmap
-------

* v1
- Framework of plugins to integrate security tools
- Tasks API
- Vulnerability reports
- Security alerts

* v2
- Integration of the dashboard of the security tools
- Persistent tasks
