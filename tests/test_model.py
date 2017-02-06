# Copyright (c) 2017 Luiz Menezes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

import pytest

from simple_model.exceptions import EmptyField, ValidationError

from .conftest import MyModel, MyEmptyModel


def test_model_fields(model):
    assert model.foo == 'foo'
    assert model.bar == 'bar'
    assert model.baz == ''
    assert model.qux == ''
    assert 'foo' in repr(model)


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
    assert model.validate() is None


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


def test_model_serialize_exclude_fields(model):
    serialized = model.serialize(exclude_fields=('baz', 'qux'))
    assert serialized == {'foo': 'foo', 'bar': 'bar'}


def test_model_clean_without_clean_method(model):
    for field_name in model.fields:
        setattr(model, field_name, field_name)

    model.clean()

    for field_name in model.fields:
        assert getattr(model, field_name) == field_name


def test_model_clean(model):
    for field_name in model.fields:
        setattr(model, field_name, ' {} '.format(field_name))
        setattr(model, 'clean_{}'.format(field_name), lambda s: s.strip())

    model.clean()

    for field_name in model.fields:
        assert getattr(model, field_name) == field_name
