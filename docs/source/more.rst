Customizing the fields on your model
====================================

Models are used to manage business logic, data and rules of applications.
Data is represented by model classes and its fields. The easiest way to
define fields using simple model is by using `type hints`_ syntax:

.. code:: python

    from decimal import Decimal

    from simple_model import Model


    class ProductCategory(Model):
        name: str
        is_active: bool = False


    class Product(Model):
        title: str
        description: str
        category: ProductCategory
        price: Decimal
        is_active: bool = False


In the example above we create two models ``ProductCategory`` with ``name``
and ``is_active`` fields and ``Product`` with ``title``, ``description`` and
other fields.

simple model will automtically create custom initializers (``__init__`` methods
or constructors) that receives all the specified fields as parameters.
To create model instances just do the following:


.. code:: python

    category = ProductCategory(
        name='clothing',
        is_active=True,
    )
    product = Product(
        title='Pants',
        description='Pants are great',
        category=category,
        price=80,
        is_active=True,
    )


As shown in the models above it is possible to can easily customize field types
by defining the class attributes using `type hints`_. It is also possible to
provide a default value for each field by setting values on each field on the
model class.


Defining fields without explicit types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you don't want to enforce types on your fields it is possible to:

1. Use ``typing.Any`` as field type
2. Define fields using the ``Meta`` class

Let's try to define fields without typing by using the first approach:

.. code:: python

    import typing

    from simple_model import Model


    class Bag:
        name: typing.Any
        brand: typing.Any
        items: typing.Any


This notation can turn repetitive when working with a great number of fields.
So simple model also support creating fields by defining a fields attribute
inside the model ``Meta`` class. The attribute must be a tuple of the name
of each field as a string. This behaviour is shown in the following example:

.. code:: python

    class Bag:
        class Meta:
            fields = (
                'name',
                'brand',
                'items',
            )


The result is the same on both examples: a model ``Bag`` is created with
``name``, ``brand`` and ``items`` fields. Model instances are created the
same way as showed on previous examples.

It is also possible to define fields using both approaches:

.. code:: python

    # TBD


Validating data on your model
=============================

TBD


Cleaning values on your fields
==============================

TBD


Converting models to dict
=========================

TBD


Creating models instances and classes from dicts
================================================

TBD


FAQ
===

TBD


.. _`type hints`: https://www.python.org/dev/peps/pep-0484/#type-definition-syntax
