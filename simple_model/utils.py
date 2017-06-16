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
