import typing
from typing import Any, Callable, Iterable, Iterator, Tuple, Union

from .exceptions import ValidationError
from .fields import ModelField
from .utils import is_not_special_object


class BaseModel(type):
    _field_class = ModelField

    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__

        # do not perform initialization for Model class
        # only initialize Model subclasses
        parents = [base for base in bases if isinstance(base, BaseModel)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        new_class = super_new(cls, name, bases, attrs, **kwargs)
        attr_meta = attrs.get('Meta')
        meta = attr_meta if attr_meta else getattr(new_class, 'Meta', None)
        if not meta:
            meta = type('Meta', (), {})

        attrs = set(
            k for k, v in new_class.__dict__.items()
            if not (k[:2] == '__' and k[-2:] == '__') and is_not_special_object(v)
        )
        hints = typing.get_type_hints(new_class)
        try:
            meta.fields = getattr(meta, 'fields')
        except AttributeError:  # assume all fields are defined as class attributes
            assert hints or attrs, ('Model must have a "fields" attribute on its Meta class or its '
                                    'fields defined as class attributes'.format(new_class.__name__))
            fields = set(hints) | attrs
            fields.discard('Meta')
            meta.fields = tuple(fields)

        meta.allow_empty = getattr(meta, 'allow_empty', tuple())

        for field_name in meta.fields:
            field_type = hints.get(field_name) if hints else None
            default_value = getattr(new_class, field_name, None)
            if isinstance(default_value, ModelField):
                default_value = default_value.default_value
            field = ModelField(
                model_class=new_class,
                name=field_name,
                default_value=default_value,
                type=field_type,
                allow_empty=field_name in meta.allow_empty,
            )
            setattr(new_class, field_name, field)

        new_class._meta = meta

        return new_class


class Model(metaclass=BaseModel):
    def __init__(self, **kwargs):
        for field_name in self._meta.fields:
            descriptor = getattr(type(self), field_name)
            field_value = kwargs.get(field_name)
            default = descriptor.default_value
            factory = default if isinstance(default, Callable) else None
            field_value = factory() if factory and not field_value else kwargs.get(field_name, default)
            setattr(self, field_name, field_value)

        self.__post_init__(**kwargs)

    def __post_init__(self, **kwargs):
        pass

    def __eq__(self, other: Any) -> bool:
        try:
            return dict(self) == dict(other)  # type: ignore
        except (TypeError, ValueError):
            return False

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        self.clean()

        for name, value, descriptor in self._get_fields():
            yield name, descriptor.to_python(value)

    def __repr__(self) -> str:
        attrs = ', '.join(
            '{name}={value!r}'.format(name=name, value=value) for name, value, _ in self._get_fields()
        )
        return '{class_name}({attrs})'.format(class_name=type(self).__name__, attrs=attrs)

    def _get_fields(self) -> Iterator[Tuple[str, Any, ModelField]]:
        cls = type(self)
        return (
            (field_name, getattr(self, field_name), getattr(cls, field_name))
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

    def clean(self):
        for name, value, descriptor in self._get_fields():
            clean_value = descriptor.clean(self, value)
            setattr(self, name, clean_value)

        self.validate()

    def validate(self, raise_exception: bool=True) -> Union[None, bool]:
        for name, value, descriptor in self._get_fields():
            try:
                descriptor.validate(self, value)
            except ValidationError:
                if raise_exception:
                    raise
                return False

        return None if raise_exception else True
