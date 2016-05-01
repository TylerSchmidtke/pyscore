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


if __name__ == "__main__":
    manager.run()


