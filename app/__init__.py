from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('config')
db = SQLAlchemy(app)

from app import routes, models

from .momentjs import momentjs
app.jinja_env.globals['momentjs'] = momentjs