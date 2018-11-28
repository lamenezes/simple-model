from typing import Any, List, Union, Tuple, TypeVar

from .exceptions import EmptyField

PARAMETRIZED_GENERICS = (List, Tuple)

Unset = type('Unset', (), {})


class ModelField:
    def __init__(self, model_class, name, default_value=Unset, type=None):
        self.model_class = model_class
        self.name = name
        self._default_value = default_value
        self._type = type
        self.is_property = isinstance(getattr(model_class, name, None), property)

        try:
            self._validate = getattr(model_class, 'validate_{}'.format(name))
        except AttributeError:
            self._validate = None

    def __repr__(self):
        return (f'ModelField(model_class={self.model_class!r}, name={self.name!r}, '
                f'default_value={self._default_value!r}, type={self._type!r})')

    @property
    def default_value(self):
        return self._default_value if self._default_value is not Unset else None

    @property
    def types(self):
        try:
            return self._type.__args__ or []
        except AttributeError:
            return [self._type]

    @property
    def allow_empty(self):
        return type(None) in self.types or self._default_value is not Unset

    def _split_class_and_type(self, type_):
        try:
            return type_.__origin__, type_
        except AttributeError:
            return type_, None

    def convert_to_type(self, instance, value, field_class=None):
        field_class = field_class or self._type
        field_class, field_type = self._split_class_and_type(field_class)

        if not field_class or field_class is Any or value is None or self.is_property:
            return value

        if field_class is Union:
            assert issubclass(type(value), field_type.__args__), (
                'Field of type {} received an object of invalid type {}').format(
                    field_type.__args__, type(value))

            return value

        if not issubclass(field_class, PARAMETRIZED_GENERICS) and type(value) is field_class:
            return value

        from simple_model.models import Model
        if issubclass(field_class, Model) and isinstance(value, Model):
            assert type(value) is field_class, ('Field of type {} received an object of invalid '
                                                'type {}').format(field_class, type(value))

        if issubclass(field_class, Model):
            return field_class(**value)

        if issubclass(field_class, (list, tuple)):
            try:
                element_field_class = field_type.__args__[0] if field_type.__args__ else None
            except AttributeError:
                element_field_class = None

            # if iterable value is a type var refrain from casting to avoid converting to a type
            # the user may not want , e.g.
            # T = TypeVar('T', str, bytes)
            # class Model:
            #    t: T
            # what's the correct type to convert here? str? bytes? for now there's no conversion
            if isinstance(element_field_class, TypeVar):
                element_field_class = None

            iterable_field_class = tuple if issubclass(field_class, tuple) else list
            if not element_field_class:
                return iterable_field_class(value)

            values = []
            for elem in value:
                if not isinstance(elem, element_field_class):
                    elem = self.convert_to_type(instance, elem, field_class=element_field_class)
                values.append(elem)

            return iterable_field_class(values)

        if isinstance(value, field_class):
            return value

        return field_class(value)

    def validate(self, instance, value):
        if not self.allow_empty and self.model_class.is_empty(value):
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
