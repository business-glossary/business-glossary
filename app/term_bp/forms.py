from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField
from flask_wtf.file import FileField, FileRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from flask_admin.form.widgets import Select2Widget
from wtforms.validators import DataRequired, URL, Required

from ..models import Term, TermStatus, Person, Category, DocumentType, Rule


class TermForm(FlaskForm):
    '''
    Form for admin to add or edit a Term
    '''
    name = StringField('Name', validators=[DataRequired('Please enter the term name.')])
    short_description = TextAreaField('Short Description',
                                      validators=[DataRequired('Please enter a short description.')])
    long_description = TextAreaField('Long Description', validators=[DataRequired('Please enter a long description.')])
    abbreviation = StringField('Abbrevation')
    categories = QuerySelectMultipleField(query_factory=lambda: Category.query.all(),
                                          get_label="name",
                                          widget=Select2Widget())
    owner = QuerySelectField(query_factory=lambda: Person.query.all(),
                             get_label="name",
                             widget=Select2Widget())
    steward = QuerySelectField(query_factory=lambda: Person.query.all(),
                               get_label="name",
                               widget=Select2Widget())
    status = QuerySelectField(query_factory=lambda: TermStatus.query.all(),
                              get_label="status",
                              widget=Select2Widget())
    save = SubmitField('Save')
    cancel = SubmitField('Cancel')


class DocumentForm(FlaskForm):
    '''
    Form for uploading documents
    '''
    document_name = StringField('Name', validators=[DataRequired("Enter a name for the document.")])
    document_description = StringField('Description',
                                       validators=[DataRequired('Enter a description of the document.')])
    document = FileField('Select a document', validators=[FileRequired('Select a document')])
    document_type = QuerySelectMultipleField(query_factory=lambda: DocumentType.query.all(),
                                             get_label="type",
                                             validators=[Required()])
    submit = SubmitField(label="Upload")


class RuleForm(FlaskForm):
    '''
    Form for entering new rules
    '''
    name = StringField('Name', validators=[DataRequired()])
    identifier = StringField('Indentifier', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[DataRequired()])
    submit = SubmitField('OK')


class LinkForm(FlaskForm):
    '''
    Form for entering new links
    '''
    text = StringField('Text', validators=[DataRequired('Please enter descriptive text for the link')])
    address = StringField('Address', validators=[URL('Please enter a valid URL')])
    submit = SubmitField('Submit')


class RelatedTermForm(FlaskForm):
    '''
    Form for entering related links
    '''
    terms = QuerySelectMultipleField(get_label="name")
#    terms = QuerySelectMultipleField(query_factory=lambda: Term.query.order_by(Term.name).all(),
 #                                    get_label="name")
    submit = SubmitField("Submit")
