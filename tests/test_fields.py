import typing
from unittest import mock

import pytest

from simple_model.converters import to_dict
from simple_model.exceptions import EmptyField, ValidationError
from simple_model.fields import ModelField, Unset
from simple_model.models import Model

from .conftest import MyModel


class MyValidationError(ValidationError):
    pass


@pytest.fixture
def model_field():
    return ModelField(MyModel, name='bar', default_value='default', type=str)


@pytest.fixture
def empty_model_field():
    return ModelField(MyModel, name='bar', type=str)


@pytest.fixture
def typeless_model_field():
    return ModelField(MyModel, name='bar')


def test_model_field(model_field):
    assert issubclass(model_field.model_class, Model)
    assert model_field.name == 'bar'
    assert model_field.default_value == 'default'
    assert issubclass(str, model_field.type)


def test_empty_model_field_default_value(empty_model_field):
    assert empty_model_field._default_value is Unset
    assert empty_model_field.default_value is None


@pytest.mark.parametrize('value', (1, '1', [2], ['2']))
def test_model_field_to_python_simple(model_field, value):
    assert model_field.to_python(value) == value


def test_model_field_to_python_nested(model2, model_field):
    model2.validate()
    assert model_field.to_python(model2) == to_dict(model2)


@pytest.mark.parametrize('iterable', (list, tuple))
def test_model_field_to_python_nested_iterable(iterable, model_field, model, model2):
    model.validate()
    model2.validate()
    assert model_field.to_python(iterable([model, model2])) == [to_dict(model), to_dict(model2)]


@pytest.mark.parametrize('iterable', (list, tuple))
def test_model_field_to_python_iterable_empty(iterable, model_field, model, model2):
    assert model_field.to_python(iterable([])) == iterable()


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
def test_model_field_validate_empty_field(empty_model_field, blank_value):
    empty_model_field.value = blank_value
    with pytest.raises(EmptyField):
        empty_model_field.validate(None, None)


def test_model_field_validate_and_clean(model_field):
    model_field._validate = lambda _, s: s.strip()

    assert model_field.validate(None, ' foo ') == 'foo'


def test_model_field_validate_and_clean_clean_nested(model):
    class MyModel(Model):
        foo: str
        bar: str
        baz: typing.Any

        def validate_foo(self, value):
            return value.strip()

    model = MyModel(foo=' foo ', bar='bar', baz='baz')
    other_model = MyModel(foo='foo', bar='bar', baz=model)

    other_model.validate()

    assert model.foo == 'foo'


def test_model_field_convert_to_type_unset(typeless_model_field):
    value = 'valuable'

    assert typeless_model_field.convert_to_type(None, value) is value

    typeless_model_field.type = typing.Any
    assert typeless_model_field.convert_to_type(None, value) is value

    assert typeless_model_field.convert_to_type(None, value, field_class=None) is value

    assert typeless_model_field.convert_to_type(None, value, field_class=typing.Any) is value


@pytest.mark.parametrize('value', (1, '1'))
def test_model_field_convert_to_type_union(typeless_model_field, value):
    assert typeless_model_field.convert_to_type(None, value, field_class=typing.Union[int, str]) is value


def test_model_field_convert_to_type_union_invalid(typeless_model_field):
    value = dict()
    with pytest.raises(AssertionError) as exc_info:
        typeless_model_field.convert_to_type(None, value, field_class=typing.Union[int, str])

    assert str(exc_info.value) == "Field of type (<class 'int'>, <class 'str'>) received an object of invalid type <class 'dict'>"


def test_model_field_convert_to_type_value_has_correct_type(model_field):
    value = 'valuable'

    assert model_field.convert_to_type(None, value) is value


def test_model_field_convert_to_type_invalid_model_type(model_field):
    model_field.type = Model
    value = MyModel()

    with pytest.raises(AssertionError):
        model_field.convert_to_type(None, value)


def test_model_field_convert_to_type_model_type(model_field):
    model_field.type = MyModel
    value = {}

    model = model_field.convert_to_type(None, value)

    assert isinstance(model, MyModel)


def test_model_field_convert_to_type(model_field):
    value = 1

    assert model_field.convert_to_type(None, value) == '1'


@pytest.mark.parametrize('iterable_type, iterable_cls', (
    (typing.List, list),
    (typing.Tuple, tuple),
))
def test_model_field_convert_to_type_iterable_without_type(iterable_type, iterable_cls, model_field):
    model_field.type = iterable_type
    value = iterable_cls([1, 2])

    assert model_field.convert_to_type(None, value) == value


@pytest.mark.parametrize('iterable_type, iterable_cls', (
    (typing.List[str], list),
    (typing.Tuple[str], tuple),
))
def test_model_field_convert_to_type_iterable_typed(iterable_type, iterable_cls, model_field):
    model_field.type = iterable_type
    value = iterable_cls([1, 2])

    assert model_field.convert_to_type(None, value) == iterable_cls(['1', '2'])


@pytest.mark.parametrize('iterable_type', (list, tuple))
def test_model_field_convert_to_type_iterable_generic(iterable_type, model_field):
    model_field.type = iterable_type
    value = iterable_type([1, 2])

    assert model_field.convert_to_type(None, value) == value


@pytest.mark.parametrize('iterable_type, iterable_cls', (
    (typing.List[int], list),
    (typing.Tuple[int], tuple),
))
def test_model_field_convert_to_type_iterable_same_type(iterable_type, iterable_cls, model_field):
    model_field.type = iterable_type
    value = iterable_cls([1, 2])

    assert model_field.convert_to_type(None, value) == value
