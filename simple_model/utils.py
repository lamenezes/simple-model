def capitalize_first(string):
    return string[0].upper() + string[1:]


def camel_case(string):
    string = capitalize_first(string)
    for separator in ('_', '-', ' '):
        if separator not in string:
            continue
        string = ''.join(capitalize_first(substr) for substr in string.split(separator))
    return string
