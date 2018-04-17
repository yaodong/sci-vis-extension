###
TDA
###

1. Requirements
===============

TODO

2. Development
==============

This project has two separated servers. They both has builtin server for development.

2.1 start api server
--------------------

::

   cd api/
   python manage.py runserver

Visit ``http://127.0.0.1:8000/api/`` to check if it's running successfully.

Run UI
------

::

   cd web/
   ember serve

Visit ``http://localhost:4200`` to check if it's running.
