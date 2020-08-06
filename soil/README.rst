====
soil
====

Basic Python framework including REST API, database access, RPC, etc.

This framework is abstracted from OpenStack projects, shares common design,
basic functions to quicken the process of creating new Python project, this
project provides demos to show how to implement specific function.

Features
--------

* Generate config sample config file automatically
  run 'tox -e genconfig' to generate latest sample config file. Need update
  etc/soil/soil.conf.sample when add/delete/change config option. For more details,
  please refer to: https://docs.openstack.org/developer/oslo.config/generator.html.

* Soil provides db api module to implements CRUD on two database tables:
  demos and services.

* Soil API deploys a WSGI server for accessing backend resources and also
  provides demos to show how to CRUD resources.
