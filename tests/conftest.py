import typing

import pytest

from simple_model.exceptions import ValidationError
from simple_model.models import Model


class MyModel(Model):
    foo: str
    bar: typing.Any
    baz = None
    qux = None

    def validate_foo(self, value):
        if len(value) != 3:
            raise ValidationError()


@pytest.fixture
def model_data():
    return {
        'foo': 'foo',
        'bar': 'bar',
        'baz': '',
        'qux': '',
    }


@pytest.fixture
def model(model_data):
    return MyModel(**model_data)


@pytest.fixture
def model2():
    return MyModel(foo='f00', bar='barbar', baz='', qux='')
