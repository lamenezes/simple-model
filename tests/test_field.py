# Copyright (c) 2017 Luiz Menezes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

import pytest

from simple_model.model import ModelField


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


def test_model_serialize_exclude_fields(model):
    serialized = model.serialize(exclude_fields=('baz', 'qux'))
    assert serialized == {'foo': 'foo', 'bar': 'bar'}
