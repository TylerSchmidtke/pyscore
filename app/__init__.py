from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager
from flask.ext.wtf import CsrfProtect
from flask.ext.uploads import UploadSet, configure_uploads, ALL
from config import config

bootstrap = Bootstrap()
db = MongoEngine()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
csrf = CsrfProtect()
attachments = UploadSet('attachments', ALL)

# Define available roles in WTForms choices format
ROLES = [('administrator', 'administrator'),
         ('contributer', 'contributer'),
         ('user', 'user')]


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    configure_uploads(app, attachments)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Custom routes and error pages

    # Populate the default admin user and roles

    # Blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app
