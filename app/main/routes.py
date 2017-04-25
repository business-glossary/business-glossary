'''Routes for the Business Glossary'''

# import os
from os import mkdir
from os.path import dirname, join

import warnings

from flask import render_template, request, send_from_directory, send_file
from app import app, db, pages

from flask_flatpages import pygments_style_defs
from config import BASE_DIR
from flask_security import current_user
from sqlalchemy import func
from flask_admin import Admin, form, BaseView, expose
from flask_admin.contrib.sqla import ModelView

from . import main
from ..models import Document, DocumentType, Term, TermStatus, Category, Person, Link, Location, Table, \
    Column, Rule, Note

# WTForms helpers
from ..utils import wtf
wtf.add_helpers(app)

# Create directory for file fields to use
FILE_PATH = join(BASE_DIR, 'app', 'static', 'files')

try:
    mkdir(FILE_PATH)
except OSError:
    pass

#####################
#### admin views ####
#####################

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
    column_searchable_list = ['identifier', 'name', 'description']
    column_default_sort = 'identifier'

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

class TableView(ProtectedModelView):
    '''Set the view options with displaying a Table in the admin view'''
    column_default_sort = 'name'
    column_filters = ['location']
    form_excluded_columns = ('columns')

class ColumnView(ProtectedModelView):
    '''Set the view options with displaying a Column in the admin view'''
    column_filters = ['table', 'name']

class BackupView(BaseView):
    '''Add backup option to admin menu'''
    @expose('/')
    def index(self):
        return self.render('backup/backup_restore.html')

admin = Admin(app,
              name='BUSINESS GLOSSARY',
              template_mode='bootstrap3',
              base_template='/admin/new_master.html')

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)
    admin.add_view(TermView(Term, db.session))

admin.add_view(RuleView(Rule, db.session))
admin.add_view(ProtectedModelView(Note, db.session))
admin.add_view(ProtectedModelView(Link, db.session))
admin.add_view(FileView(Document, db.session))
admin.add_view(ProtectedModelView(Location, db.session, category="Assets"))
admin.add_view(TableView(Table, db.session, category="Assets"))
admin.add_view(ColumnView(Column, db.session, category="Assets"))
admin.add_view(ProtectedModelView(DocumentType, db.session, category="Lookups"))
admin.add_view(ProtectedModelView(TermStatus, db.session, category="Lookups"))
admin.add_view(ProtectedModelView(Category, db.session, category="Lookups"))
admin.add_view(ProtectedModelView(Person, db.session, category="Lookups"))
admin.add_view(BackupView(name='Backup', endpoint='backup', category='Backup & Restore'))


@app.context_processor
def inject_user():
    '''Inject pages to make it available on all pages'''
    tagged = [p for p in pages]

    return dict(tagged=tagged)


###########################
#### define the routes ####
###########################

@main.route('/about')
def about():
    '''Present the about page'''
    return render_template('about.html')


@main.route('/')
@main.route('/glossary/')
def glossary():
    '''Display the glossary main list of terms'''
    glossary = Term.query.order_by(Term.name).all()
    return render_template('show_glossary.html', glossary=glossary)


@main.route('/glossary_rules/')
def glossary_rules():
    rules = Rule.query.order_by(Rule.identifier).all()

    return render_template('show_glossary_rules.html', rules=rules)


@app.route('/<path:path>/')
def page(path):
    '''Serve up markdown pages using Flask-FlatPages'''
    page = pages.get_or_404(path)
    return render_template('flatpages/page.html', page=page)


@app.route('/tag/<string:tag>/')
def tag(tag):
    '''Handle FlatPages tags'''
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('flatpages/tag.html', pages=tagged, tag=tag)


@main.route('/abbreviations/')
def abbreviations():
    glossary = Term.query.filter(Term.abbreviation != "").order_by(Term.abbreviation).all()
    return render_template('show_abbreviations.html', glossary=glossary)


@main.route('/backup_restore/')
def backup_restore():
    return render_template('backup/backup_restore.html')


@main.route('/do_backup/', methods=['POST'])
def do_backup():
    from app.loader import dump_yaml
    import time
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = "bg_export_" + timestr + ".yml"
    dump_yaml.dump(join(dirname(BASE_DIR), 'bg_interface', filename))
    return render_template('backup/do_backup.html', filename=filename)

@main.route('/download/<string:selected_filename>/')
def download(selected_filename):
    try:
        return send_file(join(dirname(BASE_DIR), 'bg_interface', selected_filename),
                         as_attachment=True,
                         attachment_filename=selected_filename)
    except Exception as e:
        return str(e)

@main.route('/profile/')
def profile():
    '''Present the user profile'''
    return render_template('show_profile.html')


