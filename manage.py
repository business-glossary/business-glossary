import os

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db

app.config.from_object(os.getenv('BG_CONFIG') or 'config.DevelopmentConfig')

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
