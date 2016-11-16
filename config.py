import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
print "BASE_DIR=" + BASE_DIR

class Config(object):
    SECRET_KEY = 'enter your secret key here'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TERMS_PER_PAGE = 5

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'glossary_dev.db')
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'glossary_test.db')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'glossary.db')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
