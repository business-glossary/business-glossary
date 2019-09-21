"""
    business_glossary.term
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains the definition for the term blueprint.

    :copyright: (c) 2017 by Alan Tindale.
    :license: Apache, see LICENSE for more details.
"""

from flask import Blueprint

term = Blueprint('term', __name__)

from . import views