import pytest
import typing
from datetime import datetime
from unittest import mock

from simple_model import Model
from simple_model.exceptions import EmptyField, ValidationError
from simple_model.fields import ModelField

from .conftest import MyModel


class FooBarModel(Model):
    foo: str
    bar: str

    def validate_foo(self, foo):
        return foo.strip()


class TypedModel(Model):
    boolean = True  # default
    common: typing.Any
    empty = None
    model: FooBarModel
    models: typing.List[FooBarModel]
    number: float  # type constraint
    string: str = 'foobar'  # type constraint + default


class TypelessModel(Model):
    boolean = True
    number = 1.0
    string = 'foobar'


def now():
    return datetime(2019, 6, 9)


class FactoryFieldModel(Model):
    now: datetime = now
    number: float = float
    string = 'foobar'


@pytest.fixture
def model_clean_validate_foo_data():
    return {'foo': 'foo', 'bar': 'bar'}


@pytest.fixture
def model_clean_validate_foo(model_clean_validate_foo_data):
    return FooBarModel(**model_clean_validate_foo_data)


@pytest.fixture
def nested_model():
    class CleanQuxModel(Model):
        foo: str
        bar: str
        baz: typing.Any = None
        qux: str = ''

        def validate_foo(self, value):
            if len(value) != 3:
                raise ValidationError()

        def validate_qux(self, value):
            return value.strip()

    grandma = CleanQuxModel(foo='foo', bar='bar', qux=' qux ')
    mother = CleanQuxModel(foo='foo', bar='bar', baz=grandma, qux=' qux ')
    child = CleanQuxModel(foo='foo', bar='bar', baz=mother, qux=' qux ')
    return child


@pytest.fixture
def many_source():
    return (
        {'foo': '1 foo', 'bar': '1 bar', 'qux': '1 qux'},
        {'foo': '2 foo', 'bar': '2 bar', 'qux': '2 qux'},
        {'foo': '3 foo', 'bar': '3 bar', 'qux': '3 qux'},
    )


@pytest.fixture
def typed_model(model_clean_validate_foo):
    return TypedModel(
        common='common',
        number=6.9,
        model=model_clean_validate_foo,
        models=[model_clean_validate_foo] * 2,
    )


def test_base_model(model):
    assert model.foo == 'foo'
    assert model.bar == 'bar'


@pytest.mark.skip(reason="iter is broken and will be removed on version 2")
def test_base_model_iter(model_clean_validate_foo):
    model_clean_validate_foo.foo = ' foo '

    for k, v in model_clean_validate_foo:
        assert k == v


def test_base_model_repr(model_clean_validate_foo):
    assert type(model_clean_validate_foo).__name__ in repr(model_clean_validate_foo)
    assert "foo='foo'" in repr(model_clean_validate_foo)
    assert "bar='bar'" in repr(model_clean_validate_foo)


def test_base_model__get_fields(model_clean_validate_foo):
    for name, value, descriptor in model_clean_validate_foo._get_fields():
        assert name in ('foo', 'bar')
        assert value in ('foo', 'bar')
        assert isinstance(descriptor, ModelField)


@pytest.mark.parametrize('value', (False, 0, 'foo', 10, {'foo': 'bar'}, [1]))
def test_base_model_is_empty_false(model, value):
    assert model.is_empty(value) is False


@pytest.mark.parametrize('value', ('', {}, []))
def test_base_model_is_empty_true(model, value):
    assert model.is_empty(value) is True


def test_base_model_validate_and_clean(model_clean_validate_foo):
    model_clean_validate_foo.foo = ' foo '

    model_clean_validate_foo.validate()

    assert model_clean_validate_foo.foo == 'foo'
    assert model_clean_validate_foo.bar == 'bar'


def test_base_model_validate_fail(model):
    class MyModel(type(model)):
        foo: str
        bar: str

        def validate_foo(self, value):
            if value != 'foo':
                raise ValidationError()

    my_model = MyModel(foo='abc', bar='bar')

    assert my_model.validate(raise_exception=False) is False
    with pytest.raises(ValidationError):
        my_model.validate()


def test_base_model___eq___equals():
    model = FooBarModel(foo='foo', bar='bar')
    other_model = FooBarModel(foo='foo', bar='bar')

    assert model == model
    assert model is model

    assert model == {'foo': 'foo', 'bar': 'bar'}
    assert model == (('foo', 'foo'), ('bar', 'bar'))
    assert model == [('foo', 'foo'), ('bar', 'bar')]

    assert model is not other_model
    assert model == other_model


def test_base_model___eq___not_equals(model):
    other_model = FooBarModel(foo='bar', bar='foo')

    assert model != other_model
    assert model != {}
    assert model != ()
    assert model != []
    assert model != 1
    assert model != 'model'


def test_model(model):
    assert model.foo == 'foo'
    assert model.bar == 'bar'
    assert model.baz == ''
    assert model.qux == ''
    assert 'foo' in repr(model)
    for k, v in model:
        assert k in model._meta.fields


def test_model__get_fields(model):
    for name, value, descriptor in model._get_fields():
        assert name in model._meta.fields
        assert value == getattr(model, name)
        assert isinstance(descriptor, ModelField)


def test_model_fields_without_fields():
    with pytest.raises(AssertionError):
        class FieldlessModel(Model):
            pass


@pytest.mark.parametrize('value', (False, 0))
def test_model_validate_empty(model, value):
    model.bar = value
    assert model.validate(raise_exception=False) is True


@pytest.mark.parametrize('empty_value', (None, ''))
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


