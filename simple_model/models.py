from typing import Any, Callable, Iterable, Iterator, Tuple, Union

from .base import BaseModel
from .exceptions import ValidationError
from .fields import ModelField
from .utils import getkey


class Model(metaclass=BaseModel):
    def __init__(self, **kwargs):
        self._validation_count = 0

        for field_name in self._meta.fields:
            descriptor = self._meta.descriptors[field_name]

            field_value = kwargs.get(field_name)
            default = descriptor.default_value
            factory = default if isinstance(default, Callable) else None
            field_value = factory() if factory and not field_value else kwargs.get(field_name, default)

            setattr(self, field_name, field_value)

        self.__post_init__(**kwargs)

    def __post_init__(self, **kwargs):
        pass

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Model):
            other_fields = list(other._get_fields())
            get_func = getattr
        else:
            try:
                other = dict(other)
            except (ValueError, TypeError):
                return NotImplemented
            other_fields = other
            get_func = getkey  # type: ignore

        self_fields = list(self._get_fields())
        if len(self_fields) != len(other_fields):
            return False

        for name, _ in self_fields:
            value = getattr(self, name)
            try:
                if value != get_func(other, name):
                    return False
            except AttributeError:
                return False

        return True

    def __repr__(self) -> str:
        attrs = ', '.join(
            '{name}={value!r}'.format(name=name, value=getattr(self, name))
            for name, _ in self._get_fields()
        )
        return '{class_name}({attrs})'.format(class_name=type(self).__name__, attrs=attrs)

    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except AttributeError:
            descriptor = self._meta.descriptors.get(name)
            if descriptor and not descriptor.is_property:
                raise

    def _get_fields(self) -> Iterator[Tuple[str, ModelField]]:
        return (
            (field_name, self._meta.descriptors[field_name])  # type: ignore
            for field_name in self._meta.fields  # type: ignore
        )

    @classmethod
    def build_many(cls, source: Iterable) -> list:
        if cls.is_empty(source):
            return []

        keys_sets = [d.keys() for d in source]
        for key_set in keys_sets:
            if key_set ^ keys_sets[0]:
                raise ValueError('All elements in source should have the same keys')

        return [cls(**item) for item in source]

    @staticmethod
    def is_empty(value: Any) -> bool:
        if value == 0 or value is False:
            return False
        return not bool(value)

    def convert_fields(self):
        for name, descriptor in self._get_fields():
            if descriptor.is_property:
                continue

            value = getattr(self, name)
            new_value = descriptor.convert_to_type(self, value)
            setattr(self, name, new_value)

    def validate(self, raise_exception: bool = True) -> Union[None, bool]:
        self._validation_count += 1
        self.convert_fields()

        for name, descriptor in self._get_fields():
            if descriptor.is_property and descriptor._validate is None:
                continue

            value = getattr(self, name)
            try:
                value = descriptor.validate(self, value)
            except ValidationError:
                if raise_exception:
                    raise
                return False

            setattr(self, name, value)

        return None if raise_exception else True

    def as_dict(self):
        """
        Returns the model as a dict
        """
        from .converters import to_dict
        return to_dict(self)
