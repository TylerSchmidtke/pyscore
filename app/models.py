from . import db, login_manager, ROLES
from flask.ext.login import UserMixin, AnonymousUserMixin
from flask.ext.bcrypt import check_password_hash
import datetime


class User(UserMixin, db.Document):
    displayname = db.StringField(required=True)
    username = db.StringField(unique=True, required=True)
    password_hash = db.StringField(max_length=128, required=True)
    score = db.IntField(required=True, default=0)
    roles = db.ListField(required=True, default=['user'])
    join_time = db.DateTimeField(default=datetime.datetime.now)
    solved_challenges = db.ListField(default=[])
    hints = db.ListField(default=[])
    registration_ip = db.StringField(default=None)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


class Challenge(db.Document):
    plain_text = db.StringField(required=True)
    challenge_text = db.StringField(required=True)
    attachment_path = db.StringField(required=False)
    notes = db.StringField(required=False, max_length=1024, default=None)
    points = db.IntField(required=True, default=10)
    hint = db.StringField(required=False, max_length=256, default=None)
    hint_points = db.IntField(required=False)
    failures = db.IntField(required=True, default=0)
    successes = db.IntField(required=True, default=0)
    active = db.BooleanField(required=True, default=True)
    case_sensitive = db.BooleanField(required=True, default=True)
    fuzzy_answer = db.BooleanField(required=True, default=False)


class Role(db.Document):
    name = db.StringField(max_length=24, required=True, choices=ROLES)
    description = db.StringField(max_length=255, required=True)


class AnonymousUser(AnonymousUserMixin):
    roles = []
    hints = []


class Audit(db.Document):
    timestamp = db.DateTimeField(default=datetime.datetime.now)
    user = db.StringField()
    message = db.StringField()
    message_type = db.StringField()
    ip = db.StringField(default=None)


@login_manager.user_loader
def load_user(user_id):
    return User.objects.get(id=user_id)

login_manager.anonymous_user = AnonymousUser
