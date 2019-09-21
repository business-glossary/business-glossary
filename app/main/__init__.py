"""
    business_glossary.main
    ~~~~~~~~~~~~~~~~~~~~~~

    This module contains the definition of the main blueprint.

    :copyright: (c) 2017 by Alan Tindale.
    :license: Apache, see LICENSE for more details.
"""

from flask import Blueprint

main = Blueprint('main', __name__)

from . import routes
