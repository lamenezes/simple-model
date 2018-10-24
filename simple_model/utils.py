import inspect
import re
import typing

NOT_WORD = re.compile(r'\W')
SNAKE_CASE = re.compile('([a-z0-9])([A-Z])')
SNAKE_CASE_AUX = re.compile('(.)([A-Z][a-z]+)')
_PRIVATE_ATTR_RE = re.compile(r'_[\w\d]+__[\w\d]')


def capitalize_first(string: str) -> str:
    return string[0].upper() + string[1:] if string != '' else string


def camel_case(string: str) -> str:
    string = capitalize_first(string)
    for separator in ('_', '-', ' '):
        if separator not in string:
            continue
        string = ''.join(capitalize_first(substr) for substr in string.split(separator))
    return string


def coerce_to_alpha(string: str) -> str:
    return NOT_WORD.sub('_', string)


def snake_case(string: str) -> str:
    aux = SNAKE_CASE_AUX.sub(r'\1_\2', string)
    return SNAKE_CASE.sub(r'\1_\2', aux).lower()


def is_not_special_object(obj):
    return not any((
        inspect.isclass(obj),
        inspect.ismethod(obj),
        inspect.isfunction(obj),
        inspect.isgeneratorfunction(obj),
        inspect.isgenerator(obj),
        inspect.isroutine(obj),
        isinstance(obj, property),
    ))


def getkey(d: dict, key: typing.Any):
    return d[key]


def remove_private_keys(d: dict) -> dict:
    return {
        k: v for k, v in d.items() if not k.startswith('__')
    }


def is_private_attribute(name):
    return _PRIVATE_ATTR_RE.match(name) is not None
