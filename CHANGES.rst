=======
Changes
=======

UNRELEASED
==========


1.1.1 / 2018-15-02
==================

* Fix attribute default value as function so when the model receives the field value the default value is ignored


1.1.0 / 2018-15-02
==================

* Fix ``setup.py`` ``long_description``
* Allow models fields be defined with class attributes without typing
* Fix type conversion on fields using ``typing.List[...]``
* Bugfix: remove ``Meta`` attribute from model class meta fields
* Fields attributes may receive function as default values. The function is executed
  (without passing arguments to it) on model instantiation


1.0.2 / 2018-01-10
==================

* Add missing function name to ``__all__`` on ``simple_model.__init__``


1.0.1 / 2018-01-10
==================

* Fix setup.py


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
