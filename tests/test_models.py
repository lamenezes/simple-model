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


def test_base_model___eq___not_equals_same_model():
    model = FooBarModel(foo='bar', bar='foo')
    other_model = FooBarModel(foo='fool', bar='bare')

    assert model != other_model


def test_base_model___eq___not_equals_different_models_same_field_qty():
    class OtherModel(Model):
        baz: str
        qux: str

    model = FooBarModel(foo='bar', bar='foo')
    other_model = OtherModel(baz='fool', qux='bare')

    assert model != other_model


def test_model(model):
    assert model.foo == 'foo'
    assert model.bar == 'bar'
    assert model.baz == ''
    assert model.qux == ''
    assert 'foo' in repr(model)


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


def test_model_validate_and_clean_model_list(model):
    class MyModel(Model):
        foo: str
        bar: typing.List = []

        def validate_foo(self, foo):
            return foo.strip()

    model = MyModel(foo='foo ')
    model2 = MyModel(foo='foo ')
    model3 = MyModel(
        foo='foo ',
        bar=[model, model2],
    )
    model3.validate()

    assert model3.foo == 'foo'
    assert model2.foo == 'foo'
    assert model.foo == 'foo'


@pytest.mark.parametrize('empty_value', ('', None))
def test_wtf_validate(empty_value):
    class MyModel(Model):
        foo: str = empty_value

    model = MyModel()
    assert model.validate() is None  # does not raise EmptyField


def test_model_validate_and_clean_type_conversion(model):
    OtherModel = type(model)

    class TypedModel(Model):
        any: typing.Any
        iterable: typing.List
        model: OtherModel
        model_as_dict: OtherModel
        models: typing.List[OtherModel]
        number: float
        numbers: typing.List[float]
        string: str
        strings: typing.Tuple[str]
        string_none: str = None

    class Foo:
        def __init__(self, foo):
            pass

    model_data = {'foo': 'foo', 'bar': 'bar'}
    iterable = ['1', 2, '3']
    model = TypedModel(
        any=Foo('toba'),
        iterable=list(iterable),
        model=OtherModel(**model_data),
        model_as_dict=model_data,
        models=[model_data],
        number='10',
        numbers=list(iterable),
        string=1,
        strings=tuple(iterable),
    )

    model.validate()
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
    assert model.string_none is None


def test_field_conversion_model_type_conflict(model):
    OtherModel = type(model)

    class MyModel(Model):
        field: OtherModel

    my_model = MyModel(field=model)
    invalid_model = MyModel(field=my_model)
    with pytest.raises(AssertionError):
        invalid_model.validate()