def test_model_validate_nested(nested_model):
    nested_model.baz.foo = ''
    assert nested_model.validate(raise_exception=False) is False

    nested_model.baz.foo = 'foo'
    nested_model.baz.baz.foo = ''
    assert nested_model.validate(raise_exception=False) is False


def test_model_iter_simple(model):
    as_dict_model = {
        'foo': 'foo',
        'bar': 'bar',
        'baz': '',
        'qux': '',
    }
    assert dict(model) == as_dict_model


@pytest.mark.parametrize('iterable', (list, tuple))
def test_model_iter_nested_list(iterable, model, model2):
    other_model = MyModel(foo='foo', bar=iterable([model, model2]), baz=model)
    as_dict = dict(other_model)
    expected = {
        'foo': 'foo',
        'bar': [dict(model), dict(model2)],
        'baz': dict(model),
        'qux': None
    }
    assert as_dict == expected


def test_model_validate_and_clean_without_clean_method(model):
    for field_name in model._meta.fields:
        setattr(model, field_name, field_name)

    model.validate()

    for field_name in model._meta.fields:
        assert getattr(model, field_name) == field_name


def test_model_validate_and_clean():
    fields = ('foo', 'bar', 'baz')

    class TidyModel(Model):
        foo: str
        bar: str
        baz: str

        def validate_foo(self, foo):
            return foo.strip()

        def validate_bar(self, bar):
            return bar.strip()

        def validate_baz(self, baz):
            return baz.strip()

    model = TidyModel(
        foo=' foo ',
        bar=' bar ',
        baz=' baz ',
    )
    model.validate()

    for field_name in fields:
        assert getattr(model, field_name) == field_name


def test_model_validate_and_clean_nested(nested_model):
    nested_model.validate()

    assert nested_model.qux == 'qux'
    assert nested_model.baz.qux == 'qux'
    assert nested_model.baz.baz.qux == 'qux'


def test_model_iter_clean(model):
    class CleanBarMyModel(Model):
        foo: str
        bar: str
        baz = ''
        qux = ''

        def validate_bar(self, value):
            return value.strip()

    model = CleanBarMyModel(foo='foo', bar=' bar ', baz='', qux='')
    model.validate()
    as_dict = dict(model)
    assert as_dict == {'foo': 'foo', 'bar': 'bar', 'baz': '', 'qux': ''}


def test_model_get_fields_invalid():
    with pytest.raises(AssertionError) as exc:
        type('FieldlessModel', (Model,), {})

    assert 'model must define class attributes' in str(exc)


def test_build_many(many_source):
    models = MyModel.build_many(many_source)

    assert len(models) == 3
    assert models[0].foo == '1 foo'
    assert models[1].bar == '2 bar'
    assert models[2].qux == '3 qux'


def test_build_many_empty_iterable():
    assert MyModel.build_many([]) == []


def test_build_many_different_items():
    with pytest.raises(ValueError):
        MyModel.build_many([{'a': 1}, {'b': 2}])


def test_type_model(typed_model, model_clean_validate_foo):
    assert typed_model.number == 6.9
    assert typed_model.boolean is True
    assert typed_model.string == 'foobar'
    assert typed_model.common == 'common'
    assert typed_model.model == model_clean_validate_foo
    assert typed_model.models == [model_clean_validate_foo] * 2


def test_typed_model_clean_type_conversion(
    typed_model, model_clean_validate_foo_data, model_clean_validate_foo
):
    typed_model.common = 'common'
    typed_model.number = '6.9'
    typed_model.string = 6.9
    typed_model.model = model_clean_validate_foo_data
    typed_model.models = [model_clean_validate_foo_data] * 2

    typed_model.validate()

    assert isinstance(typed_model.number, float)
    assert isinstance(typed_model.string, str)
    assert isinstance(typed_model.model, Model)
    assert isinstance(typed_model.models, list)
    for model in typed_model.models:
        assert isinstance(model, Model)


def test_model_inheritance_with_meta_fields(model_clean_validate_foo):
    class SubTypedModel(TypedModel):
        other_string: str
        sub: typing.Any = None

    model = SubTypedModel(
        common='common',
        number=6.9,
        model=model_clean_validate_foo,
        models=[model_clean_validate_foo] * 2,
        other_string='other',
    )

    assert model.boolean
    assert model.common
    assert model.empty is None
    assert model.number
    assert model.string
    assert model.model
    assert model.models
    assert model.other_string
    assert model.sub is None


def test_model_inheritance_without_meta_fields():
    class SuperModel(Model):
        foo: str
        bar: str

    class SubModel(SuperModel):
        foo: str = ''
        bar: int
        baz: str
        qux: str

    model = SubModel(
        bar=10,
        baz='baz',
        qux='qux',
    )
    model.validate()

    assert model.bar
    assert model.baz
    assert model.qux


def test_typeless_model():
    model = TypelessModel()

    assert model.boolean
    assert model.number
    assert model.string


def test_field_factory_model():
    model = FactoryFieldModel(number=6.9)

    assert model.now == now()
    assert model.number == 6.9
    assert model.string == 'foobar'


def test_model_validate_and_clean_invalid_mocked_model(model):
    model.validate = mock.Mock(side_effect=ValidationError)

    with pytest.raises(ValidationError):
        model.validate()


def test_model_validate_and_clean_invalid_model_validate_called_after_clean(model):
    class MyModel(Model):
        foo: str
        bar: str

        def validate_foo(self, foo):
            foo = foo.strip()
            if len(foo) != 3:
                raise ValidationError()
            return foo

    model = MyModel(foo='fo ', bar='bar')
    with pytest.raises(ValidationError):
        model.validate()
