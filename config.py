import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
print "BASE_DIR=" + BASE_DIR

class Config(object):
    SECRET_KEY = 'enter your secret key here'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TERMS_PER_PAGE = 5

    MAIL_SERVER = 'mail.pl.boq.com.au'
    MAIL_PORT = 25
    MAIL_USE_SSL = False
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''

    APPLICATION_NAME = 'Business Glossary'

    # Flask-Security flags
    SECURITY_CONFIRMABLE = False
    SECURITY_REGISTERABLE = False
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True

    SECURITY_PASSWORD_HASH = "bcrypt"

    SECURITY_PASSWORD_SALT = "$2a$12$sSoMBQ9V4hxNba5E0Xl3Fe"
    SECURITY_CONFIRM_SALT = "$2a$12$QyCM19UPUNLMq8n225V7qu"
    SECURITY_RESET_SALT = "$2a$12$GrrU0tYteKw45b5VfON5p."
    SECURITY_REMEMBER_SALT = "$2a$12$unlKF.sL4gnm4icbk0tvVe"

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'glossary_dev.db')
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'glossary_test.db')
    SQLALCHEMY_ECHO = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'glossary.db')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
