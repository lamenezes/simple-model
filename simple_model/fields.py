from typing import Any, List, Tuple

from .exceptions import EmptyField

PARAMETRIZED_GENERICS = (List, Tuple)


class ModelField:
    def __init__(self, model_class, name, default_value=None, type=None, allow_empty=False):
        self.model_class = model_class
        self.name = name
        self.default_value = default_value
        self.type = type
        self.allow_empty = allow_empty

        try:
            self._validate = getattr(model_class, 'validate_{}'.format(name))
        except AttributeError:
            self._validate = None

        try:
            self._clean = getattr(model_class, 'clean_{}'.format(name))
        except AttributeError:
            self._clean = None

    def convert_to_type(self, instance, value, type=None):
        type = type or self.type
        if not type or type is Any:
            return value

        if not issubclass(type, PARAMETRIZED_GENERICS) and isinstance(value, type):
            return value

        from simple_model.models import Model
        if issubclass(type, Model):
            return type(**value)

        if issubclass(type, (list, tuple)):
            element_type = type.__args__[0] if type.__args__ else None
            if not element_type:
                return value

            values = []
            for elem in value:
                if not isinstance(elem, element_type):
                    elem = self.convert_to_type(instance, elem, type=element_type)
                values.append(elem)

            iterable_type = tuple if issubclass(type, tuple) else list
            return iterable_type(values)

        return type(value)

    def clean(self, instance, value):
        value = self.convert_to_type(instance, value)
        clean_value = value if not self._clean else self._clean(instance, value)

        try:
            value.clean()
        except AttributeError:
            pass

        self.validate(instance, value)
        return clean_value

    def validate(self, instance, value):
        if not self.allow_empty and self.model_class.is_empty(value):
            raise EmptyField(self.name)

        if self._validate:
            return self._validate(instance, value)

        try:
            value.validate()
        except AttributeError:
            return

    def to_python(self, value):
        if isinstance(value, (list, tuple)):
            python_value = []
            for elem in value:
                try:
                    elem = dict(elem)
                except (TypeError, ValueError):
                    pass
                python_value.append(elem)
            return python_value

        if not value:
            return value

        try:
            return dict(value)
        except (TypeError, ValueError):
            return value
