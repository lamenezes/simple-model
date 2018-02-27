from typing import Any, List

from .models import Model
from .utils import camel_case, coerce_to_alpha, snake_case


def model_class_builder(class_name: str, data: Any) -> type:
    keys = data.keys() or ('',)
    attrs = {
        'allow_empty': tuple(keys),
        'fields': tuple(keys),
    }
    Meta = type('Meta', (), attrs)
    new_class = type(class_name, (Model,), {'Meta': Meta})
    return new_class


def model_builder(
    data: Any, class_name: str='MyModel', cls: type=None, recurse: bool=True,
    snake_case_keys: bool=True, alpha_keys: bool=True,
) -> Model:

    clean_funcs = []
    if snake_case_keys:
        clean_funcs.append(snake_case)

    if alpha_keys:
        clean_funcs.append(coerce_to_alpha)

    data = {func(key): value for key, value in data.items() for func in clean_funcs}
    if not cls:
        cls = model_class_builder(class_name, data)
    instance = cls(**data)

    if not recurse:
        return instance

    # dafuq
    for name, value, descriptor in instance._get_fields():
        if isinstance(value, dict):
            value = model_builder(value, camel_case(name))
        elif isinstance(value, (list, tuple)):
            value = list(value)

            for i, elem in enumerate(value):
                if not isinstance(elem, dict):
                    continue
                value[i] = model_builder(elem, 'NamelessModel')

            field_class = value.__class__
            value = field_class(value)

        setattr(instance, name, value)

    return instance


def model_many_builder(
    data: list, class_name: str='MyModel', cls: type=None, recurse: bool=True,
    snake_case_keys: bool=True, alpha_keys: bool=True,
) -> List[Model]:

    if len(data) == 0:
        return []

    first = data[0]
    cls = model_class_builder(class_name, first)
    models = []
    for element in data:
        model = model_builder(
            data=element,
            class_name=class_name,
            cls=cls,
            recurse=recurse,
            snake_case_keys=snake_case_keys,
            alpha_keys=alpha_keys,
        )
        models.append(model)

    return models
