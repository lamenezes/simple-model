import inspect
import re


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
    return re.sub(r'\W', '_', string)


def snake_case(string: str) -> str:
    aux = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', aux).lower()


def is_not_special_object(obj):
    return not any((
        inspect.isclass(obj),
        inspect.ismethod(obj),
        inspect.isfunction(obj),
        inspect.isgeneratorfunction(obj),
        inspect.isgenerator(obj),
        inspect.isroutine(obj),
        isinstance(obj, property)
    ))
