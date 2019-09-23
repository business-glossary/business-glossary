"""
    business_glossary.config
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This module defines config classes.

    :copyright: (c) 2017 by Alan Tindale.
    :license: Apache, see LICENSE for more details.
"""

import os

from app.extensions import tables, fenced_code, wikilinks, footnotes

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config(object):
    '''Define the base configuration object'''
    SECRET_KEY = 'This is a new secret key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TERMS_PER_PAGE = 5
    CSRF_ENABLED = True

    MAIL_SERVER = 'mail.example.com'
    MAIL_PORT = 25
    MAIL_USE_SSL = False
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    ADMINS_EMAIL = ['admin@example.com']
    ADMINS_FROM_EMAIL = ['admin@example.com']

    APPLICATION_NAME = 'Business Glossary'

    # Use the Active Directory sAMAccountName and domain to login.
    # This is used in the form of domain\\username.
    LDAP_AD_USE_SAN = True
    LDAP_AD_DOMAIN = 'tindale'

    # Host and port are manditory required fields.
    LDAP_HOST = ''
    LDAP_PORT = 389
    # If LDAP_AD_USE_SAN is False then we need these options to be specified.
    LDAP_USER_ATTR = ''
    LDAP_USER_DN = ''
    LDAP_BASE_DN = ''

    # FlatPages configuration
    FLATPAGES_AUTO_RELOAD = True
    FLATPAGES_EXTENSION = '.md'
    FLATPAGES_MARKDOWN_EXTENSIONS = ['codehilite', tables, footnotes, fenced_code, wikilinks]

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    '''Define the development configuration object'''
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('BG_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'glossary_dev.db')
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    '''Define the test configuration object'''
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('BG_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'glossary_test.db')
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    '''Define the production configuration object'''
    SQLALCHEMY_DATABASE_URI = os.environ.get('BG_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'glossary.db')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
