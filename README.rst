============
Simple Model
============

.. image:: https://travis-ci.org/lamenezes/simple-model.svg?branch=master
    :target: https://travis-ci.org/lamenezes/simple-model
.. image:: https://coveralls.io/repos/github/lamenezes/simple-model/badge.svg?branch=master
    :target: https://coveralls.io/github/lamenezes/simple-model?branch=master
.. image:: https://badge.fury.io/py/pysimplemodel.svg
    :target: https://badge.fury.io/py/pysimplemodel

*SimpleModel* offers a simple way to handle data using classes instead of a
plenty of lists and dicts.

It has simple objectives:

- Define your fields easily (just a tuple, not dicts or instances of type classes whatever)
- Support for field validation
- Convert to dict

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
        fields = ('name', 'age', 'height', 'weight')
        allow_empty = ('height', 'weight')

        def validate_age(self, value):
            if 0 > value > 150:
                raise ValidationError

        def validate_height(self, value):
            if value <= 0:
                raise ValidationError

.. code:: python

    >> person = Person(name='John Doe', age=18)
    >> person.name
    'John Doe'
    >> person.validate()
    >> dict(person)
    {'name': 'John Doe', 'age': 18, 'height': '', 'weight': ''}


Validation
----------

Model values aren't validated until the `validated` method is called:

.. code:: python

    >> person = Person()  # no exception
    >> person.validate()
    ...
    EmptyField: name field cannot be empty
    >> person = Person(name='Jane Doe', age=60)
    >> person.validate()  # now it's ok!


You may change the validate method to return a boolean instead of raising an
exception:

.. code:: python

    >> person = Person()
    >> person.validate(raise_exception=False)
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
        fields = ('name', 'age')

        def clean_name(self, value):
            return value.strip()

        def clean_age(self, value):
            return int(value)

    >> person = CleanPerson(name='John Doe  \n', age='10')
    >> person.name, person.age
    ('John Doe  \n', '10')
    >> person.clean()
    >> person.name, person.age
    ('John Doe', 10)


Conversion to Dict
------------------

To convert to dict is pretty straight-forward task:

.. code:: python

    >> person = Person(name='Jane Doe', age=60)
    >> dict(person)
    {'age': 60, 'height': None, 'name': 'Jane Doe', 'weight': None}


Simple model also supports dict conversion of nested models:

.. code:: python

    class SocialPerson(Model):
        fields = ('name', 'friend')

    >> person = Person(name='Jane Doe', age=60)
    >> other_person = SocialPerson(name='John Doe', friend=person)
    >> dict(other_person)
    {'friend': {'age': 60, 'height': None, 'name': 'Jane Doe', 'weight': None}, 'name': 'John Doe'}


It also supports nested models as lists:

.. code:: python

    class MoreSocialPerson(Model):
        fields = ('name', 'friends')

    >> person = Person(name='Jane Doe', age=60)
    >> other_person = Person(name='John Doe', age=15)
    >> social_person = MoreSocialPerson(name='Foo Bar', friends=[person, other_person])
    {
        'name': 'Foo Bar',
        'friends': [
            {
                'age': 60,
                'height': None,
                'name': 'Jane Doe',
                'weight': None
            },
            {
                'age': 15,
                'height': None,
                'name': 'John Doe',
                'weight': None
            }
        ]
    }
