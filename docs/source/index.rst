=====================================
simple model: data handling made easy
=====================================

simple model offers a simple way to work with data. It is very common to use
lists and dict to handle data, but your code can get ugly very easily when
building larger applications.

It allows you to easily define models using classes and perform common tasks
such as data cleaning, validation, type conversion and much more.

this lib has simple objectives:

* Define models easily (support type hints)
* Perform validation, cleaning, default values and type conversion
* Convert models to dict

installing
==========

.. code:: bash

    $ pip install pysimplemodel


Quite easy. ⚽⬆


basic example
=============

To define your models is as simple as stated in the following example:

.. code:: python

    from simple_model import Model
    from simple_model.exceptions import ValidationError


    class Person(Model):
        age: int
        height: float
        name: str
        weight: float

        class Meta:
            allow_empty = ('height', 'weight')

        def clean_name(self, name):
            return name.strip()

        def validate_age(self, age):
            if age < 0 or age > 150:
                raise ValidationError('Invalid value for age "{!r}"'.format(age))

        def validate_height(self, height):
            if height <= 0:
                raise ValidationError('Invalid value for height "{!r}"'.format(age))


    >>> person = Person(name='John Doe', age=18)
    >>> person.name
    'John Doe'
    >>> person.validate()
    >>> dict(person)
    {'name': 'John Doe', 'age': 18, 'height': '', 'weight': ''}


If you want to understand better other simple model features consult the
following pages simple model's docs.


More Docs
=========

.. toctree::
   :maxdepth: 2

   more
