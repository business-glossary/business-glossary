from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired

from ..models import Term, TermStatus, Person, Category


class TermForm(FlaskForm):
    '''
    Form for admin to add or edit a Term
    '''
    term = StringField('Term', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    abbreviation = StringField('Abbrevation', validators=[DataRequired()])
    status = QuerySelectField(query_factory=lambda: TermStatus.query.all(),
                              get_label="status")
    owner = QuerySelectField(query_factory=lambda: Person.query.all(),
                             get_label="name")
    steward = QuerySelectField(query_factory=lambda: Person.query.all(),
                               get_label="name")
    categories = QuerySelectMultipleField(query_factory=lambda: Category.query.all(),
                                  get_label="name")
    save = SubmitField('Save')

