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
