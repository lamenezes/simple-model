import typing

from .fields import ModelField, Unset
from .utils import is_not_special_object, is_private_attribute


class ModelMetaClass(type):
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
        fields.discard('_is_valid')
        return tuple(field for field in fields if not is_private_attribute(field))

    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__

        # do not perform initialization for Model class
        # only initialize Model subclasses
        parents = [base for base in bases if isinstance(base, ModelMetaClass)]
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
        new_class._is_valid = False

        return new_class
