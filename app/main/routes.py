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

from os import mkdir
from os.path import dirname, join

from flask import render_template, request, send_from_directory, send_file
from flask import current_app

from flask_flatpages import pygments_style_defs
from flask_security import current_user
from flask_flatpages import FlatPages
from sqlalchemy import func
from app import models
from app.config import BASE_DIR
from . import main

from app.main.models import Document, DocumentType, Term, TermStatus, Category, Person, Link, Location, Table, \
    Column, Rule, Note

from flask import current_app as app

pages = FlatPages(app)

@main.context_processor
def inject_pages():
    """
    Returns pages that will be avaiables in every template view
    """
    from app.extensions import pages
    tagged = [p for p in pages if 'index' in p.meta.get('tags', [])]
    
    ordered = sorted(tagged, key=lambda p: p.meta['title'])
       
    return dict(tagged=ordered)

###########################
#### define the routes ####
###########################

@main.route('/about')
def about():
    '''Present the about page'''
    from app import __VERSION__
    return render_template('about.html', version=__VERSION__)


@main.route('/')
@main.route('/glossary/')
def glossary():
    '''Display the glossary main list of terms'''
    glossary = models.Term.query.order_by(Term.name).all()
    return render_template('show_glossary.html', glossary=glossary)


@main.route('/glossary_rules/')
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


@main.route('/generate_pdf/', methods=['POST'])
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
@main.route('/rule/<string:selected_rule_name>')
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


###########################################
## Produce PDF
###########################################

@main.route('/full_glossary')
def full_glossary():
    terms = Term.query.order_by(Term.name).all()
    return render_template('print/full_glossary.html', terms=terms)


###########################################
## Proof-of-concept type code
###########################################

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
