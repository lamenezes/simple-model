import pytest

from simple_model.builder import model_builder, model_class_builder, model_many_builder
from simple_model.models import Model


def test_model_class_builder():
    Birl = model_class_builder('Birl', {'f': 'foo', 'b': 'bar'})
    birl = Birl()

    assert isinstance(birl, Model)
    keys = ('f', 'b')
    assert len(Birl._meta.fields) == len(keys)
    assert set(Birl._meta.fields) == set(keys)

    assert birl.validate(raise_exception=False) is True
    assert dict(birl) == {'f': None, 'b': None}


def test_model_class_builder_empty_data():
    Birl = model_class_builder('Birl', {})
    birl = Birl()

    assert isinstance(birl, Model)


def test_model_builder():
    data = {
        'foo': 'foo',
        'bar': 'bar',
    }
    birl = model_builder(data, recurse=False)
    assert birl.foo == 'foo'
    assert birl.bar == 'bar'
    assert type(birl).__name__ == 'MyModel'


def test_model_builder_class_name():
    data = {
        'foo': 'foo',
        'bar': 'bar',
    }
    birl = model_builder(data, class_name='Birl', recurse=False)
    assert birl.foo == 'foo'
    assert birl.bar == 'bar'
    assert type(birl).__name__ == 'Birl'


def test_model_builder_recurse_false():
    my_model = {'baz': 'baz', 'qux': 'qux'}
    data = {
        'foo': 'foo',
        'bar': 'bar',
        'my_model': my_model,
    }
    birl = model_builder(data, recurse=False)
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
    birl = model_builder(data)
    assert birl.foo == 'foo'
    assert birl.bar == 'bar'
    assert birl.my_model.baz == 'baz'
    assert birl.my_model.qux == 'qux'

    assert type(birl.my_model).__name__ == 'MyModel'
    assert type(birl.my_model) not in (Model, type(birl))


@pytest.mark.parametrize('iterable_class', (tuple, list))
def test_model_builder_recurse_iterable(iterable_class):
    models = iterable_class([{'baz': 'baz', 'qux': 'qux'}, 1, 2])
    data = {
        'foo': 'foo',
        'bar': 'bar',
        'models': models,
    }
    birl = model_builder(data)
    assert birl.foo == 'foo'
    assert birl.bar == 'bar'
    assert birl.models[0].baz == 'baz'
    assert birl.models[0].qux == 'qux'
    assert birl.models[1] == 1
    assert birl.models[2] == 2

    assert isinstance(birl.models[0], Model)
    assert type(birl.models[0]).__name__ == 'NamelessModel'


def test_model_builder_data_keys_with_special_characters():
    data = {
        'foo*bar': 'foobar',
        'baz/qux': 'bazqux',
    }
    birl = model_builder(data)
    assert birl.foo_bar == 'foobar'
    assert birl.baz_qux == 'bazqux'


def test_model_builder_custom_class():
    data = {
        'foo*bar': 'foobar',
        'baz/qux': 'bazqux',
    }
    cls = model_class_builder('Model', data)

    birl = model_builder(data, cls=cls)

    assert isinstance(birl, cls)


def test_model_many_builder():
    element = {
        'foo*bar': 'foobar',
        'baz/qux': 'bazqux',
    }
    model_count = 3
    data = [element] * model_count

    models = model_many_builder(data)

    assert len(models) == model_count
    first = models[0]
    for model in models[1:]:
        assert isinstance(model, type(first))


@pytest.mark.parametrize('iterable', ([], ()))
def test_model_many_builder_empty_iterable(iterable):
    models = model_many_builder(iterable)
    assert isinstance(models, list)
    assert models == []
