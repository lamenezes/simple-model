from unittest import mock

import pytest

from simple_model.exceptions import EmptyField, ValidationError
from simple_model.fields import ModelField
from simple_model.models import Model

from .conftest import MyModel


class MyValidationError(ValidationError):
    pass


@pytest.fixture
def model_field():
    return ModelField(MyModel, name='bar', default_value='default', type=str, allow_empty=True)


def test_model_field(model_field):
    assert issubclass(model_field.model_class, Model)
    assert model_field.name == 'bar'
    assert model_field.default_value == 'default'
    assert issubclass(str, model_field.type)
    assert model_field.allow_empty is True


@pytest.mark.parametrize('value', (1, '1', [2], ['2']))
def test_model_field_to_python_simple(model_field, value):
    assert model_field.to_python(value) == value


def test_model_field_to_python_nested(model2, model_field):
    assert model_field.to_python(model2) == dict(model2)


@pytest.mark.parametrize('iterable', (list, tuple))
def test_model_field_to_python_nested_iterable(iterable, model_field, model, model2):
    assert model_field.to_python(iterable([model, model2])) == [dict(model), dict(model2)]


@pytest.mark.parametrize('iterable', (list, tuple))
def test_model_field_to_python_iterable_empty(iterable, model_field, model, model2):
    assert model_field.to_python(iterable([])) == []


@pytest.mark.parametrize('iterable', (list, tuple))
def test_model_field_to_python_iterable(iterable, model_field, model, model2):
    assert model_field.to_python(iterable([1, 2, 3])) == [1, 2, 3]


def test_model_field_validate(model, model_field):
    validate = mock.MagicMock(return_value=None)
    model_field._validate = validate

    assert model_field.validate(None, None) is None


@pytest.mark.parametrize('exception', (ValidationError, EmptyField, MyValidationError))
def test_model_field_validate_validation_error(model, model_field, exception):
    validate = mock.MagicMock(side_effect=exception('foo'))
    model_field._validate = validate

    with pytest.raises(exception):
        model_field.validate(None, None)


@pytest.mark.parametrize('blank_value', (None, '', [], {}, ()))
def test_model_field_validate_empty_field(model_field, blank_value):
    model_field.allow_empty = False
    model_field.value = blank_value
    with pytest.raises(EmptyField):
        model_field.validate(None, None)


def test_model_field_clean(model_field):
    model_field._clean = lambda _, s: s.strip()

    assert model_field.clean(None, ' foo ') == 'foo'


def test_model_field_clean_invalid(model, model_field):
    model_field._clean = lambda _, s: s.strip()
    model_field._validate = type(model).validate_foo

    with pytest.raises(ValidationError):
        model_field.clean(None, ' fo ')


def test_model_field_clean_without_clean_method(model_field):
    model_field._clean = None

    assert model_field.clean(None, ' foo ') == ' foo '


def test_model_field_clean_without_clean_method_invalid(model, model_field):
    model_field._clean = None
    model_field._validate = model_field.model_class.validate_foo

    with pytest.raises(ValidationError):
        model_field.clean(None, ' fo ')


def test_model_field_clean_nested(model):
    class MyModel(Model):
        class Meta:
            fields = (
                'foo',
                'bar',
                'baz',
            )

        def clean_foo(self, value):
            return value.strip()

    model = MyModel(foo=' foo ', bar='bar', baz='baz')
    other_model = MyModel(foo='foo', bar='bar', baz=model)

    other_model.clean()

    assert model.foo == 'foo'


def test_model_field_clean_type_conversion(model):
    OtherModel = type(model)
    from typing import Any, List, Tuple

    class TypedModel(Model):
        any: Any
        iterable: List
        model: OtherModel
        models: List[OtherModel]
        number: float
        numbers: List[float]
        string: str
        strings: Tuple[str]

    class Foo:
        def __init__(self, foo):
            pass

    iterable = ['1', 2, '3']
    model = TypedModel(
        any=Foo('toba'),
        iterable=list(iterable),
        model={'foo': 'foo', 'bar': 'bar'},
        models=[{'foo': 'foo', 'bar': 'bar'}],
        number='10',
        numbers=list(iterable),
        string=1,
        strings=tuple(iterable),
    )

    model.clean()
    assert isinstance(model.any, Foo)
    assert isinstance(model.iterable, list)
    assert model.iterable == iterable
    assert isinstance(model.model, TypedModel.model.type)
    assert isinstance(model.models, list)
    for elem in model.models:
        assert isinstance(elem, TypedModel.models.type.__args__[0])
    assert isinstance(model.number, TypedModel.number.type)
    assert isinstance(model.numbers, list)
    for elem in model.numbers:
        assert isinstance(elem, TypedModel.numbers.type.__args__[0])
    assert isinstance(model.string, TypedModel.string.type)
    assert isinstance(model.strings, tuple)
    for elem in model.strings:
        assert isinstance(elem, TypedModel.strings.type.__args__[0])
