from app import app, db
from flask import render_template, request, flash, session, url_for, redirect, jsonify, send_from_directory
from models import Document, DocumentType, Term, Category, Person, Link, Table, Column, Rule
import os
import os.path as op

from flask_admin import Admin, form
from flask_admin.contrib.sqla import ModelView

# Create directory for file fields to use
file_path = op.join(op.dirname(__file__), 'static/files')

print "file_path=", file_path

try:
    os.mkdir(file_path)
except OSError:
    pass

# Administrative views

class FileView(ModelView):
	# Override form field to use Flask-Admin FileUploadField
	form_overrides = {
		'path': form.FileUploadField
	}

	# Pass additional parameters to 'path' to FileUploadField constructor
	form_args = {
		'path': {
			'label': 'File',
			'base_path': file_path,
			'allow_overwrite': False
		}
	}

class RuleView(ModelView):
    form_excluded_columns = ('created_on', 'updated_on')

class TermView(ModelView):
	form_excluded_columns = ('created_on', 'updated_on')
	column_searchable_list = ['term']

class ColumnView(ModelView):
	column_filters = ['table', 'name']

admin = Admin(app, name='BUSINESS GLOSSARY', template_mode='bootstrap3', base_template='/admin/new_master.html')
admin.add_view(ModelView(Category, db.session))
admin.add_view(TermView(Term, db.session))
admin.add_view(ModelView(Person, db.session))
admin.add_view(ModelView(Link, db.session))
admin.add_view(ModelView(Table, db.session))
admin.add_view(ColumnView(Column, db.session))
admin.add_view(FileView(Document, db.session))
admin.add_view(ModelView(DocumentType, db.session))
admin.add_view(RuleView(Rule, db.session))

# Now define the routes

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/')
def glossary():
	return render_template('show_glossary.html', glossary = Term.query.order_by(Term.term).all())

@app.route('/term/<int:selected_term>')
def show_term(selected_term):
	return render_template('show_term.html', term = Term.query.filter_by(id=selected_term).first())

@app.route('/documents/<int:selected_term>')
def show_documents(selected_term):
	documents = Document.query.order_by(Document.name).all()

	term = Term.query.filter_by(id=selected_term).first()

	documents = term.documents

	print "Documents...."

	print documents

	return render_template('show_documents.html', term=term, documents=Document.query.order_by(Document.name).all())

@app.route('/assets/<int:selected_term>')
def show_assets(selected_term):

	term = Term.query.filter_by(id=selected_term).first()
	assets = term.columns

	print assets

	return render_template('show_assets.html', term=term, assets=assets)

@app.route('/rules/<int:selected_term>')
def show_rules(selected_term):

	term = Term.query.filter_by(id=selected_term).first()
	rules = term.rules

	return render_template('show_rules.html', term=term, rules=rules)

@app.route('/rule/<int:selected_rule>')
def show_rule(selected_rule):

	rule = Rule.query.filter_by(id=selected_rule).first()

	return render_template('show_rule.html', rule=rule)

@app.route('/tables/<selected_location>')
def show_tables(selected_location):

	tables = Table.query.filter_by(location=selected_location).all()

	return render_template('show_tables.html', selected_location=selected_location, tables=tables)

@app.route('/table/<selected_table>')
@app.route('/table/<selected_table>/details')
def show_table_details(selected_table):

	table = Table.query.filter_by(id=selected_table).first()
	columns = table.columns

	return render_template('show_table_details.html', table=table, columns=columns)

@app.route('/table/<selected_table>/columns')
def show_table_columns(selected_table):

	table = Table.query.filter_by(id=selected_table).first()
	columns = table.columns

	return render_template('show_table_columns.html', table=table, columns=columns)
	
	
# Testing

@app.route('/source_code')
def source_code():
	filename = '05_ACCT HIST.sas'
	root_dir = os.path.dirname(os.getcwd())
	print root_dir
	return send_from_directory(os.path.join('.', 'static', 'source_code'), filename, as_attachment=False, mimetype='text/html')
