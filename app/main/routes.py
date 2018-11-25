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

from os import mkdir, getenv
from os.path import dirname, join, isfile
from datetime import datetime

from flask import flash, redirect, url_for, render_template, request, \
     send_from_directory, send_file
from flask import current_app

from flask_flatpages import pygments_style_defs
from flask_security import current_user, login_required, roles_required
from flask_security.utils import encrypt_password
from flask_flatpages import FlatPages
from sqlalchemy import func
from app import models
from app.config import BASE_DIR
from app.main.forms import RegistrationForm
from app.extensions import db, pages
from . import main

from app.main.models import Document, DocumentType, Term, TermStatus, \
    Category, Person, Link, Location, Table, \
    Column, Rule, Note

from app.users.models import User


###############################################################################
# Filters

@main.app_template_filter('env')
def env(value, key):
    '''Return environment variables for use on the admin settings page'''
    return getenv(key, value)


###############################################################################
# Context processors

@main.context_processor
def inject_pages():
    '''Returns pages that will be avaiables in every template view'''
    tagged = [p for p in pages if 'index' in p.meta.get('tags', [])]
    ordered = sorted(tagged, key=lambda p: p.meta['title'])
    return dict(tagged=ordered)


###############################################################################
# Routes

@main.route('/about')
def about():
    '''Present the about page'''
    from app import __VERSION__
    return render_template('about.html', version=__VERSION__)


@main.route('/')
@main.route('/glossary/')
@login_required
def glossary():
    '''Display the glossary main list of terms'''
    glossary = models.Term.query.order_by(Term.name).all()
    return render_template('show_glossary.html', glossary=glossary)


@main.route('/glossary_rules/')
@login_required
def glossary_rules():
    rules = Rule.query.order_by(Rule.identifier).all()
    return render_template('show_glossary_rules.html', rules=rules)


@main.route('/<path:path>/')
def page(path):
    '''Serve up markdown pages using Flask-FlatPages'''
    from app.extensions import pages
    page = pages.get_or_404(path)
    return render_template('flatpages/page.html', page=page)


@main.route('/tag/<string:tag>/')
def tag(tag):
    '''Handle FlatPages tags'''
    from app.extensions import pages
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('flatpages/tag.html', pages=tagged, tag=tag)


@main.route('/abbreviations/')
@login_required
def abbreviations():
    glossary = Term.query.filter(Term.abbreviation != "").order_by(Term.abbreviation).all()
    return render_template('show_abbreviations.html', glossary=glossary)


@main.route('/admin/backup/')
@roles_required('admin')
def show_backup():
    '''
    This route presents the backup and restore page from which the do_backup
    is called.
    '''
    return render_template('backup/backup_restore.html')


@main.route('/do_backup/', methods=['POST'])
@login_required
def do_backup():
    from app.loader import dump_yaml
    import time
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = "bg_export_" + timestr + ".yml"
    dump_yaml.dump(join(dirname(BASE_DIR), 'bg_interface', filename))
    return render_template('backup/do_backup.html', 
                           filename=filename,
                           function='Backup',
                           title='Backup Business Glossary Data')


@main.route('/do_column_association_export/', methods=['POST'])
@login_required
def do_column_association_export():
    from app.loader import export
    import time
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = "bg_column_associations_" + timestr + ".csv"
    export.export(join(dirname(BASE_DIR), 'bg_interface', filename))
    return render_template('backup/do_backup.html', 
                           filename=filename,
                           function='Export',
                           title='Column Associations Export')


@main.route('/generate_pdf/', methods=['POST'])
@login_required
def do_print():
    '''
    Generate a PDF of all glossary content
    '''
    categories = request.form.getlist("category")

    from app.print import generate_pdf
    import time
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = "glossary_" + timestr + ".pdf"
    generate_pdf(filename, categories)
    return render_template('print/print_finished.html', filename=filename)


@main.route('/download/<string:selected_filename>/')
@login_required
def download(selected_filename):
    try:
        return send_file(join(dirname(BASE_DIR), 'bg_interface', selected_filename),
                         as_attachment=True,
                         attachment_filename=selected_filename)
    except Exception as e:
        return str(e)


@main.route('/profile/')
@login_required
def profile():
    '''Present the user profile'''
    return render_template('users/show_profile.html')


@main.route('/term/<int:selected_term>')
@main.route('/term/<string:selected_term_name>')
@login_required
def show_term(selected_term=None, selected_term_name=None):

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


