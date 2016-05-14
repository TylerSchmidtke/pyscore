from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Regexp


class ChallengeForm(Form):
    challenge_submission = StringField('', validators=[Regexp('.*[A-Za-z0-9_.\h]*$',
                                                              0,
                                                              'Challenge submissions must have only letters, '
                                                              'numbers, dots, spaces, or underscores.')])
    submit = SubmitField('Submit')


