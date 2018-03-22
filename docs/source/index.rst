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
        is_active: bool = False
        name: str

        def validate_age(self, age):
            if age < 0 or age > 150:
                raise ValidationError('Invalid age')
            return age

        def validate_name(self, name):
            if len(name) == 0:
                raise ValidationError('Invalid name')
            return name.strip()


.. code:: python

    >>> person = Person(name='John Doe', age=18)
    >>> person.name
    'John Doe'
    >> print(person.is_active)
    False
    >>> person.validate()
    >>> dict(person)
    {'name': 'John Doe', 'age': 18, is_active: False}
    >> other_person = Person(name='', age=44)
    >> other_person.validate()
    Traceback (most recent call last):
      ...
    ValidationError: Invalid name


If you want to understand better other simple model features consult the
following pages simple model's docs.


More Docs
=========

.. toctree::
   :maxdepth: 2

   more
