# Copyright (c) 2017 Luiz Menezes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

import pytest

from simple_model.model import Model, ModelField
from simple_model.exceptions import EmptyField, ValidationError


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


@pytest.fixture
def model_field(model):
    return ModelField(model, name='bar', value=1, allow_empty=True)


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


def test_model_fields_allow_empty__all__():
    model = MyEmptyModel()

    model.validate()

    assert model.foo is None
    assert model.bar is None
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

    with pytest.raises(EmptyField) as exc:
        MyModel(foo=empty_value, bar=empty_value).validate()

    assert 'cannot be empty' in str(exc)


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


def test_model_serialize_simple(model):
    serialized_model = {
        'foo': 'foo',
        'bar': 'bar',
        'baz': '',
        'qux': '',
    }
    assert model.serialize() == serialized_model


@pytest.mark.parametrize('iterable', (list, tuple))
def test_model_serialize_nested_list(iterable, model, model2):
    other_model = MyModel(foo='foo', bar=iterable([model, model2]), baz=model)
    serialized = other_model.serialize()
    expected = {
        'foo': 'foo',
        'bar': [model.serialize(), model2.serialize()],
        'baz': model.serialize(),
        'qux': None
    }
    assert serialized == expected


def test_model_field_serialize_simple(model_field):
    model_field.value = 1
    assert model_field.serialize() == 1


def test_model_field_serialize_nested(model, model_field):
    model_field.value = model
    assert model_field.serialize() == model.serialize()


@pytest.mark.parametrize('iterable', (list, tuple))
def test_model_field_serialize_nested_iterable(iterable, model_field, model, model2):
    model_field.value = iterable([model, model2])
    assert model_field.serialize() == [model.serialize(), model2.serialize()]


def test_model_serialize_exclude_fields(model):
    serialized = model.serialize(exclude_fields=('baz', 'qux'))
    assert serialized == {'foo': 'foo', 'bar': 'bar'}
