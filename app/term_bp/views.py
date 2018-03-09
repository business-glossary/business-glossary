import os

from werkzeug.utils import secure_filename

from flask import abort, flash, redirect, render_template, url_for, request, jsonify, send_from_directory, Response
from flask_login import current_user, login_required

from sqlalchemy import exc
from app.term_bp.forms import TermForm, DocumentForm, RuleForm, LinkForm, RelatedTermForm, AssetForm, DemoForm
from app.config import BASE_DIR
from . import term_bp
from app.extensions import db
from app.models import Term, Document, Rule, Link, Table, Column


def check_admin():
    '''
    Prevent non-admins from accessing the page
    '''
    if not current_user.is_active:
        abort(403)


#########################################################################################
##
##  Term
##
#########################################################################################

@term_bp.route('/term/add', methods=['GET', 'POST'])
@login_required
def add_term():
    '''
    Add a term to the database
    '''
    check_admin()

    form = TermForm()

    if form.validate_on_submit():
        term = Term(name=form.name.data,
                    short_description=form.short_description.data,
                    long_description=form.long_description.data,
                    abbreviation=form.abbreviation.data,
                    status=form.status.data,
                    owner=form.owner.data,
                    steward=form.steward.data,
                    categories=form.categories.data)

        try:
            # Add term to the database
            db.session.add(term)
            db.session.commit()
            print(">>>> Added a new term")
            print(">>>>>>> %s" % term.id)
            flash('You have successfully added a new term.')
        except Exception as ex:
            print("Error %s occured." % ex)
            flash('An error occurred when adding the new term.')
        # Redirect to term page
        return redirect(url_for('main.show_term', selected_term=term.id))

    # Load term template
    return render_template('admin/terms/term.html',
                           action="Add",
                           form=form)


