#!/usr/bin/env python
from app import create_app, db
from app.models import User, Role
from flask.ext.script import Shell, Manager, Server
import os


app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, user=User, role=Role)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("runserver", Server(
    use_debugger=True,
    use_reloader=True,
    host="0.0.0.0"
))


@manager.command
def test():
    """Run unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.option('-e', '--env', dest='env', default='prod', help='Environment: dev or prod.')
@manager.option('-d', '--db', dest='db_url', default='localhost', help='MongoDB URL: default=localhost')
def setup(env, db_url):
    # Create connection
    from pymongo import MongoClient
    from flask.ext.bcrypt import generate_password_hash
    con = MongoClient(db_url, 27017)

    if env == 'prod':
        db_env = con['pyscore']
    else:
        db_env = con['pyscore-dev']

    # Insert admin user
    admin = {
        'displayname': 'admin',
        'username': 'admin',
        'password_hash': generate_password_hash('pyscore', 15).decode('utf-8'),
        'roles': ['administrator', 'contributer', 'user']
    }
    user = db_env.user
    user.replace_one({'username': 'admin'}, admin, upsert=True)
    con.close()


if __name__ == "__main__":
    manager.run()


