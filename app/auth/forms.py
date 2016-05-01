from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Regexp, EqualTo
from ..models import User


class RegisterForm(Form):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0,
                                                          'Usernames must have only letters, '
                                                          'numbers, or underscores.')])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128), EqualTo('password2',
                             'Passwords must match.')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register!')

    def validate_username(self, field):
        if User.objects(username=field.data.lower()):
            raise ValidationError('Username is already taken.')


class LoginForm(Form):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')