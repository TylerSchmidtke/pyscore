import unittest
from app import create_app
from app.models import User
from flask.ext.bcrypt import generate_password_hash
from mongoengine import connect


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        d = connect('pyscore-test')
        d.drop_database('pyscore-test')
        self.app_context.pop()

    def test_password_verification(self):
        u = User(password_hash=generate_password_hash('barbarian'))
        self.assertTrue(u.verify_password('barbarian'))
        self.assertFalse(u.verify_password('thulsa'))

    def test_password_salts_are_random(self):
        u = User(password_hash=generate_password_hash('barbarian'))
        u2 = User(password_hash=generate_password_hash('barbarian'))
        self.assertTrue(u.password_hash != u2.password_hash)
