import typing
from typing import Any, Callable, Iterable, Iterator, Tuple, Union

from .exceptions import ValidationError
from .fields import ModelField, Unset
from .utils import is_not_special_object, is_private_attribute, getkey


class BaseModel(type):
    _field_class = ModelField

    @classmethod
    def _get_class_attributes(cls, new_class, parents):
        attrs = set(
            k for k, v in vars(new_class).items()
            if not (k[:2] == '__' and k[-2:] == '__') and is_not_special_object(v) and not is_private_attribute(k)
        )

        if not parents:
            return attrs

        return cls._get_class_attributes(parents[0], parents[1:]) | attrs

    @classmethod
    def _get_fields(cls, attrs, hints):
        fields = set(hints) | attrs
        fields.discard('Meta')
        return tuple(field for field in fields if not is_private_attribute(field))

    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__

        # do not perform initialization for Model class
        # only initialize Model subclasses
        parents = [base for base in bases if isinstance(base, BaseModel)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        new_class = super_new(cls, name, bases, attrs, **kwargs)
        meta = type('Meta', (), {})

        hints = typing.get_type_hints(new_class)
        attrs = cls._get_class_attributes(new_class, parents)
        assert hints or attrs, '{} model must define class attributes'.format(new_class.__name__)
        meta.fields = cls._get_fields(attrs, hints)
        meta.descriptors = {}

        for field_name in meta.fields:
            field_type = hints.get(field_name) if hints else None
            default_value = getattr(new_class, field_name, Unset)
            field = ModelField(
                model_class=new_class,
                name=field_name,
                default_value=default_value,
                type=field_type,
            )
            meta.descriptors[field_name] = field

        new_class._meta = meta

        return new_class


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