@term_bp.route('/term/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_term(id):
    '''
    Edit a term
    '''
    check_admin()

    term = Term.query.get_or_404(id)
    form = TermForm(obj=term)

    if form.validate_on_submit():
        # No cancel and submit are not used.
        term.name = form.name.data
        term.short_description = form.short_description.data
        term.long_description = form.long_description.data
        term.abbreviation = form.abbreviation.data
        term.status = form.status.data
        term.owner = form.owner.data
        term.steward = form.steward.data
        term.categories = form.categories.data

        db.session.commit()
        flash('You have successfully edited the term.')

        # Redirect to the terms page
        return redirect(url_for('main.show_term', selected_term=term.id))

    form.short_description.data = term.short_description
    form.long_description.data = term.long_description
    form.name.data = term.name
    form.abbreviation.data = term.abbreviation
    form.status.data = term.status
    form.owner.data = term.owner
    form.steward.data = term.steward
    form.categories.data = list(term.categories)
    return render_template('admin/terms/term.html',
                           action="Edit",
                           form=form,
                           term=term)


@term_bp.route('/term/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_term(id):
    '''
    Delete a term from the database
    '''
    check_admin()

    term = Term.query.get_or_404(id)
    db.session.delete(term)
    db.session.commit()

    # redirect to the terms page
    return redirect(url_for('main.glossary'))
    # Redirect to term page
    #return redirect(url_for('main.show_term', selected_term=1))


#########################################################################################
##                                                                                     ##
##  Print routine                                                                      ##
##                                                                                     ##
#########################################################################################

@term_bp.route('/term/print/<int:term_id>')
def print_report(term_id):

    import pdfkit
    import time

    pdf_directory = os.path.join(BASE_DIR, 'app', 'static', 'files')
    path = os.getenv("PATH")
    if "wkhtmltopdf" not in path:
        os.environ["PATH"] += os.pathsep + 'C:/Program Files/wkhtmltopdf/bin'

    timestr = time.strftime("%Y%m%d-%H%M%S")
    output_filename = "glossary_" + timestr + ".pdf"

    print(">> Generating PDF for term %s" % term_id)
    terms = Term.query.filter_by(id=term_id).all()
    print(terms)

    from flask import current_app

    html_text = render_template('print/glossary_print.html', terms=terms)

    options = {
        'page-size': 'A4',
        'dpi': 300,
        'margin-top': '20mm',
        'margin-right': '20mm',
        'margin-bottom': '20mm',
        'margin-left': '20mm',
        'encoding': "UTF-8",
        'header-left': "BOQ Credit Risk Analytics",
        'header-right': "Term Definition",
        'header-font-name': 'Roboto',
        'header-font-size': '8',
        'header-spacing': '10',
        'footer-left': '[date], [time]',
        'footer-right': 'Page [page] of [topage]',
        'footer-font-name': 'Roboto',
        'footer-font-size': '8',
        'footer-spacing': '10',
        'no-outline': None
    }

    css = os.path.join(BASE_DIR, 'app', 'static', 'css', 'print_style.css')
    cover = os.path.join(BASE_DIR, 'app', 'templates', 'print', 'cover_page.html')
    
    print("css=%s" % css)
    print("pdf_directory=%s" % pdf_directory)

    print(html_text)
    pdfkit.from_string(html_text, os.path.join(pdf_directory, output_filename), options=options, css=css)

    response = Response()
    response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Content-Length', str(os.path.getsize(os.path.join(pdf_directory, output_filename))))

    return send_from_directory(directory=pdf_directory,
                               filename=output_filename,

                               as_attachment=True,
                               mimetype='application/pdf')

#########################################################################################
##
##  Documents
##
#########################################################################################

@term_bp.route('/term/<int:term_id>/document/upload', methods=['GET', 'POST'])
@login_required
def upload_document(term_id):
    '''Upload a document to a term'''
    form = DocumentForm()
    if form.validate_on_submit() and request.method == 'POST':
        document = form.document.data
        print(document)
        filename = secure_filename(document.filename)
        # Save the document to the file system
        try:
            document.save(os.path.join(
                BASE_DIR, 'app', 'static', 'files', filename
            ))
            print("Success uploading document!")
        except Exception as ex:
            print("Error detected!")
            print("Error '{0}' occured. Arguments {1}.".format(ex.message, ex.args))

        # Now add document details to the database
        term = Term.query.filter_by(id=term_id).first()

        new_doc = Document(name=form.document_name.data,
                           description=form.document_description.data,
                           path=filename,
                           types=form.document_type.data)

        term.documents.append(new_doc)

        try:
            # Add the document to the database
            db.session.add(new_doc)
            db.session.commit()
            flash('You have successfully added the new document.')
        except:
            # In case term name already exists
            flash('Error occurred.')
        return redirect(url_for('main.show_term', selected_term=term_id))

    return render_template('admin/terms/document_upload.html',
                           form=form,
                           term_id=term_id)


@term_bp.route('/document/delete/<int:document_id>')
@login_required
def delete_document(document_id):
    '''
    Delete a document from the database and on disk

    :param document_id: The key of the document to delete
    :type document_id: int
    '''
    print("Referrer=%s" % request.referrer)
    print(document_id)
    document = Document.query.get_or_404(document_id)
    print(document.name)
    try:
        # Note that the document is deleted by the model
        db.session.delete(document)
        db.session.commit()
    except Exception as ex:
        print("Error %s occured." % ex)
        flash('An error occurred while deleting file.')

    # flash('You have successfully deleted the document.')

    return redirect(request.referrer)

#########################################################################################
##
##  Rule
##
#########################################################################################

#@term_bp.route('/term/<int:term_id>/rules/create', methods=['GET', 'POST'])
#@login_required
#def create_rule(term_id):
#    term = Term.query.filter(Term.id == term_id).first_or_404()
#    form = RuleForm()
#    if form.validate_on_submit():
#        rule = Rule()

#        rule.name = form.name.data
#        rule.identifier = form.identifier.data
#        rule.description = form.description.data
#        rule.notes = form.notes.data

#        term.rules.append(rule)

#        db.session.add(rule)
#        db.session.commit()
#        return jsonify(status='ok')
#    return render_template('rules/add.html', form=form)

@term_bp.route('/term/<int:term_id>/rules/create', methods=['GET', 'POST'])
@login_required
def create_rule(term_id):
    '''
    Add a rule to the database
    '''
    check_admin()

    term = Term.query.filter(Term.id == term_id).first_or_404()
    form = RuleForm()

    if form.validate_on_submit():
        rule = Rule()

        rule.name = form.name.data
        rule.identifier = form.identifier.data
        rule.description = form.description.data
        rule.notes = form.notes.data

        term.rules.append(rule)

        db.session.add(rule)
        db.session.commit()

        flash('You have successfully added the %s rule.' % rule.name)

        # Redirect to term page
        return redirect(url_for('main.show_term', selected_term=term.id))

    # Load term template
    return render_template('admin/rules/rule.html',
                           action="Add",
                           form=form)

#@term_bp.route('/rule/edit/<int:rule_id>', methods=['GET', 'POST'])
#@login_required
#def edit_rule(rule_id):
    #term = Term.query.filter(Term.id == term_id).first_or_404()
#    rule = Rule.query.filter(Rule.id == rule_id).first_or_404()
#    form = RuleForm(obj=rule)
#    if form.validate_on_submit():
#        rule.name = form.name.data
#        rule.identifier = form.identifier.data
#        rule.description = form.description.data
#        rule.notes = form.notes.data
#        db.session.commit()
        #flash('Successfully edited the rule.')
#        return jsonify(status='ok')
#    form.name.data = rule.name
#    form.identifier.data = rule.identifier
#    form.description.data = rule.description
#    form.notes.data = rule.notes
#    return render_template('rules/edit.html', form=form)

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

#@term_bp.route('/rule/edit/<int:rule_id>', methods=['GET', 'POST'])
@term_bp.route('/term/<int:term_id>/rule/<int:rule_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_rule(term_id, rule_id):
    '''
    Edit a rule
    '''
    check_admin()

    rule = Rule.query.filter(Rule.id == rule_id).first_or_404()
    form = RuleForm(obj=rule)

    if form.validate_on_submit():
        # No cancel and submit are not used.
        rule.name = form.name.data
        rule.identifier = form.identifier.data
        rule.description = form.description.data
        rule.notes = form.notes.data

        db.session.commit()
        flash('You have successfully edited the rule.')

        print(">> Referrer URL %s" % request.referrer)

        print(">> %s" % request.values)

        # Redirect to the terms page
        # Need to find the term ID
        return redirect(url_for('main.show_term', selected_term=term_id))

    form.name.data = rule.name
    form.identifier.data = rule.identifier
    form.description.data = rule.description
    form.notes.data = rule.notes

    return render_template('admin/rules/rule.html',
                           action="Edit",
                           form=form,
                           rule=rule,
                           term_id=term_id)

#########################################################################################
##
##  Link
##
#########################################################################################

@term_bp.route('/term/<int:term_id>/link/add/', methods=['GET', 'POST'])
@login_required
def add_link(term_id):
    '''
    Add a link to the database
    '''
    check_admin()

    form = LinkForm()

    if form.validate_on_submit():
        link = Link(text=form.text.data,
                    address=form.address.data)

        # Now add document details to the database
        term = Term.query.filter_by(id=term_id).first()
        term.links.append(link)

        try:
            # Add link to the database
            db.session.add(link)
            db.session.commit()
        except exc.IntegrityError as ex:
            # TODO: Return messsage to an error page?
            # return render_to_response("template.html", {"message": e.message})
            # Constraints etc.
            print(ex)
        except exc.OperationalError as ex:
            # TODO: Return messsage to an error page?
            # Database is locked or something
            print(ex)
        except Exception as ex:
            # In case link name already exists
            print(ex)
            flash('Error: link name already exists.')

        flash('You have successfully added a new link.')

        # Redirect to term page
        return redirect(url_for('main.show_term', selected_term=term_id))

    # Load term template
    return render_template('links/link.html',
                           action="Add",
                           term_id=term_id,
                           form=form)


@term_bp.route('/link/delete/<int:link_id>/', methods=['GET', 'POST'])
@login_required
def delete_link(link_id):
    '''
    Delete a link from the database and on disk

    :param link_id: The key of the document to delete
    :type link_id: int
    '''
    link = Link.query.get_or_404(link_id)
    try:
        db.session.delete(link)
        db.session.commit()
    except Exception as ex:
        print(ex)
        flash('Something went wrong.')
    return redirect(request.referrer)

#########################################################################################
##
##  Related Term
##
#########################################################################################

@term_bp.route('/term/<int:term_id>/related/add/', methods=['GET', 'POST'])
@login_required
def add_related_term(term_id):
    '''
    Add a related term
    '''
    check_admin()

    add_term = False

    term = Term.query.get_or_404(term_id)
    print("\n")
    print("Existing related terms: %s" % term.related_terms)
    form = RelatedTermForm(terms=term.related_terms)
    print("setup my query")
    my_query = Term.query.filter(Term.id != term_id).order_by(Term.name)
    print("add my query")
    form.terms.query = my_query
    print("my query done")

    print("here is query")
    print(form.terms.query)
    print("here is query_factory")
    print(form.terms.query_factory)

    if form.validate_on_submit():

        print("Forms data: %s" % form.terms.data)

        removed = list(set(term.related_terms).difference(form.terms.data))
        added = list(set(form.terms.data).difference(term.related_terms))

        print("XXX")
        print("removed: %s" % list(set(term.related_terms).difference(form.terms.data)))
        print("added: %s" % list(set(form.terms.data).difference(term.related_terms)))
        print("same: %s" % set(term.related_terms).intersection(form.terms.data))
        print("list set %s" % list(set(term.related_terms)- set(form.terms.data)))
        print("XXX\n")

        for removed_term in removed:
            term.unrelate(removed_term)
            print("Unrelated %s" % removed_term)

        for added_term in added:
            term.relate(added_term)
            print("Related %s" % added_term)

        #term = Term.query.filter_by(id=term_id).first()

        # term.related_terms = form.terms.data
        # Loop through the items selected in the list
        #for related_term in form.terms.data:
        #    print("term_name=%s" % related_term)
        #    term.related_terms.append(related_term)

        print("New related terms: %s" % term.related_terms)

        print("This term: %s" % term.name)
        print("\n")

        for rterm in term.related_terms:
            print("rterm.name: %s" % rterm.name)
            for rtermr in rterm.related_terms:
                print("The related terms' related terms:")
                print("  rterm.name: %s" % rterm.name)
                print("  rtermr.name: %s" % rtermr.name)
                if rtermr.name == term.name:
                    print("yes it's on the list")

        print("\n")
        db.session.commit()

        # Redirect to term page
        return redirect(url_for('main.show_term', selected_term=term_id))

    print("no validate")

    # Load term template
    return render_template('admin/terms/related_terms.html',
                           form=form,
                           term=term)

#########################################################################################
##
##  Asset
##
#########################################################################################

@term_bp.route('/term/<int:term_id>/assets/v1/', methods=['GET', 'POST'])
@login_required
def add_asset_v1(term_id):
    '''
    Add related assets.
    '''
    check_admin()

    term = Term.query.get_or_404(term_id)
    form = AssetForm(columns=term.columns)

    return render_template('admin/terms/assets_v1.html',
                           form=form,
                           term=term)
    #return render_template('admin/terms/assets1.html',
    #                       term=term)


@term_bp.route('/assets/list/')
@login_required
def list_assets():
    '''
    List all assets by table and column.
    '''

    tables = Table.query.limit(200)

    if tables:

        results = []

        for table in tables:

            tmp_table = {
                'text' : table.name
            }

            tmp_table['nodes'] = []

            for column in table.columns:

                tmp_child = {
                    'text': column.name
                }

                tmp_table['nodes'].append(tmp_child)

            results.append(tmp_table)

    print(results)

    return jsonify(results)


@term_bp.route('/term/<int:term_id>/assets/v2')
def add_assets_v2(term_id):
    term = Term.query.get_or_404(term_id)
    return render_template('admin/terms/assets_v2.html', term=term)


@term_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    #current_app.config['SQLALCHEMY_ECHO'] = False

    search = request.args.get('q')

    print(">> %s" % search)

    query = Column.query.filter(Column.name.like('%' + str(search) + '%'))

    results = [mv.name for mv in query.all()]

    # New attempt

    my_results = []

    for column in query:

        tmp_table = {
            'id': column.id,
            'location': column.table.location.name,
            'table': column.table.name,
            'column': column.name
        }

        my_results.append(tmp_table)

    return jsonify(matching_results=my_results)


@term_bp.route("/term/<int:term_id>/assets/v3", methods=["GET", "POST"])
def add_assets_v3(term_id):
    '''Relate assets to a term'''
    term = Term.query.get_or_404(term_id)
    print("\n**************")
    print("term.columns %s" % term.columns)
    print("**************\n")

    form = DemoForm(columns=term.columns)

    print("form.columns.data %s" % form.columns.data)

    if form.validate_on_submit():
        print(">> %s" % form.columns.data)

    print("Not validated")

    return render_template("admin/terms/assets_v3.html", form=form, term=term)


@term_bp.route("/term/<int:term_id>/assets/v4", methods=["GET", "POST"])
def add_assets_v4(term_id):
    '''Relate assets to a term'''

    #app.config['SQLALCHEMY_ECHO'] = False

    print("Grab term %s", term_id)
    term = Term.query.get_or_404(term_id)

    if request.method == "POST":
        print("Form submitted")

        selected = request.form.getlist('do_assign')

        print("Loop through selected columns")
        for selected_asset in selected:

            print("Grab column %s" % selected_asset)
            column = Column.query.filter_by(id=selected_asset).first()

            # If the term exists the add the column to term relationship
            term.columns.append(column)
            db.session.commit()

        # Redirect to term page
        return redirect(url_for('main.show_term', selected_term=term_id))

    return render_template("admin/terms/assets_v4.html", term=term)
