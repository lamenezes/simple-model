# Copyright (c) 2017 Luiz Menezes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

from unittest import mock

import pytest

from simple_model.exceptions import EmptyField, ValidationError
from simple_model.model import ModelField

from .conftest import MyModel


class MyValidationError(ValidationError):
    pass


@pytest.fixture
def model_field():
    model = MyModel(foo='foo', bar='bar', baz='', qux='')
    return ModelField(model, name='bar', value=1, allow_empty=True)


def test_model_field(model_field):
    assert model_field._model
    assert model_field.value == 1
    assert model_field.name == 'bar'
    assert model_field.allow_empty is True
    assert str(model_field) == '1'
    assert 'bar=1' in repr(model_field)


def test_model_field_set_value_to_its_own_model(model_field):
    with pytest.raises(TypeError):
        model_field.value = model_field._model


def test_model_field_serialize_simple(model_field):
    model_field.value = 1
    assert model_field.serialize() == 1


def test_model_field_serialize_nested(model2, model_field):
    model_field.value = model2
    assert model_field.serialize() == model2.serialize()


@pytest.mark.parametrize('iterable', (list, tuple))
def test_model_field_serialize_nested_iterable(iterable, model_field, model, model2):
    model_field.value = iterable([model, model2])
    assert model_field.serialize() == [model.serialize(), model2.serialize()]


@pytest.mark.parametrize('iterable', (list, tuple))
def test_model_field_serialize_iterable_empty(iterable, model_field, model, model2):
    model_field.value = iterable([])
    assert model_field.serialize() == []


@pytest.mark.parametrize('iterable', (list, tuple))
def test_model_field_serialize_iterable(iterable, model_field, model, model2):
    model_field.value = iterable([1, 2, 3])
    assert model_field.serialize() == [1, 2, 3]


def test_model_field_validate(model_field):
    validate = mock.MagicMock(return_value=None)
    model_field._validate = validate

    assert model_field.validate() is None


@pytest.mark.parametrize('exception', (ValidationError, EmptyField, MyValidationError))
def test_model_field_validate_validation_error(model_field, exception):
    validate = mock.MagicMock(side_effect=exception('foo'))
    model_field._validate = validate

    with pytest.raises(exception):
        model_field.validate()


@pytest.mark.parametrize('blank_value', (None, '', 0, [], {}, ()))
def test_model_field_validate_empty_field(model_field, blank_value):
    model_field.allow_empty = False
    model_field.value = blank_value
    with pytest.raises(EmptyField):
        model_field.validate()


def test_model_field_clean(model_field):
    model_field._clean = lambda s: s.strip()
    model_field.value = ' foo '

    model_field.clean()

    assert model_field.value == 'foo'


def test_model_field_clean_without_clean_method(model_field):
    model_field._clean = None
    model_field.value = ' foo '

    model_field.clean()

    assert model_field.value == ' foo '
