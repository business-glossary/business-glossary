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

from flask_security import Security
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_flatpages import FlatPages
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

from markdown.extensions.tables import TableExtension
from markdown.extensions.footnotes import FootnoteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.wikilinks import WikiLinkExtension

db = SQLAlchemy()
security = Security()
bootstrap = Bootstrap()
mail = Mail()
pages = FlatPages()
moment = Moment()
csrf = CSRFProtect()
migrate = Migrate()

tables = TableExtension()
footnotes = FootnoteExtension()
fenced_code = FencedCodeExtension()
wikilinks = WikiLinkExtension()