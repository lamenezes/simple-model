from typing import Any, Dict, List

from .model import Model
from .utils import camel_case


def model_class_builder(name: str, data: Any) -> type:
    attrs = {
        'allow_empty': '__all__',
        'fields': tuple(data.keys()),
    }
    new_class = type(name, (Model,), attrs)
    return new_class


def model_builder(name: str, data: Any, recurse: bool=True) -> Model:
    parent_class = model_class_builder(name, data)
    instance = parent_class(**data)

    if not recurse:
        return instance

    for field in instance._get_fields():
        if isinstance(field.value, Dict):
            field.value = model_builder(camel_case(field.name), field.value)
        elif isinstance(field.value, (List, tuple)):
            field.value = list(field.value)

            for i, value in enumerate(field.value):
                if not isinstance(value, Dict):
                    continue
                field.value[i] = model_builder('NamelessModel', value)

            field_class = field.value.__class__
            field.value = field_class(field.value)

    return instance
