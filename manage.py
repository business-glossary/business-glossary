"""
This is the main manage.py script.

From here you can load and dump data and start the built-in webserver.

Copyright 2016, 2017 Alan Tindale
"""

import os
import datetime

COV = None

if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from app.users.models import User, Role
from app.extensions import db

from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand

from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import encrypt_password

from app.core import create_app

#from app.models import *
#from app.users.models import db
from app.config import BASE_DIR

app = create_app(os.getenv('BG_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def create_user(email):
    """Add an admin user to your database"""

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    from getpass import getpass

    password = getpass()

    user = user_datastore.create_user(email=email, password=encrypt_password(password))

    admin_role = user_datastore.find_or_create_role("admin")
    user_datastore.add_role_to_user(user, admin_role)
    user.confirmed_at = datetime.datetime.utcnow()

    db.session.commit()
    print("Created admin user: %s" % (user, ))


@manager.command
def clear_db():
    '''Clear the database'''
    db.drop_all()
    db.create_all()


@manager.command
def load_data(filename):
    '''Load data into application'''
    from app.loader import load_yaml
    load_yaml.load(filename)


@manager.option('-y', '--yaml', help='Dump to yaml format', dest='yaml', default=False, action="store_true")
@manager.option('-j', '--json', help='Dump to json format', dest='json', default=False, action="store_true")
def dump(yaml, json):
    '''Dump data from application'''

    import time
    timestr = time.strftime("%Y%m%d-%H%M%S")

    file_path = os.path.join(os.path.dirname(BASE_DIR), 'bg_interface')
    file_name = os.path.join(file_path, "bg_export_" + timestr)

    if yaml:
        from app.loader import dump_yaml
        dump_yaml.dump(file_name + ".yaml")

    if json:
        from app.loader import dump_json
        dump_json.dump(file_name + ".json")


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        covdir = os.path.join(BASE_DIR, 'htmlcov')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)

if __name__ == '__main__':
    manager.run()
