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

import os
from flask_admin import Admin, BaseView, form, expose
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user

#from app.term_bp.forms import PrintForm
from app.extensions import db
from app.models import Category

from app.config import BASE_DIR

# Create directory for file fields to use
FILE_PATH = os.path.join(BASE_DIR, 'app', 'static', 'files')

try:
    os.mkdir(FILE_PATH)
except OSError:
    pass

######################
## Admin views
######################

class ProtectedModelView(ModelView):
    '''Check user has logged in for each admin view'''
    def is_accessible(self):
        return current_user.has_role('admin')

class FileView(ProtectedModelView):
    '''Override form field to use Flask-Admin FileUploadField'''
    form_overrides = {
        'path': form.FileUploadField
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'path': {
            'label': 'File',
            'base_path': FILE_PATH,
            'allow_overwrite': False
        }
    }

class RuleView(ProtectedModelView):
    '''Set the view options with displaying a Rule in the admin view'''
    form_excluded_columns = ('created_on', 'updated_on')
    form_columns = ('identifier', 'name', 'description', 'notes', 'terms', 'comments', 'documents')
    column_searchable_list = ['identifier', 'name', 'description']
    column_default_sort = 'identifier'
    form_widget_args = {
        'notes': {
            'rows': 10
        },
        'description': {
            'rows': 5
        }
    }

class TermView(ProtectedModelView):
    '''Set the view options with displaying a Term in the admin view'''
    form_create_rules = ('name', 'short_description', 'long_description', 'abbreviation', 'owner',
                         'steward', 'status', 'categories', 'links', 'rules', 'documents')
    form_edit_rules = ('name', 'short_description', 'long_description', 'abbreviation', 'owner',
                       'steward', 'status', 'categories', 'links', 'rules', 'related_terms',
                       'documents', 'columns')
    column_list = ['name', 'short_description', 'abbreviation', 'status']
    form_excluded_columns = ('created_on', 'updated_on')
    column_searchable_list = ['name']
    form_widget_args = {
        'long_description': {
            'rows': 5
        }
    }

class TableView(ProtectedModelView):
    '''Set the view options with displaying a Table in the admin view'''
    column_default_sort = 'name'
    column_filters = ['location', 'name']
    form_excluded_columns = ('columns')

class ColumnView(ProtectedModelView):
    '''Set the view options with displaying a Column in the admin view'''
    column_filters = ['table', 'name']

class BackupView(BaseView):
    '''Add backup option to admin menu'''
    @expose('/')
    def index(self):
        return self.render('backup/backup_restore.html')

class PrintView(BaseView):
    '''Add print option to admin menu'''
    @expose('/')
    def index(self):
        categories = Category.query.all()
        return self.render('print/print_admin_menu.html', categories=categories)