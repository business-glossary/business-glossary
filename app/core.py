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
import warnings

from app.extensions import db, security, bootstrap, mail, pages, moment, csrf
from app.config import config

from app.users.models import User, Role

from app.main import main as main_blueprint
from app.term_bp import term_bp as term_bp_blueprint

from flask import Flask
from flaskext.markdown import Markdown

from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import encrypt_password

from flask_admin import Admin

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

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    from app.users.forms import ExtendedRegisterForm
    security.init_app(app, user_datastore, register_form=ExtendedRegisterForm)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    md = Markdown(app, output_format='html5', extensions=['fenced_code', 'tables', 'abbr', 'footnotes'])

    pages.init_app(app)
    csrf.init_app(app)

    # Setup admin view - should find a better place for this
    from app.main.admin import MyHomeView, RuleView, FileView, TableView, ColumnView, ProtectedModelView, TermView, PrintView

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

    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(term_bp_blueprint)

    with app.app_context():
        db.create_all()
        if not User.query.first():
            # Create a default admin user if there is no user in the database
            user_datastore.create_role(name='admin')
            user_datastore.create_user(
                name='Administration Account',
                email='admin@example.com',
                password=encrypt_password('password'),
                roles=['admin']
            )
            db.session.commit()
            app.logger.info('Created admin user admin@example.com')

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


# Send templated emails
def send_mail(destination, subject, template, **template_kwargs):
    """
    Send templatised emails.

    :param destination: The destination email address.
    :param subject: The email subject line.
    :param template: The template email.
    :param template_kwargs: Any parameters to substitute in the email.
    """
    text = flask.render_template("{0}.txt".format(template), **template_kwargs)

    logging.info("Sending email to %s. Body is: %s", destination, repr(text)[:50])

    msg = Message(subject, sender=_security.email_sender, recipients=[destination])

    msg.body = text
    msg.html = flask.render_template("{0}.html".format(template),
                                     **template_kwargs)

    mail.send(msg)
