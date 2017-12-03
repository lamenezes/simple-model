import pytest

from simple_model.exceptions import EmptyField, ValidationError
from simple_model import DynamicModel, Model
from simple_model.fields import ModelField

from .conftest import MyModel, MyEmptyModel


class MyFooBarModel(Model):
    class Meta:
        fields = ('foo', 'bar')

    def clean_foo(self, foo):
        return foo.strip()


@pytest.fixture
def model_clean_validate_foo(model):
    return MyFooBarModel(foo='foo', bar='bar')


@pytest.fixture
def nested_model():
    grandma = MyModel(foo='foo', bar='bar', qux=' qux ')
    mother = MyModel(foo='foo', bar='bar', baz=grandma, qux=' qux ')
    child = MyModel(foo='foo', bar='bar', baz=mother, qux=' qux ')
    grandma.clean_qux = mother.clean_qux = child.clean_qux = lambda s: s.strip()
    return child


@pytest.fixture
def many_source():
    return (
        {'foo': '1 foo', 'bar': '1 bar', 'qux': '1 qux'},
        {'foo': '2 foo', 'bar': '2 bar', 'qux': '2 qux'},
        {'foo': '3 foo', 'bar': '3 bar', 'qux': '3 qux'},
    )


def test_base_model(model):
    assert model.foo == 'foo'
    assert model.bar == 'bar'


def test_base_model_iter(model_clean_validate_foo):
    model_clean_validate_foo.foo = ' foo '

    for k, v in model_clean_validate_foo:
        assert k == v


def test_base_model_repr(model_clean_validate_foo):
    assert type(model_clean_validate_foo).__name__ in repr(model_clean_validate_foo)
    assert "foo='foo'" in repr(model_clean_validate_foo)
    assert "bar='bar'" in repr(model_clean_validate_foo)


def test_base_model__get_fields(model_clean_validate_foo):
    for field in model_clean_validate_foo._get_fields():
        assert field.name in ('foo', 'bar')
        assert isinstance(field, ModelField)
        assert field.allow_empty is False


@pytest.mark.parametrize('value', (False, 0, 'foo', 10, {'foo': 'bar'}, [1]))
def test_base_model_is_empty_false(model, value):
    assert model.is_empty(value) is False


@pytest.mark.parametrize('value', ('', {}, []))
def test_base_model_is_empty_true(model, value):
    assert model.is_empty(value) is True


def test_base_model_clean(model_clean_validate_foo):
    model_clean_validate_foo.foo = ' foo '

    model_clean_validate_foo.clean()

    assert model_clean_validate_foo.foo == 'foo'
    assert model_clean_validate_foo.bar == 'bar'


def test_base_model_validate_success(model):
    model.get_fields = lambda: ('foo', 'bar')

    def validate_foo(value):
        if value != 'foo':
            raise ValidationError()

    model.validate_foo = validate_foo

    assert model.validate(raise_exception=False) is True
    assert model.validate() is None


def test_base_model_validate_fail(model):
    model.foo = 'abc'
    model.get_fields = lambda: ('foo', 'bar')

    def validate_foo(value):
        if value != 'foo':
            raise ValidationError()

    model.validate_foo = validate_foo

    assert model.validate(raise_exception=False) is False
    with pytest.raises(ValidationError):
        model.validate()


def test_base_model___eq___equals(model):
    other_model = MyFooBarModel(foo='foo', bar='bar')
    other_model.get_fields = model.get_fields = lambda: ('foo', 'bar')

    assert model == model
    assert model is model

    assert model == {'foo': 'foo', 'bar': 'bar'}
    assert model == (('foo', 'foo'), ('bar', 'bar'))
    assert model == [('foo', 'foo'), ('bar', 'bar')]

    assert model is not other_model
    assert model == other_model


def test_base_model___eq___not_equals(model):
    other_model = MyFooBarModel(foo='bar', bar='foo')
    other_model.get_fields = model.get_fields = lambda: ('foo', 'bar')

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
        assert field.allow_empty is (field.name in model._meta.allow_empty)


def test_model_get_fields():
    class MyGetFieldsModel(MyModel):
        def get_fields(self):
            return self._meta.fields + ('birl',)

    model = MyGetFieldsModel(foo='foo', bar='bar', birl='birl')
    assert model.validate(raise_exception=False)


def test_model_get_fields_without_fields():
    class FieldlessModel(Model):
        pass

    assert FieldlessModel._meta.fields == ()
    with pytest.raises(AssertionError):
        FieldlessModel().get_fields()


def test_model_get_allow_empty():
    class MyGetFieldsModel(MyModel):
        def get_allow_empty(self):
            return self._meta.allow_empty + ('bar',)

    model = MyGetFieldsModel(foo='foo')
    assert model.validate(raise_exception=False)


def test_model_get_allow_empty_without_fields():
    class AllowEmptylessModel(Model):
        class Meta:
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
    for field_name in model._meta.fields:
        setattr(model, field_name, field_name)

    model.clean()

    for field_name in model._meta.fields:
        assert getattr(model, field_name) == field_name


def test_model_clean(model):
    for field_name in model._meta.fields:
        setattr(model, field_name, ' {} '.format(field_name))
        setattr(model, 'clean_{}'.format(field_name), lambda s: s.strip())

    model.clean()

    for field_name in model._meta.fields:
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
    FieldlessModel = type('FieldlessModel', (Model,), {})
    with pytest.raises(AssertionError) as exc:
        FieldlessModel()

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
