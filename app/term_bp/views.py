import os

from werkzeug.utils import secure_filename

from flask import abort, flash, redirect, render_template, url_for, request, jsonify
from flask_login import current_user, login_required

from sqlalchemy import exc
from app.term_bp.forms import TermForm, DocumentForm, RuleForm, LinkForm, RelatedTermForm
from . import term_bp
from .. import db
from ..models import Term, Document, Rule, Link

from config import BASE_DIR

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
            flash('You have successfully added a new term.')
        except:
            # In case term name already exists
            flash('Error: term name already exists.')

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
##
##  Documents
##
#########################################################################################

@term_bp.route('/term/<int:term_id>/document/upload', methods=['GET', 'POST'])
@login_required
def upload_document(term_id):
    '''Upload a document to a term'''
    form = DocumentForm()
    if form.validate_on_submit():
        document = form.document.data
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
    except:
        flash('Something went wrong.')

    # flash('You have successfully deleted the document.')

    return redirect(request.referrer)

#########################################################################################
##
##  Rule
##
#########################################################################################

@term_bp.route('/term/<int:term_id>/rules/create', methods=['GET', 'POST'])
@login_required
def create_rule(term_id):
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
        return jsonify(status='ok')
    return render_template('rules/add.html', form=form)


@term_bp.route('/rule/edit/<int:rule_id>', methods=['GET', 'POST'])
@login_required
def edit_rule(rule_id):
    #term = Term.query.filter(Term.id == term_id).first_or_404()
    rule = Rule.query.filter(Rule.id == rule_id).first_or_404()
    form = RuleForm(obj=rule)
    if form.validate_on_submit():
        rule.name = form.name.data
        rule.identifier = form.identifier.data
        rule.description = form.description.data
        rule.notes = form.notes.data
        db.session.commit()
        #flash('Successfully edited the rule.')
        return jsonify(status='ok')
    form.name.data = rule.name
    form.identifier.data = rule.identifier
    form.description.data = rule.description
    form.notes.data = rule.notes
    return render_template('rules/edit.html', form=form)

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
    print(term.related_terms)
    print("\n")
    form = RelatedTermForm(terms=term.related_terms)

    if form.validate_on_submit():

        print(form.terms.data)

        if form.terms.data:
            term = Term.query.filter_by(id=term_id).first()

            term.related_terms = form.terms.data
            # Loop through the items selected in the list
            #for related_term in form.terms.data:
            #    print("term_name=%s" % related_term)
            #    term.related_terms.append(related_term)

            db.session.commit()
        else:
            print("Nothing to do, form was empty.")

        try:
            # db.session.add(link)
            # db.session.commit()
            print("Trying to add relationship")
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

        # Redirect to term page
        return redirect(url_for('main.show_term', selected_term=term_id))

    print("no validate")

    # Load term template
    return render_template('admin/terms/related_terms.html',
                           form=form,
                           term=term)

#########################################################################################
##
##  Term
##
#########################################################################################

@term_bp.route('/term/<int:term_id>/asset/add/', methods=['GET', 'POST'])
@login_required
def add_asset(term_id):
    '''
    Add a related asset
    '''
    check_admin()

    return render_template('admin/terms/asset.html',
                           form=form,
                           term=term)