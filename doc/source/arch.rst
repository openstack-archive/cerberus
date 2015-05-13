=======================
Cerberus's Architecture
=======================

Cerberus can be cut in two big parts:

* API
* Manager


.. figure:: ./cerberus-arch.png
   :width: 100%
   :align: center
   :alt: Architecture summary


Module loading and extensions
=============================

Cerberus manager makes use of stevedore to load extensions dynamically.