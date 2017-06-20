from typing import Any, Dict, List

from .model import Model
from .utils import camel_case, coerce_to_alpha, snake_case


def model_class_builder(class_name: str, data: Any) -> type:
    keys = data.keys() or ('',)
    attrs = {
        'allow_empty': '__all__',
        'fields': tuple(keys),
    }
    new_class = type(class_name, (Model,), attrs)
    return new_class


def model_builder(
    data: Any, class_name: str='MyModel', recurse: bool=True,
    snake_case_keys: bool=True, alpha_keys: bool=True,
) -> Model:

    clean_funcs = []
    if snake_case_keys:
        clean_funcs.append(snake_case)

    if alpha_keys:
        clean_funcs.append(coerce_to_alpha)

    data = {func(key): value for key, value in data.items() for func in clean_funcs}
    cls = model_class_builder(class_name, data)
    instance = cls(**data)

    if not recurse:
        return instance

    for field in instance._get_fields():
        if isinstance(field.value, Dict):
            field.value = model_builder(field.value, camel_case(field.name))
        elif isinstance(field.value, (List, tuple)):
            field.value = list(field.value)

            for i, value in enumerate(field.value):
                if not isinstance(value, Dict):
                    continue
                field.value[i] = model_builder(value, 'NamelessModel')

            field_class = field.value.__class__
            field.value = field_class(field.value)

    return instance
