from .models import Model


def to_dict(model: Model):
    if not isinstance(model, Model):
        raise TypeError('First argument must be of class type simple_model.Model')

    assert model._validation_count, 'model.validate() must be run before conversion'

    d = {}
    for field_name, descriptor in model._get_fields():
        value = getattr(model, field_name)
        d[field_name] = descriptor.to_python(value)

    return d
