#################
#### imports ####
#################

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_flatpages import FlatPages
from flaskext.markdown import Markdown
from flask_moment import Moment
from flask_mail import Mail

import os

################
#### config ####
################

app = Flask(__name__)

app.config.from_object(os.getenv('BG_CONFIG') or 'config.DevelopmentConfig')
app.config.from_envvar('BG_SETTINGS', silent=True)

db = SQLAlchemy(app)
moment = Moment(app)
mail = Mail(app)
md = Markdown(app, extensions=['fenced_code', 'tables', 'abbr'])
pages = FlatPages(app)

print
print("BG_SETTINGS=%s" % os.getenv('BG_SETTINGS'))
print("MAIL_SERVER=%s" % app.config['MAIL_SERVER'])
print("BG_CONFIG=%s" % os.getenv('BG_CONFIG'))
print("TERMS_PER_PAGE=%s" % app.config['TERMS_PER_PAGE'])
print("SQLALCHEMY_DATABASE_URI=" + app.config['SQLALCHEMY_DATABASE_URI'])
print("SQLALCHEMY_TRACK_MODIFICATIONS=%s" % app.config['SQLALCHEMY_TRACK_MODIFICATIONS'])
print

if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler(mailhost=app.config['MAIL_SERVER'],
                            fromaddr=app.config['ADMINS_FROM_EMAIL'],
                            toaddrs=app.config['ADMINS_EMAIL'],
                            subject='Application Error Occurred')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

# Send templated emails
def send_mail(destination, subject, template, **template_kwargs):
    text = flask.render_template("{0}.txt".format(template), **template_kwargs)

    logging.info("Sending email to {0}. Body is: {1}".format(
        destination, repr(text)[:50]))

    msg = Message(
        subject,
        recipients=[destination]
    )

    msg.body = text
    msg.html = flask.render_template("{0}.html".format(template),
            **template_kwargs)

    mail.send(msg)


# Bootstrap helpers
def alert_class_filter(category):
    # Map different message types to Bootstrap alert classes
    categories = {
        "message": "warning"
    }
    return categories.get(category, category)

app.jinja_env.filters['alert_class'] = alert_class_filter


# WTForms helpers
from utils import wtf
wtf.add_helpers(app)


# Import the security/user models
from users import models


# Import custom error templates
from errors import views


# Register blueprints
from main import main as main_blueprint
app.register_blueprint(main_blueprint)