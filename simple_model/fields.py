from typing import Any, List, Tuple

from .exceptions import EmptyField

PARAMETRIZED_GENERICS = (List, Tuple)

Unset = type('Unset', (), {})


class ModelField:
    def __init__(self, model_class, name, default_value=Unset, type=None):
        self.model_class = model_class
        self.name = name
        self._default_value = default_value
        self.type = type

        try:
            self._validate = getattr(model_class, 'validate_{}'.format(name))
        except AttributeError:
            self._validate = None

    @property
    def default_value(self):
        return self._default_value if self._default_value is not Unset else None

    def convert_to_type(self, instance, value, field_type=None):
        field_type = field_type or self.type
        if not field_type or field_type is Any or value is None:
            return value

        if not issubclass(field_type, PARAMETRIZED_GENERICS) and type(value) is field_type:
            return value

        from simple_model.models import Model
        if issubclass(field_type, Model) and isinstance(value, Model):
            assert type(value) is field_type, ('Field of type {} received an object of invalid '
                                               'type {}').format(field_type, type(value))

        if issubclass(field_type, Model):
            return field_type(**value)

        if issubclass(field_type, (list, tuple)):
            try:
                element_field_type = field_type.__args__[0] if field_type.__args__ else None
            except AttributeError:
                element_field_type = None

            iterable_field_type = tuple if issubclass(field_type, tuple) else list
            if not element_field_type:
                return iterable_field_type(value)

            values = []
            for elem in value:
                if not isinstance(elem, element_field_type):
                    elem = self.convert_to_type(instance, elem, field_type=element_field_type)
                values.append(elem)

            return iterable_field_type(values)

        return field_type(value)

    def validate(self, instance, value):
        if self._default_value is Unset and self.model_class.is_empty(value):
            raise EmptyField(self.name)

        if isinstance(value, (list, tuple)):
            for elem in value:
                try:
                    elem.validate()
                except AttributeError:
                    continue

        if self._validate:
            return self._validate(instance, value)

        try:
            value.validate()
        except AttributeError:
            return value

        return value

    def to_python(self, value):
        if not value:
            return value

        from .converters import to_dict
        if not isinstance(value, (list, tuple)):
            try:
                return to_dict(value)
            except (TypeError, ValueError):
                return value

        python_value = []
        for elem in value:
            try:
                elem = to_dict(elem)
            except (TypeError, ValueError):
                pass
            python_value.append(elem)

        value_cls = type(python_value)
        return python_value if issubclass(value_cls, list) else value_cls(python_value)
