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

- Define your fields easily (just a tuple, not dicts or instances from type classes whatever)
- Support for field validation
- Serialize to dict

That's it. If you want something more complex there are plenty of libraries and frameworks that does a lot of cool stuff.


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
