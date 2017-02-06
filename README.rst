============
Simple Model
============

.. image:: https://travis-ci.org/lamenezes/simple-model.svg?branch=master
    :target: https://travis-ci.org/lamenezes/simple-model

.. image:: https://coveralls.io/repos/github/lamenezes/simple-model/badge.svg?branch=master
    :target: https://coveralls.io/github/lamenezes/simple-model?branch=master


*SimpleModel* offers a simple way to handle data using classes instead of a
plenty of lists and dicts.

It has simple objectives:

- Define your fields easily (just a tuple, not dicts or instances of type classes whatever)
- Support for field validation
- Serialize to dict

That's it. If you want something more complex there are plenty of libraries and
frameworks that does a lot of cool stuff.

--------------
How to install
--------------

.. code:: shell

    pip install pysimplemodel

----------
How to use
----------

.. code:: python

    from simple_model import Model
    from simple_model.exceptions import ValidationError


    class Person(Model):
        fields = ('name', 'age', 'gender', 'height', 'weight')
        allow_empty = ('height', 'weight')

        def validate_age(self, value):
            if 0 > value > 150:
                raise ValidationError

        def validate_gender(self, value):
            if value not in ('M', 'F'):
                raise ValidationError

.. code:: python

    >> person = Person(name='John Doe', age=18, gender='M')
    >> person.name
    'John Doe'
    >> person.validate()
    >> person.serialize()
    {'name': 'John Doe', 'age': 18, 'gender': 'M', 'height': '', 'weight': ''}


Validation
----------

Model values aren't validated until the `validated` method is called:

.. code:: python

    >> person = Person()  # no exception
    >> person.validate()
    ...
    EmptyField: name field cannot be empty
    >> person = Person(name='Jane Doe', age=60, gender='F')
    >> person.validate()  # now it's ok!


You may change the validate method to return a boolean instead of raising an
exception:

.. code:: python

    >> person = Person()
    >> person.validate(raise_exception=False)
    False
    >>> person = Person(name='Jane Doe', age=60, gender='F')
    >>> person.validate(raise_exception=False)
    True


Cleaning
--------

Sometimes it is necessary to clean some values of your models, this can be
easily done using simple-model:

.. code:: python

    class CleanPerson(Model):
        fields = ('name', 'gender')

        def clean_name(self, value):
            return value.strip()

        def clean_gender(self, value):
            return value.upper()

    >> person = CleanPerson(name='John Doe  \n', gender='m')
    >> person.name, person.gender
    ('John Doe  \n', 'm')
    >> person.clean()
    >> person.name, person.gender
    ('John Doe', 'M')


Serialization
-------------

Simple serialization is pretty straight-forward:

.. code:: python

    >> person = Person(name='Jane Doe', age=60, gender='F')
    >> person.serialize()
    {'age': 60, 'gender': 'F', 'height': None, 'name': 'Jane Doe', 'weight': None}

You may also hide some fields from serialization by passing a list to the
`serialize` method:


.. code:: python

    >> person.serialize(exclude_fields=('gender', 'weight'))
    {'age': 60, 'height': None, 'name': 'Jane Doe'}

Simple model also supports nested models:


.. code:: python

    class SocialPerson(Model):
        fields = ('name', 'friend')

    >> person = Person(name='Jane Doe', age=60, gender='F')
    >> other_person = SocialPerson(name='John Doe', friend=person)
    >> other_person.serialize()
    {'friend': {'age': 60, 'gender': 'F', 'height': None, 'name': 'Jane Doe', 'weight': None}, 'name': 'John Doe'}


It also supports nested models as lists:

.. code:: python

    class MoreSocialPerson(Model):
        fields = ('name', 'friends')

    >> person = Person(name='Jane Doe', age=60, gender='F')
    >> other_person = Person(name='John Doe', age=15, gender='M')
    >> social_person = MoreSocialPerson(name='Foo Bar', friends=[person, other_person])
    {
        'name': 'Foo Bar',
        'friends': [
            {
                'age': 60,
                'gender': 'F',
                'height': None,
                'name': 'Jane Doe',
                'weight': None
            },
            {
                'age': 15,
                'gender': 'M',
                'height': None,
                'name': 'John Doe',
                'weight': None
            }
        ]
    }
