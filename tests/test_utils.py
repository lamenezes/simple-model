from simple_model.utils import camel_case, capitalize_first, coerce_to_alpha


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
