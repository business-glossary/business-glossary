from os import getenv
from app.core import create_app

app = create_app(getenv('BG_CONFIG') or 'default')
