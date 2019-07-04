=======
Changes
=======

2.4.3 / 2019-07-04
==================

* Fix model.as_dict() when model has enum attribute

2.4.2 / 2019-04-26
==================

* Fix model field custom validate method on subclass of Model subclasses

2.4.1 / 2019-04-23
==================

* Fix model inheritance to keep _is_valid out of model fields


2.4.0 / 2019-04-08
==================

* Add Model.as_dict() helper function to make it easier to convert models to dict
* Add a first implementation of the lazy validation model (LazyModel)
* Change Model._validation_count (int) to Model._is_valid (bool) to make model validation handling more simple
* Move BaseModel metaclass black magic to a separate module (improve Model code readability)


2.3.3 / 2018-11-29
==================

* Fix type hints


2.3.2 / 2018-11-28
==================

* Fix model validation to avoid accessing properties unless it's really necessary


2.3.1 / 2018-11-28
==================

* Fix type conversion to avoid converting when the field value is a subclass of the expected type


2.3.0 / 2018-10-24
==================

* Support typing.Optional on field definitions. Thanks @daneoshiga.
* Minor performance enhancements. Thanks @daneoshiga.


2.2.0 / 2018-10-23
==================

* Remove "private" attributes (e.g. `Foo.__bar`) from model fields. Thanks @georgeyk
* Support typing.Union on field definitions. Thanks @daneoshiga.


2.1.2 / 2018-07-22
==================

* Add support to Python 3.7 support.


2.1.1 / 2018-04-21
==================

* Fix model validation for fields defined by properties with setters


2.1.0 / 2018-04-20
==================

* Add support to property (getter and setter) as model fields
* Move ModeField relation to Model from class attributes to Meta


2.0.4 / 2018-04-19
==================

* Fix model_many_builder properly using cls argument


2.0.3 / 2018-04-13
==================

* Use os.path instead of Pathlib on setup


2.0.2 / 2018-04-10
==================

* Fix version extraction


2.0.1 / 2018-04-10
==================

* Fix setup path handling when extracting version from changelog file


2.0.0 / 2018-04-10
==================

* Move clean responsibility to validation (remove ``clean`` method support)
* Move conversion on validation from field to model
* Remove ``Meta`` class from simple model
* Fix model validation to properly validate fields with values of list of models
* Fix model field converstion for cases when field type is a subclass of Model
* Move conversion to dict to ``simple_model.to_dict`` function (instead of built-in ``dict`` function)
* Return generator on ``simple_model.builder.model_many_builder`` instead of list
* Fix model conversion on fields defined as ``list`` type
* Fix setup.py path handling


1.1.5 / 2018-03-05
==================

* Fix fields to be mandatory by default as designed / stated in docs


1.1.4 / 2018-03-05
==================

* Fix ``Model.clean()``: call model validate after model cleaning instead of field validate after field cleaning


1.1.3 / 2018-02-27
==================

* Fix ``model_many_builder`` to stop raising errors when empty iterable is received as argument


1.1.2 / 2018-02-21
==================

* Fix field conversion to only happen when value is not None
* Raise exception when trying to convert field with invalid model type
* Fix model fields to stop including some methods and properties


1.1.1 / 2018-02-15
==================

* Fix attribute default value as function so when the model receives the field value the default value is ignored


1.1.0 / 2018-02-15
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


0.15.0 / 2017-12-19
===================

* Use pipenv
* Drop python 3.3 support


0.14.0 / 2017-11-21
===================

* Add ``model_many_builder()``. It builds lists of models from data lists
* Fix travis config


0.13.0 / 2017-11-21
===================

* Transfrom ``BaseModel.is_empty`` from an instance method to a class method
* Don't raise an exception when ``BaseModel.build_many`` receives empty iterable. Instead returns another empty iterable
