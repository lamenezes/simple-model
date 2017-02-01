# Copyright (c) 2017 Luiz Menezes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

import pytest

from simple_model import Model
from simple_model.exceptions import EmptyField, ValidationError


class MyModel(Model):
    fields = ('foo', 'bar', 'baz', 'qux')
    allow_empty = ('baz', 'qux')

    def validate_foo(self, value):
        if len(value) != 3:
            raise ValidationError()


@pytest.fixture
def model():
    return MyModel(foo='foo', bar='bar', baz='', qux='')


def test_model_fields(model):
    assert model.foo == 'foo'
    assert model.bar == 'bar'
    assert model.baz == ''
    assert model.qux == ''


def test_model_fields_allow_empty():
    model = MyModel(foo='foo', bar='bar')
    assert model.foo == 'foo'
    assert model.bar == 'bar'
    assert model.baz is None
    assert model.qux is None


@pytest.mark.parametrize('empty_value', (None, '', 0))
def test_model_fields_validate_allow_empty_error(empty_value):
    with pytest.raises(EmptyField):
        MyModel().validate()

    with pytest.raises(EmptyField):
        MyModel(foo=empty_value).validate()

    with pytest.raises(EmptyField):
        MyModel(bar=empty_value).validate()

    with pytest.raises(EmptyField):
        MyModel(foo=empty_value, bar=empty_value).validate()


def test_model_fields_field_validation(model):
    assert model.validate() is True


def test_model_fields_field_validation_without_raise(model):
    model.foo = ''
    assert model.validate(raise_exception=False) is False


def test_model_fields_field_validation_error(model):
    model.foo = 'fo'
    with pytest.raises(ValidationError):
        model.validate()


def test_model_fields_field_validation_error_without_raise(model):
    model.foo = 'fo'
    assert model.validate(raise_exception=False) is False


def test_model_serialize(model):
    serialized_model = {
        'foo': 'foo',
        'bar': 'bar',
        'baz': '',
        'qux': '',
    }
    assert model.serialize() == serialized_model


def test_model_serialize_model(model):
    other_model = MyModel(foo='foo', bar=model)
    serialized = other_model.serialize()
    assert serialized == {'foo': 'foo', 'bar': model.serialize(), 'baz': None, 'qux': None}
