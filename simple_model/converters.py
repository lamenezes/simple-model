from .models import Model


def to_dict(model: Model):
    if not isinstance(model, Model):
        raise TypeError('First argument must be of class type simple_model.Model')

    assert model._validation_count, 'model.validate() must be run before conversion'

    return {
        field: descriptor.to_python(value)
        for field, value, descriptor in model._get_fields()
    }
