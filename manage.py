import os
import datetime

COV = None

if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from flask_security.utils import encrypt_password
from app import app, db
from app.users.models import user_datastore
from config import BASE_DIR

app.config.from_object(os.getenv('BG_CONFIG') or 'config.DevelopmentConfig')

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def add_admin(email, password):
    """Add an admin user to your database"""
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

@manager.command
def dump(filename):
    '''Dump data from application'''
    from app.loader import dump_yaml

    dump_yaml.dump(filename)

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
