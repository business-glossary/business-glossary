#################
#### imports ####
#################

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flaskext.markdown import Markdown
from flask_moment import Moment
#from config import config

import os

################
#### config ####
################

app = Flask(__name__)

app.config.from_object(os.getenv('BG_CONFIG') or 'config.DevelopmentConfig')

db = SQLAlchemy(app)
moment = Moment(app)
md = Markdown(app, extensions=['fenced_code'])

print
print "BG_CONFIG=%s" % os.getenv('BG_CONFIG')
print "TERMS_PER_PAGE=%s" % app.config['TERMS_PER_PAGE']
print "SQLALCHEMY_DATABASE_URI=" + app.config['SQLALCHEMY_DATABASE_URI']
print "SQLALCHEMY_TRACK_MODIFICATIONS=%s" % app.config['SQLALCHEMY_TRACK_MODIFICATIONS']
print

#################################
#### register our blueprints ####
#################################

from main import main as main_blueprint
app.register_blueprint(main_blueprint)
