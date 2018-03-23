import pytest

from simple_model import to_dict


def test_model_to_dict_invalid_argument():
    with pytest.raises(TypeError):
        to_dict('')


def test_model_to_dict_model_not_validated(model):
    with pytest.raises(AssertionError):
        to_dict(model)


def test_model_to_dict_simple(model):
    as_dict_model = {
        'foo': 'foo',
        'bar': 'bar',
        'baz': '',
        'qux': '',
    }
    model.validate()

    assert to_dict(model) == as_dict_model


@pytest.mark.parametrize('iterable', (list, tuple))
def test_model_to_dict_nested_list(iterable, model, model2):
    model_class = type(model)
    other_model = model_class(foo='foo', bar=iterable([model, model2]), baz=model)
    other_model.validate()

    as_dict = to_dict(other_model)

    expected = {
        'foo': 'foo',
        'bar': [to_dict(model), to_dict(model2)],
        'baz': to_dict(model),
        'qux': None
    }
    assert as_dict == expected
