import pytest

from simple_model.utils import camel_case, capitalize_first, coerce_to_alpha, getkey, snake_case, remove_private_keys


def test_utils_capitalize_first():
    assert capitalize_first('') == ''
    assert capitalize_first('foobar') == 'Foobar'
    assert capitalize_first('foobar_*/') == 'Foobar_*/'


def test_utils_camel_case():
    assert camel_case('foo') == 'Foo'
    assert camel_case('foo_bar_baz') == 'FooBarBaz'
    assert camel_case('foo-bar_baz') == 'FooBarBaz'
    assert camel_case('foobarbaz') == 'Foobarbaz'
    assert camel_case('fooBarBaz') == 'FooBarBaz'
    assert camel_case('foo bar baz') == 'FooBarBaz'
    assert camel_case('foo Bar-baz') == 'FooBarBaz'
    assert camel_case('') == ''


def test_coerce_to_alpha():
    assert coerce_to_alpha('') == ''
    assert coerce_to_alpha('foo-bar.baz') == 'foo_bar_baz'


def test_snake_case():
    assert snake_case('') == ''
    assert snake_case('foo') == 'foo'
    assert snake_case('FooBarBazQux') == 'foo_bar_baz_qux'
    assert snake_case('FooBarBaz___') == 'foo_bar_baz___'


def test_getkey():
    d = {'foo': 'bar'}
    assert getkey(d, 'foo') == d['foo']

    with pytest.raises(KeyError):
        getkey(d, 'toba')


def test_remove_private_keys():
    d = {
        'public': 'public',
        '_protected': '_protected',
        '__private': '__private',
        '___what': '___what',
    }

    assert list(remove_private_keys(d)) == ['public', '_protected']
