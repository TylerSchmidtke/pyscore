from flask.ext.wtf import Form
from passlib import hash
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, \
                    IntegerField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, Optional
from .. import ROLES

POINTS = [(i, i) for i in list(range(5, 105, 5))]

# Generate a list of selections for hash_type, remove miscellaneous non-hashes
HASHES = [(i, i) for i in dir(hash)[28:]]
HASHES.insert(0, ("custom", "custom"))
REMOVE_HASHES = ['django_disabled', 'unix_disabled',
                 'plaintext', 'roundup_plaintext', 'unix_fallback']
for h in REMOVE_HASHES:
    HASHES.remove((h, h))


class CreateChallengeForm(Form):

    plain_text = StringField('Plain Text', validators=[DataRequired(),
                                                       Regexp('.*[A-Za-z0-9_.\h\?]*$',
                                                              0,
                                                              'Challenge plain text must have only letters, '
                                                              'numbers, dots, spaces, or underscores.')])
    hash_type = SelectField("Hash Type", choices=HASHES, validators=[Optional()])
    challenge_text = StringField('Challenge Text', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Length(max=1024),
                                               Regexp('.*[A-Za-z0-9_.\h\?]*$',
                                                      0,
                                                      'Notes must have only letters, '
                                                      'numbers, dots, spaces, or underscores.'),
                                               Optional()])
    points = SelectField('Points', choices=POINTS, coerce=int)
    active = BooleanField('Active', default=True)
    case_sensitive = BooleanField('Case Sensitive Answer', default=True)
    fuzzy_answer = BooleanField('Fuzzy Answer Matching', default=False)
    attachment = FileField('Attachment', validators=[Optional()])
    submit = SubmitField('Create')


class SearchUserForm(Form):
    username = StringField('Username', validators=[Length(1, 64),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0,
                                                          'Usernames must have only letters, '
                                                          'numbers, or underscores.')])
    role = SelectField('Role', choices=ROLES, default=('user', 'user'))
    submit = SubmitField('Search')


class ModifyChallengeForm(Form):
    active = BooleanField('Active', validators=[Optional()])
    fuzzy_answer = BooleanField('Fuzzy Answer Matching', default=False)
    delete = BooleanField('Delete', validators=[Optional()])
    points = SelectField('Points', choices=POINTS, coerce=int, validators=[Optional()])
    attachment = FileField('Attachment', validators=[Optional()])
    submit = SubmitField('Modify')


class ModifyUserForm(Form):
    delete = BooleanField('Delete', validators=[Optional()])
    password = PasswordField('Password', validators=[Optional(), Length(8, 128)])

    score = IntegerField('Score', validators=[Optional()])
    submit = SubmitField('Update!')
