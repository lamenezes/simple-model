============
Simple Model
============

.. image:: https://badge.fury.io/py/pysimplemodel.svg
    :target: https://github.com/lamenezes/simple-model

.. image:: https://img.shields.io/badge/python-3.6-blue.svg
    :target: https://github.com/lamenezes/simple-model

.. image:: https://img.shields.io/github/license/lamenezes/simple-model.svg
    :target: https://github.com/lamenezes/simple-model/blob/master/LICENSE

.. image:: https://travis-ci.org/lamenezes/simple-model.svg?branch=master
    :target: https://travis-ci.org/lamenezes/simple-model

.. image:: https://coveralls.io/repos/github/lamenezes/simple-model/badge.svg?branch=master
    :target: https://coveralls.io/github/lamenezes/simple-model?branch=master


*SimpleModel* offers a simple way to handle data using classes instead of a
plenty of lists and dicts.

It has simple objectives:

- Define your fields easily (just a tuple, nor dicts or instances of type classes whatever)
- Support for field validation
- Conversion to dict

That's it. If you want something more complex there are plenty of libraries and
frameworks that does a lot of cool stuff.

.. contents:: **Table of Contents**


How to install
--------------

.. code:: shell

    pip install pysimplemodel


How to use
----------

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

.. code:: python

    >>> person = Person(age=18.0, name='John Doe ')
    >>> person.name
    'John Doe '
    >>> person.clean()
    >>> person.name
    'John Doe'
    >>> person.age
    18
    >>> person.validate(raise_exception=False)
    True
    >>> dict(person)
    {
        'age': 18,
        'height': '',
        'name': 'John Doe',
        'weight': '',
    }


Validation
----------

Model values aren't validated until the `validated` method is called:

.. code:: python

    >>> person = Person()  # no exception
    >>> person.validate()
    ...
    EmptyField: name field cannot be empty
    >>> person = Person(name='Jane Doe', age=60)
    >>> person.validate()  # now it's ok!


You may change the validate method to return a boolean instead of raising an
exception:

.. code:: python

    >>> person = Person()
    >>> person.validate(raise_exception=False)
    False
    >>> person = Person(name='Jane Doe', age=60)
    >>> person.validate(raise_exception=False)
    True


Cleaning
--------

Sometimes it is necessary to clean some values of your models, this can be
easily done using simple-model:

.. code:: python

    class CleanPerson(Model):
        age: int
        name: str

        def clean_name(self, name):
            return name.strip()


    >>> person = CleanPerson(name='John Doe  \n', age='10')
    >>> person.name, person.age
    ('John Doe  \n', '10')
    >>> person.clean()
    >>> person.name, person.age
    ('John Doe', 10)


Build many models
-----------------

It's possible to build many models in a single step, it can be done by passing an iterable
to the `build_many` method.

.. code:: python

    >>> people = [
        {'name': 'John Doe'},
        {'name': 'John Doe II'},
    ]
    >>> models = Person.build_many(people)


Conversion to Dict
------------------

To convert to dict is pretty straight-forward task:

.. code:: python

    >>> person = Person(name='Jane Doe', age=60)
    >>> dict(person)
    {
        'age': 60,
        'height': None,
        'name': 'Jane Doe',
        'weight': None,
    }


Simple model also supports dict conversion of nested models:

.. code:: python

    class SocialPerson(Model):
        friend: Person
        name: str


    >>> person = Person(name='Jane Doe', age=60)
    >>> other_person = SocialPerson(name='John Doe', friend=person)
    >>> dict(other_person)
    {
        'friend': {
            'age': 60,
            'height': None,
            'name': 'Jane Doe',
            'weight': None,
        },
        'name': 'John Doe',
    }


It also supports nested models as lists:

.. code:: python

    import typing


    class MoreSocialPerson(Model):
        friends: typing.List[Friend]
        name: str


    >>> person = Person(name='Jane Doe', age=60)
    >>> other_person = Person(name='John Doe', age=15)
    >>> social_person = MoreSocialPerson(name='Foo Bar', friends=[person, other_person])
    >>> dict(social_person)
    {
        'name': 'Foo Bar',
        'friends': [
            {
                'age': 60,
                'height': None,
                'name': 'Jane Doe',
                'weight': None,
            },
            {
                'age': 15,
                'height': None,
                'name': 'John Doe',
                'weight': None,
            }
        ]
    }
