import datetime
import os
import os.path as op

from sqlalchemy.event import listens_for

from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime

from app import db

file_path = op.join(op.dirname(__file__), 'static/files')

term_category_relationship = db.Table('term_category_relationship',
                                      db.Column('term_id',
                                                db.Integer,
                                                db.ForeignKey('term.id'),
                                                nullable=False),
                                      db.Column('category_id',
                                                db.Integer,
                                                db.ForeignKey('category.id'),
                                                nullable=False),
                                      db.PrimaryKeyConstraint('term_id', 'category_id'))

document_types_relationship = db.Table('document_types_table',
                                       db.Column('document_id',
                                                 db.Integer,
                                                 db.ForeignKey('document.id'),
                                                 nullable=False),
                                       db.Column('document_type_id',
                                                 db.Integer,
                                                 db.ForeignKey('document_type.id'),
                                                 nullable=False),
                                       db.PrimaryKeyConstraint('document_id', 'document_type_id'))

term_column_relationship = db.Table('term_column_relationship',
                                    db.Column('term_id',
                                              db.Integer,
                                              db.ForeignKey('term.id'),
                                              nullable=False),
                                    db.Column('column_id',
                                              db.Integer,
                                              db.ForeignKey('column.id'),
                                              nullable=False),
                                    db.PrimaryKeyConstraint('term_id', 'column_id'))

term_document_relationship = db.Table('term_document_relationship',
                                      db.Column('term_id',
                                                db.Integer,
                                                db.ForeignKey('term.id'),
                                                nullable=False),
                                      db.Column('document_id',
                                                db.Integer,
                                                db.ForeignKey('document.id'),
                                                nullable=False),
                                      db.PrimaryKeyConstraint('term_id', 'document_id'))

term_rule_relationship = db.Table('term_rule_relationship',
                                  db.Column('term_id',
                                            db.Integer,
                                            db.ForeignKey('term.id'),
                                            nullable=False),
                                  db.Column('rule_id',
                                            db.Integer,
                                            db.ForeignKey('rule.id'),
                                            nullable=False),
                                  db.PrimaryKeyConstraint('term_id', 'rule_id'))

rule_document_relationship = db.Table('rule_document_relationship',
                                      db.Column('rule_id',
                                                db.Integer,
                                                db.ForeignKey('rule.id'),
                                                nullable=False),
                                      db.Column('document_id',
                                                db.Integer,
                                                db.ForeignKey('document.id'),
                                                nullable=False),
                                      db.PrimaryKeyConstraint('rule_id', 'document_id'))

term_to_term_relationship = db.Table('term_to_term_relationship',
                                     db.Column('term_id',
                                               db.Integer,
                                               db.ForeignKey('term.id'),
                                               primary_key=True),
                                     db.Column('related_term_id',
                                               db.Integer,
                                               db.ForeignKey('term.id'),
                                               primary_key=True))

class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    short_description = db.Column(db.String(100))
    long_description = db.Column(db.Text)
    abbreviation = db.Column(db.String(10))

    categories = db.relationship('Category', secondary=term_category_relationship, backref='terms')

    columns = db.relationship('Column', secondary=term_column_relationship, backref='terms')

    documents = db.relationship('Document', secondary=term_document_relationship, backref='terms')

    rules = db.relationship('Rule', secondary=term_rule_relationship, backref='terms')

    links = db.relationship('Link', backref="terms", cascade="all, delete-orphan", lazy='dynamic')

    status_id = db.Column(db.Integer, db.ForeignKey('term_status.id'))
    status = db.relationship('TermStatus', backref=db.backref('terms', lazy='dynamic'))

    owner_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    steward_id = db.Column(db.Integer, db.ForeignKey('person.id'))

    owner = db.relationship('Person', foreign_keys=[owner_id])
    steward = db.relationship('Person', foreign_keys=[steward_id])

    related_terms = db.relationship("Term",
                                    secondary=term_to_term_relationship,
                                    primaryjoin=id == term_to_term_relationship.c.term_id,
                                    secondaryjoin=id == term_to_term_relationship.c.related_term_id,
                                    backref="related_to")

    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return self.term

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

class TermStatus(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    status = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return self.status

class Category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(50))

    def __repr__(self):
        return self.name

class Link(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(200), unique=True, nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))

    def __repr__(self):
        return self.text

class Person(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name

class Location (db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    host = db.Column(db.String(50))
    description = db.Column(db.String(100))
    path = db.Column(db.String(100))
    notes = db.Column(db.String(100))

    def __repr__(self):
        return self.name

class Table(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(length=100))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship("Location", backref=db.backref('tables', lazy='dynamic'))

    def __repr__(self):
        return self.name

class Column(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100))
    type = db.Column(db.String(50))
    length = db.Column(db.String(10))
    format = db.Column(db.String(50))

    table_id = db.Column(db.Integer, db.ForeignKey('table.id'))
    table = db.relationship("Table", backref=db.backref('columns', lazy='dynamic'))

    def __repr__(self):
        return self.name

class Rule(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    identifier = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    documents = db.relationship('Document', secondary=rule_document_relationship, backref='rules')

    def __repr__(self):
        return self.name

class Document(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    path = db.Column(db.String(100))
    description = db.Column(db.String(200))

    types = db.relationship('DocumentType', secondary=document_types_relationship)

    def __repr__(self):
        return self.name

class DocumentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(45))

    def __repr__(self):
        return self.type

    def __unicode__(self):
        return self.type

@listens_for(Document, 'after_delete')
def del_file(mapper, connection, target):
    '''Delete hooks for models, delete files if models are getting deleted'''
    print("file_path=", file_path)

    if target.path:
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            # Don't care if was not deleted because it does not exist
            pass
