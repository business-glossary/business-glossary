"""
    business_glossary.utils
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This module adds some Jinja2 helpers for form generation.

    :copyright: (c) 2017 by Alan Tindale.
    :license: Apache, see LICENSE for more details.
"""

from wtforms.fields import HiddenField, BooleanField

def add_helpers(app):
    """Add helpers"""
    
    def is_hidden_field_filter(field):
        return isinstance(field, HiddenField)

    def is_boolean_field_filter(field):
        return isinstance(field, BooleanField)

    app.jinja_env.filters['is_hidden_field'] = is_hidden_field_filter
    app.jinja_env.filters['is_boolean_field'] = is_boolean_field_filter
