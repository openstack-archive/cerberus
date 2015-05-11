=======================
Cerberus's Architecture
=======================

Cerberus can be cut in two big parts:

* API
* Manager


.. graphviz:: graph/arch.dot


Module loading and extensions
=============================

Cerberus manager makes use of stevedore to load extensions dynamically.