@main.route('/documents/<int:selected_term>')
@login_required
def show_documents(selected_term):
    documents = Document.query.order_by(Document.name).all()
    term = Term.query.filter_by(id=selected_term).first()
    documents = term.documents

    return render_template('show_documents.html', term=term, documents=documents)


@main.route('/assets/<int:selected_term>')
@login_required
def show_assets(selected_term):

    term = Term.query.filter_by(id=selected_term).first()
    assets = term.columns

    return render_template('show_assets.html', term=term, assets=assets)


@main.route('/rules/<int:selected_term>')
@login_required
def show_rules(selected_term):

    term = Term.query.filter_by(id=selected_term).first()
    rules = term.rules

    return render_template('show_rules.html', term=term, rules=rules)


@main.route('/rule/<int:selected_rule>')
@main.route('/rule/<string:selected_rule_name>')
@login_required
def show_rule(selected_rule=None, selected_rule_name=None):

    if selected_rule is None:
        rule = Rule.query.filter(func.lower(Rule.name) == func.lower(selected_rule_name)).first()
        if not rule:
            return render_template('errors/404.html')
        else:
            return render_template('show_rule.html', rule=rule)

    else:
        rule = Rule.query.filter_by(id=selected_rule).first()
        return render_template('show_rule.html', rule=rule)


@main.route('/rule/documents/<int:selected_rule>')
@login_required
def show_rule_documents(selected_rule):

    rule = Rule.query.filter_by(id=selected_rule).first()
    documents = rule.documents

    return render_template('show_rule_documents.html', rule=rule, documents=documents)


@main.route('/location/<selected_location>')
@main.route('/location/<selected_location>/details')
@login_required
def show_location_details(selected_location):

    location = Location.query.filter_by(id=selected_location).first()

    return render_template('show_location_details.html', location=location)


@main.route('/location/<selected_location>/tables')
@login_required
def show_location_tables(selected_location):

    location = Location.query.filter_by(id=selected_location).first()
    tables = location.tables

    return render_template('show_location_tables.html', location=location, tables=tables)


@main.route('/tables')
@login_required
def show_tables():

    tables = Table.query.all()

    return render_template('show_tables.html', tables=tables)


@main.route('/table/<selected_table>')
@main.route('/table/<selected_table>/details')
@login_required
def show_table_details(selected_table):

    table = Table.query.filter_by(id=selected_table).first()
    columns = table.columns

    return render_template('show_table_details.html', table=table, columns=columns)


@main.route('/table/<selected_table>/columns')
@login_required
def show_table_columns(selected_table):

    table = Table.query.filter_by(id=selected_table).first()
    columns = table.columns

    return render_template('show_table_columns.html', table=table, columns=columns)


@main.route('/search', methods=['GET', 'POST'])
@login_required
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


@main.route('/full_glossary')
@login_required
def full_glossary():
    '''
    Produce a PDF of the full glossary.
    '''
    terms = Term.query.order_by(Term.name).all()
    return render_template('print/full_glossary.html', terms=terms)


@main.route('/admin/users/')
@login_required
def show_users():
    users = User.query.all()
    return render_template('users/users.html', users=users)


@main.route('/user/<int:selected_user>')
@login_required
def show_user(selected_user):
    user = User.query.filter_by(id=selected_user).first()
    return render_template('users/user.html', user=user)


@main.route('/admin/user/create', methods=['GET', 'POST'])
@roles_required('admin')
def admin_create_user():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = encrypt_password(form.password.data)
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            form.email.errors.append(email + ' is already associated with another user')
            form.email.data = email
            email = ''
            return render_template('users/user_create.html', form=form)
        else:
            security = app.extensions.get('security')
            security.datastore.create_user(name=name,
                                           email=email,
                                           password=password,
                                           confirmed_at=datetime.now())
            db.session.commit()
            user = security.datastore.get_user(email)
            flash('User added successfully.')
            return redirect(url_for('main.show_users'))
    return render_template('users/user_create.html', form=form)


@main.route('/admin/settings/')
@login_required
def show_settings():
    return render_template('admin_settings.html')


@main.route('/admin/documents/')
@login_required
def admin_documents():
    documents = Document.query.all()
    document_check = []
    for document in documents:
        dp = join(BASE_DIR, 'app', 'static', 'files', document.path)
        print(" ***** File {}: {}".format(dp, isfile(dp)))
        doc = {
            'name': document.name,
            'path': document.path,
            'exists': isfile(join(BASE_DIR, 'app', 'static', 'files', document.path))
        }
        document_check.append(doc)
        print(document_check)

    return render_template('admin/show_documents.html', documents=document_check)