@main.route('/term/<int:selected_term>')
@main.route('/term/<string:selected_term_name>')
def show_term(selected_term=None, selected_term_name=None):
    print(">>>>>", selected_term)
    print(">>>>>", selected_term_name)

    if selected_term is None:
        term = Term.query.filter(func.lower(Term.name) == func.lower(selected_term_name)).first()
        if not term:
            return render_template('errors/404.html')
        else:
            return render_template('show_term.html',
                                   term=Term.query.filter(func.lower(Term.name) == \
                                                          func.lower(selected_term_name)).first())
    else:
        return render_template('show_term.html',
                               term=Term.query.filter_by(id=selected_term).first())


@main.route('/new_term/<int:selected_term>')
@main.route('/new_term/<string:selected_term_name>')
def show_new_term(selected_term=None, selected_term_name=None):
    '''Present the new term view'''

    if selected_term is None:
        term = Term.query.filter(func.lower(Term.name) == func.lower(selected_term_name)).first()
        if not term:
            return render_template('errors/404.html')
        else:
            return render_template('show_new_term.html',
                                   term=Term.query.filter(func.lower(Term.name) == \
                                                          func.lower(selected_term_name)).first())
    else:
        return render_template('show_new_term.html',
                               term=Term.query.filter_by(id=selected_term).first())


@main.route('/documents/<int:selected_term>')
def show_documents(selected_term):
    documents = Document.query.order_by(Document.name).all()
    term = Term.query.filter_by(id=selected_term).first()
    documents = term.documents

    return render_template('show_documents.html', term=term, documents=documents)


@main.route('/assets/<int:selected_term>')
def show_assets(selected_term):

    term = Term.query.filter_by(id=selected_term).first()
    assets = term.columns

    return render_template('show_assets.html', term=term, assets=assets)


@main.route('/rules/<int:selected_term>')
def show_rules(selected_term):

    term = Term.query.filter_by(id=selected_term).first()
    rules = term.rules

    return render_template('show_rules.html', term=term, rules=rules)


@main.route('/rule/<int:selected_rule>')
def show_rule(selected_rule):

    rule = Rule.query.filter_by(id=selected_rule).first()
    print(rule.documents)
    print(rule.comments)
    return render_template('show_rule.html', rule=rule)


@main.route('/rule/documents/<int:selected_rule>')
def show_rule_documents(selected_rule):

    rule = Rule.query.filter_by(id=selected_rule).first()
    documents = rule.documents

    return render_template('show_rule_documents.html', rule=rule, documents=documents)


@main.route('/location/<selected_location>')
@main.route('/location/<selected_location>/details')
def show_location_details(selected_location):

    location = Location.query.filter_by(id=selected_location).first()

    return render_template('show_location_details.html', location=location)


@main.route('/location/<selected_location>/tables')
def show_location_tables(selected_location):

    location = Location.query.filter_by(id=selected_location).first()
    tables = location.tables

    return render_template('show_location_tables.html', location=location, tables=tables)


@main.route('/table/<selected_table>')
@main.route('/table/<selected_table>/details')
def show_table_details(selected_table):

    table = Table.query.filter_by(id=selected_table).first()
    columns = table.columns

    return render_template('show_table_details.html', table=table, columns=columns)


@main.route('/table/<selected_table>/columns')
def show_table_columns(selected_table):

    table = Table.query.filter_by(id=selected_table).first()
    columns = table.columns

    return render_template('show_table_columns.html', table=table, columns=columns)


@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        search = request.form['search']

        from sqlalchemy import or_

        terms = Term.query.filter(or_(Term.name.ilike('%' + str(search) + '%'),
                                      Term.short_description.ilike('%' + str(search) + '%'),
                                      Term.long_description.ilike('%' + str(search) + '%'),
                                      Term.abbreviation.ilike('%' + str(search) + '%'))).all()
        columns = Column.query.filter(Column.name.ilike('%' + str(search) + '%')).all()
        rules = Rule.query.filter(or_(Rule.identifier.ilike('%' + str(search) + '%'),
                                      Rule.name.ilike('%' + str(search) + '%'),
                                      Rule.description.ilike('%' + str(search) + '%'),
                                      Rule.notes.ilike('%' + str(search) + '%'))).all()

        return render_template("results.html", terms=terms, columns=columns, rules=rules)
    return render_template('search.html')


@main.route('/source_code')
def source_code():
    """This is a proof-of-concept for return a position in source code to the browser"""
    filename = '05_ACCT HIST.sas'
    root_dir = os.path.dirname(os.getcwd())
    print(root_dir)
    return send_from_directory(os.path.join('.', 'static', 'source_code'),
                               filename,
                               as_attachment=False,
                               mimetype='text/html')


@app.route('/graph2')
def graph2():
    return render_template('graph2.html')
