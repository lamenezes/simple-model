import pytest

from simple_model.builder import model_builder, model_class_builder
from simple_model.model import Model


def test_model_class_builder():
    Birl = model_class_builder('Birl', {'f': 'foo', 'b': 'bar'})
    birl = Birl()

    assert issubclass(Birl, Model)
    keys = ('f', 'b')
    assert len(Birl.fields) == len(keys)
    assert set(Birl.fields) == set(keys)

    assert birl.clean() is None
    assert birl.validate(raise_exception=False) is True
    assert birl.serialize() == {'f': None, 'b': None}


def test_model_builder():
    data = {
        'foo': 'foo',
        'bar': 'bar',
    }
    birl = model_builder('Birl', data, recurse=False)
    assert birl.foo == 'foo'
    assert birl.bar == 'bar'


def test_model_builder_recurse_false():
    my_model = {'baz': 'baz', 'qux': 'qux'}
    data = {
        'foo': 'foo',
        'bar': 'bar',
        'my_model': my_model,
    }
    birl = model_builder('Birl', data, recurse=False)
    assert birl.foo == 'foo'
    assert birl.bar == 'bar'
    assert birl.my_model == my_model


def test_model_builder_recurse():
    my_model = {'baz': 'baz', 'qux': 'qux'}
    data = {
        'foo': 'foo',
        'bar': 'bar',
        'my_model': my_model,
    }
    birl = model_builder('Birl', data)
    assert birl.foo == 'foo'
    assert birl.bar == 'bar'
    assert birl.my_model.baz == 'baz'
    assert birl.my_model.qux == 'qux'

    assert type(birl.my_model).__name__ == 'MyModel'
    assert type(birl.my_model) not in (Model, type(birl))


@pytest.mark.parametrize('iterable_class', (tuple, list))
def test_model_builder_recurse_iterable(iterable_class):
    my_model = iterable_class([{'baz': 'baz', 'qux': 'qux'}, 1, 2])
    data = {
        'foo': 'foo',
        'bar': 'bar',
        'my_model': my_model,
    }
    birl = model_builder('Birl', data)
    assert birl.foo == 'foo'
    assert birl.bar == 'bar'
    assert birl.my_model[0].baz == 'baz'
    assert birl.my_model[0].qux == 'qux'
    assert birl.my_model[1] == 1
    assert birl.my_model[2] == 2

    assert isinstance(birl.my_model[0], Model)
    assert type(birl.my_model[0]).__name__ == 'NamelessModel'
