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


class MyValidationError(ValidationError):
    pass


@pytest.fixture
def model_field(model):
    return ModelField(model, name='bar', value=1, allow_empty=True)


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
