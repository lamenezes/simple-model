import pytest

from simple_model.exceptions import EmptyField, ValidationError
from simple_model import DynamicModel, Model
from simple_model.models import BaseModel

from .conftest import MyModel, MyEmptyModel


@pytest.fixture
def base_model():
    base_model = BaseModel(foo='foo', bar='bar')
    base_model.clean_foo = lambda x: x.strip()
    return base_model


@pytest.fixture
def nested_model():
    grandma = MyModel(foo='foo', bar='bar', qux=' qux ')
    mother = MyModel(foo='foo', bar='bar', baz=grandma, qux=' qux ')
    child = MyModel(foo='foo', bar='bar', baz=mother, qux=' qux ')
    grandma.clean_qux = mother.clean_qux = child.clean_qux = lambda s: s.strip()
    return child


def test_base_model(base_model):
    assert base_model.foo == 'foo'
    assert base_model.bar == 'bar'


def test_base_model_iter(base_model):
    base_model.foo = ' foo '
    base_model.get_fields = lambda: ('foo', 'bar')

    for k, v in base_model:
        assert k == v


def test_base_model_repr(base_model):
    base_model.get_fields = lambda: ('foo', 'bar')

    assert type(base_model).__name__ in repr(base_model)
    assert "foo='foo'" in repr(base_model)
    assert "bar='bar'" in repr(base_model)


def test_base_model_get_fields(base_model):
    with pytest.raises(NotImplementedError):
        base_model.get_fields()


def test_base_model__get_fields(base_model):
    base_model.get_fields = lambda: ('foo', 'bar')

    for field in base_model._get_fields():
        assert field.name in ('foo', 'bar')
        assert isinstance(field, base_model._field_class)
        assert field.allow_empty is True


@pytest.mark.parametrize('value', (False, 0, 'foo', 10, {'foo': 'bar'}, [1]))
def test_base_model_is_empty_false(base_model, value):
    assert base_model.is_empty(value) is False


@pytest.mark.parametrize('value', ('', {}, []))
def test_base_model_is_empty_true(base_model, value):
    assert base_model.is_empty(value) is True


def test_base_model_clean(base_model):
    base_model.foo = ' foo '
    base_model.get_fields = lambda: ('foo', 'bar')

    base_model.clean()

    assert base_model.foo == 'foo'
    assert base_model.bar == 'bar'


def test_base_model_validate_success(base_model):
    base_model.get_fields = lambda: ('foo', 'bar')

    def validate_foo(value):
        if value != 'foo':
            raise ValidationError()

    base_model.validate_foo = validate_foo

    assert base_model.validate(raise_exception=False) is True
    assert base_model.validate() is None


def test_base_model_validate_fail(base_model):
    base_model.foo = 'abc'
    base_model.get_fields = lambda: ('foo', 'bar')

    def validate_foo(value):
        if value != 'foo':
            raise ValidationError()

    base_model.validate_foo = validate_foo

    assert base_model.validate(raise_exception=False) is False
    with pytest.raises(ValidationError):
        base_model.validate()


def test_base_model___eq___equals(base_model):
    other_model = BaseModel(foo='foo', bar='bar')
    other_model.get_fields = base_model.get_fields = lambda: ('foo', 'bar')

    assert base_model == base_model
    assert base_model is base_model

    assert base_model == {'foo': 'foo', 'bar': 'bar'}
    assert base_model == (('foo', 'foo'), ('bar', 'bar'))
    assert base_model == [('foo', 'foo'), ('bar', 'bar')]

    assert base_model is not other_model
    assert base_model == other_model


def test_base_model___eq___not_equals(base_model):
    other_model = BaseModel(foo='bar', bar='foo')
    other_model.get_fields = base_model.get_fields = lambda: ('foo', 'bar')

    assert base_model != other_model
    assert base_model != {}
    assert base_model != ()
    assert base_model != []
    assert base_model != 1
    assert base_model != 'base_model'


def test_model(model):
    assert model.foo == 'foo'
    assert model.bar == 'bar'
    assert model.baz == ''
    assert model.qux == ''
    assert 'foo' in repr(model)
    for k, v in model:
        assert k in model.fields


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


def test_model__get_fields(model):
    for field in model._get_fields():
        assert field.allow_empty is (field.name in model.allow_empty)


def test_model_get_fields():
    class MyGetFieldsModel(MyModel):
        def get_fields(self):
            return super().fields + ('birl',)

    model = MyGetFieldsModel(foo='foo', bar='bar', birl='birl')
    assert model.validate(raise_exception=False)


def test_model_get_fields_without_fields():
    class FieldlessModel(Model):
        pass

    assert FieldlessModel.fields == ()
    with pytest.raises(AssertionError):
        FieldlessModel().get_fields()


def test_model_get_allow_empty():
    class MyGetFieldsModel(MyModel):
        def get_allow_empty(self):
            return super().allow_empty + ('bar',)

    model = MyGetFieldsModel(foo='foo')
    assert model.validate(raise_exception=False)


def test_model_get_allow_empty_without_fields():
    class AllowEmptylessModel(Model):
        fields = ('a', 'b')

    assert AllowEmptylessModel().get_allow_empty() == ()


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


def test_model_clean_nested(nested_model):
    nested_model.clean()

    assert nested_model.qux == 'qux'
    assert nested_model.baz.qux == 'qux'
    assert nested_model.baz.baz.qux == 'qux'


def test_model_iter_clean(model):
    model.bar = ' bar '
    model.clean_bar = lambda f: f.strip()
    model.clean()
    as_dict = dict(model)
    assert as_dict == {'foo': 'foo', 'bar': 'bar', 'baz': '', 'qux': ''}


def test_model_get_fields_invalid():
    with pytest.raises(AssertionError) as exc:
        Model()

    assert 'should include a fields attr' in str(exc)


def test_dynamic_model_get_fields():
    assert DynamicModel().get_fields() == ()

    model = DynamicModel(foo='le foo', bar='le bar')
    fields = model.get_fields()
    assert 'bar' in fields
    assert 'foo' in fields

    model.baz = 'le baz'
    fields = model.get_fields()
    assert 'baz' in fields
    assert len(fields) == 3

    model._private = "it's private!"
    fields = model.get_fields()
    assert '_private' not in fields
    assert len(fields) == 3
