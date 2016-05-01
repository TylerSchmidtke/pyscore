from wtforms.validators import DataRequired


class RequiredIf(DataRequired):

    def __init__(self, field_name, *args, **kwargs):
        self.field_name = field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.field_name)
        if other_field is None:
            pass
        if not other_field.data:
            super(RequiredIf, self).__call__(form, field)
