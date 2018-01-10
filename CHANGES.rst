=======
Changes
=======

1.0.0 / 2018-01-10
==================

* Move model field customization to Meta class inside model
* Support field definition using type hints (python 3.6 only)
* Drop support for python 3.4 and 3.5
* Remove ``DynamicModel``
* Add Changes file and automate versioning from parsing it
* Move main docs to sphinx
* Improve documentation


0.15.0 / 2017-19-12
===================

* Use pipenv
* Drop python 3.3 support


0.14.0 / 2017-21-11
===================

* Add ``model_many_builder()``. It builds lists of models from data lists
* Fix travis config

0.13.0 / 2017-21-11
===================

* Transfrom ``BaseModel.is_empty`` from an instance method to a class method
* Don't raise an exception when ``BaseModel.build_many`` receives empty iterable. Instead returns another empty iterable
