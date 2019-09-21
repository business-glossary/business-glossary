# -*- coding: utf-8 -*-
# 
#   Copyright 2017 Alan Tindale, All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import os

from flask import Flask
from flaskext.markdown import Markdown

from flask_admin import Admin

from app.extensions import db, bootstrap, mail, pages, moment, csrf, migrate, login_manager
from app.config import config, BASE_DIR

from app import commands

from app.auth.models import Role, User

from app.main import main as main_blueprint
from app.term_bp import term_bp as term_bp_blueprint
from app.auth.views import auth

from app.models import Term, Rule, Note, Link, Table, Document, Location, Column, DocumentType, \
                       TermStatus, Category, Person


# Bootstrap helpers
def alert_class_filter(category):
    """
    Map different message types to Bootstrap alert classes

    @param category:          string - a message type
    """
    categories = {
        "message": "warning"
    }
    return categories.get(category, category)


def create_app(config_name):
    """An application factory, as explained here:
        http://flask.pocoo.org/docs/patterns/appfactories/

    @param config_name:    The configuration object to use.
    """
    app = Flask(__name__)

    app.config.from_object(config[config_name] or config[os.getenv('BG_CONFIG')])
    app.config.from_envvar('BG_SETTINGS', silent=True)

    config[config_name].init_app(app)

    db.init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.auth.models import AnonymousUser
    login_manager.anonymous_user = AnonymousUser

    md = Markdown(app, 
                  output_format='html5', 
                  extensions=['fenced_code', 'tables', 'abbr', 'footnotes'])

    pages.init_app(app)
    csrf.init_app(app)

    register_adminviews(app)

    app.jinja_env.filters['alert_class'] = alert_class_filter

    # WTForms helpers
    from .utils import add_helpers
    add_helpers(app)

    if not app.debug:
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler(mailhost=app.config['MAIL_SERVER'],
                                   fromaddr=app.config['ADMINS_FROM_EMAIL'],
                                   toaddrs=app.config['ADMINS_EMAIL'],
                                   subject='Application Error Occurred')
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    register_blueprints(app)
    register_commands(app)

    # Create the bg_interface directory if it does not exist.
    directory = os.path.join(os.path.dirname(BASE_DIR), 'bg_interface')

    if not os.path.exists(directory):
        os.makedirs(directory)

    with app.app_context():
        db.create_all()

        role = Role.query.filter_by(name='admin').first()

        if not role:
            role = Role(name='admin', description='Administration Role')
            db.session.add(role)
            db.session.commit()

        if not User.query.first():
            # Create a default admin user if there is no user in the database
            user = User(username='admin',
                        name='Administration Account',
                        email='admin@example.com',
                        roles=[role])

            user.set_password('password')

            db.session.add(user)
            db.session.commit()

            app.logger.info('Created admin role and user (username=admin, email=admin@example.com)')

    return app


#print
#print("BG_SETTINGS=%s" % os.getenv('BG_SETTINGS'))
#print("MAIL_SERVER=%s" % app.config['MAIL_SERVER'])
#print("BG_CONFIG=%s" % os.getenv('BG_CONFIG'))
#print("TERMS_PER_PAGE=%s" % app.config['TERMS_PER_PAGE'])
#print("SQLALCHEMY_DATABASE_URI=" + app.config['SQLALCHEMY_DATABASE_URI'])
#print("SQLALCHEMY_TRACK_MODIFICATIONS=%s" % app.config['SQLALCHEMY_TRACK_MODIFICATIONS'])
#print("SQLALCHEMY_ECHO=" + str(app.config['SQLALCHEMY_ECHO']))
#print

def register_adminviews(app):
    '''Register Flask-Admin views.'''

    from app.main.admin import MyHomeView, RuleView, FileView, TableView, ColumnView, \
                               ProtectedModelView, TermView, PrintView

    admin = Admin(app,
                  name='BUSINESS GLOSSARY',
                  template_mode='bootstrap3',
                  base_template='/admin/new_master.html',
                  index_view=MyHomeView())

    admin.add_view(TermView(Term, db.session))
    admin.add_view(RuleView(Rule, db.session))
    admin.add_view(ProtectedModelView(Note, db.session))
    admin.add_view(ProtectedModelView(Link, db.session))
    admin.add_view(FileView(Document, db.session))
    admin.add_view(ProtectedModelView(Location, db.session, category="Assets"))
    admin.add_view(TableView(Table, db.session, category="Assets"))
    admin.add_view(ColumnView(Column, db.session, category="Assets"))
    admin.add_view(ProtectedModelView(DocumentType, db.session, category="Lookups"))
    admin.add_view(ProtectedModelView(TermStatus, db.session, category="Lookups"))
    admin.add_view(ProtectedModelView(Category, db.session, category="Lookups"))
    admin.add_view(ProtectedModelView(Person, db.session, category="Lookups"))
    admin.add_view(PrintView(name='Print Glossary', endpoint='print'))


def register_blueprints(app):
    '''Register Flask blueprints.'''
    app.register_blueprint(main_blueprint)
    app.register_blueprint(term_bp_blueprint)
    app.register_blueprint(auth)


def register_commands(app):
    '''Register Click commands.'''
    app.cli.add_command(commands.data)
