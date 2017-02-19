from simple_model.utils import camel_case


def test_utils_camel_case():
    assert camel_case('foo') == 'Foo'
    assert camel_case('foo_bar_baz') == 'FooBarBaz'
    assert camel_case('foo-bar_baz') == 'FooBarBaz'
    assert camel_case('foobarbaz') == 'Foobarbaz'
    assert camel_case('fooBarBaz') == 'FooBarBaz'
    assert camel_case('foo bar baz') == 'FooBarBaz'
    assert camel_case('foo Bar-baz') == 'FooBarBaz'
