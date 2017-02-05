# Copyright (c) 2017 Luiz Menezes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

import pytest

from simple_model.exceptions import ValidationError
from simple_model.model import Model


class MyModel(Model):
    fields = ('foo', 'bar', 'baz', 'qux')
    allow_empty = ('baz', 'qux')

    def validate_foo(self, value):
        if len(value) != 3:
            raise ValidationError()


class MyEmptyModel(Model):
    fields = MyModel.fields
    allow_empty = '__all__'


@pytest.fixture
def model():
    return MyModel(foo='foo', bar='bar', baz='', qux='')


@pytest.fixture
def model2():
    return MyModel(foo='f00', bar='barbar', baz='', qux='')
