from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.term_bp.forms import TermForm
from . import term_bp
from .. import db
from ..models import Term


def check_admin():
    '''
    Prevent non-admins from accessing the page
    '''
    if not current_user.is_active:
        abort(403)

# Term Views

@term_bp.route('/term/add', methods=['GET', 'POST'])
@login_required
def add_term():
    '''
    Add a term to the database
    '''
    check_admin()

    add_term = True

    form = TermForm()
    print "^^^^", form
    if form.validate_on_submit():
        term = Term(term=form.term.data,
                    description=form.description.data,
                    abbreviation=form.abbreviation.data)
        try:
            # add term to the database
            db.session.add(term)
            db.session.commit()
            flash('You have successfully added a new term.')
        except:
            # in case term name already exists
            flash('Error: term name already exists.')

        # redirect to term page
        return redirect(url_for('main.show_term', selected_term=1))

    # load term template
    return render_template('admin/terms/term.html', action="Add",
                           add_term=add_term, form=form,
                           title="Add Term")


@term_bp.route('/term/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_term(id):
    '''
    Edit a term
    '''
    check_admin()

    add_term = False

    print ">>", id

    term = Term.query.get_or_404(id)
    print ">>", term.term
    print ">>", term.description
    form = TermForm(obj=term)
    if form.validate_on_submit():
        term.term = form.term.data
        term.description = form.description.data
        term.abbreviation = form.abbreviation.data
        term.status = form.status.data
        term.owner = form.owner.data
        term.steward = form.steward.data
        term.categories = form.categories.data

        db.session.commit()
        flash('You have successfully edited the term.')

        # redirect to the terms page
        return redirect(url_for('main.show_term', selected_term=term.id))

    form.description.data = term.description
    form.term.data = term.term
    form.abbreviation.data = term.abbreviation
    form.status.data = term.status
    form.owner.data = term.owner
    form.steward.data = term.steward
    form.categories.data = list(term.categories)
    return render_template('admin/terms/term.html', action="Edit",
                           add_term=add_term, form=form,
                           term=term, title="Edit Term")


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
    flash('You have successfully deleted the term.')

    # redirect to the terms page
    return redirect(url_for('main.glossary'))

    return render_template(title="Delete Term")


