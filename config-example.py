import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default'
    UPLOADED_ATTACHMENTS_DEST = 'app/static/attachments'
    UPLOADED_ATTACHMENTS_URL = '/attachments/'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_SETTINGS = {'db': 'pyscore-dev',
                        'host': '127.0.0.1',
                        'port': 27017}


class TestingConfig(Config):
    TESTING = True
    MONGODB_SETTINGS = {'db': 'pyscore-test',
                        'host': 'localhost',
                        'port': 27017}


class ProductionConfig(Config):
    MONGODB_SETTINGS = {'db': 'pyscore',
                        'host': 'localhost',
                        'port': 27017}

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}