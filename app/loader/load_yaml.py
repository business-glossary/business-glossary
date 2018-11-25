# -*- coding: utf-8 -*-
#
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

'''Script to load data to the application database'''

import logging

import yaml

from os.path import dirname, join, isfile

from flask import current_app as app

from app import models
from app.extensions import db

from app.main.models import Term, TermStatus, Person, Category, Link, \
    Rule, Note, \
    Location, Table, Column, \
    Document, DocumentType

from sqlalchemy import and_

from app.config import BASE_DIR

LOGGER = logging.getLogger("business-glossary.load_data")


def remove_key(source_dict, *keys):
    '''Remove element(s) from a dictionary'''
    new_dict = dict(source_dict)
    for key in keys:
        # del new_dict[key]
        new_dict.pop(key, None)
    return new_dict


def add_rule(rule):
    '''Add a rule from a dict'''

    if db.session.query(Rule.id).filter_by(name=rule['name']).scalar():
        LOGGER.warning("Rule %s already exists", rule['name'])
        return

    #notes = rule['notes'].replace('\\n', '\n').replace('\\r', '\r')

    rule_to_load = remove_key(rule, 'terms')
    record = Rule(**rule_to_load)
    db.session.add(record)
    LOGGER.info("Loaded rule %s", rule['name'])

    # Get the rule again
    r = Rule.query.filter_by(identifier=rule['identifier']).first()

    for term_to_associate in rule['terms']:

        # Find the term to associate the rule with
        term = Term.query.filter_by(name=term_to_associate).first()

        # If the term is found associate with the rule
        if term:
            term.rules.append(r)
            LOGGER.info("Added rule %s to term %s", r.name, term_to_associate)
        else:
            LOGGER.warning("Could not find the term %s to associate with rule %s",
                           term_to_associate,
                           rule['name'])

    db.session.commit()


def add_term(term):
    '''Add a term from a dict'''

    if db.session.query(Term.id).filter_by(name=term['name']).scalar():
        LOGGER.warning("Term %s already exists", term['name'])
        return

    term_to_load = remove_key(term, 'owner', 'steward', 'status', 'categories')

    # Get the objects to associate
    status = TermStatus.query.filter_by(status=term['status']).first()
    owner = Person.query.filter_by(name=term['owner']).first()
    steward = Person.query.filter_by(name=term['steward']).first()

    term_to_load['steward'] = steward
    term_to_load['owner'] = owner
    term_to_load['status'] = status

    record = Term(**term_to_load)
    LOGGER.info("Loaded term %s", term['name'])

    for category_to_associate in term['categories']:

        # Find the term to associate the rule with
        category = Category.query.filter_by(name=category_to_associate).first()

        # If the term is found associate with the rule
        if category:
            record.categories.append(category)
            LOGGER.info("Added category %s to term %s", record.name, category_to_associate)
        else:
            LOGGER.warning("Added non-existent category %s to associate with term %s",
                           category_to_associate,
                           term['name'])
            category = Category(name=category_to_associate)
            db.session.add(category)
            record.categories.append(category)


    db.session.add(record)
    db.session.commit()


def add_person(person):
    '''Add a person from a dict'''

    if db.session.query(Person.id).filter_by(name=person['name']).scalar():
        LOGGER.warning("Person %s already exists", person['name'])
        return

    record = Person(**person)
    db.session.add(record)
    db.session.commit()
    LOGGER.info("Loaded %s", person['name'])


def add_term_status(term_status):
    '''Add a term status from a dict'''

    if db.session.query(TermStatus.id).filter_by(status=term_status['status']).scalar():
        LOGGER.warning("Term status %s already exists", term_status['status'])
        return

    record = TermStatus(**term_status)
    db.session.add(record)
    db.session.commit()
    LOGGER.info("Loaded %s", term_status['status'])


def add_document_type(document_type):
    '''Add a term status from a dict'''

    if db.session.query(DocumentType.id).filter_by(type=document_type['type']).scalar():
        LOGGER.warning("Document type %s already exists", document_type['type'])
        return

    record = DocumentType(**document_type)
    db.session.add(record)
    db.session.commit()
    LOGGER.info("Loaded %s", document_type['type'])


def add_location(location):
    '''Add a location from a dict'''

    if db.session.query(Location.id).filter_by(name=location['name']).scalar():
        LOGGER.warning("Location %s already exists", location['name'])
        return

    record = Location(**location)
    db.session.add(record)
    db.session.commit()
    LOGGER.info("Loaded %s", location['name'])


def add_category(category):
    '''Add a category from a dict'''

    if db.session.query(Category.id).filter_by(name=category['name']).scalar():
        LOGGER.warning("Category %s already exists", category['name'])
        return

    record = Category(**category)
    db.session.add(record)
    db.session.commit()
    LOGGER.info("Loaded %s", category['name'])


def add_table(table):
    '''Add a table from a dict'''

    # Check if the table already exists in the given location
    if Table.query.join(Location).filter(and_(Table.name == table['name'], Location.name ==  table['location'])).scalar():
        LOGGER.warning("Table %s already exists", table['name'])
        return

    table_to_load = remove_key(table, 'location')

    # Get the objects to associate
    location = Location.query.filter_by(name=table['location']).first()

    table_to_load['location'] = location
    
    record = Table(**table_to_load)
    db.session.add(record)
    db.session.commit()
    LOGGER.info("Loaded %s", table['name'])
    

def add_column(column):
    '''Add a column from a dict'''

    # Check if the column already exists in the given table
    if Table.query.join(Column).filter(and_(Table.name == column['table'], Column.name ==  column['name'])).scalar():
        LOGGER.warning("Column %s already exists in table %s", column['name'], column['table'])
        return

    # Remove the table and terms - we'll associate after this
    column_to_load = remove_key(column, 'table', 'terms')

    # Find the table to associate with
    table = Table.query.filter_by(name=column['table']).first()
    column_to_load['table'] = table

    record = Column(**column_to_load)

    # Associate with any terms
    if 'terms' in column:
        for term_to_associate in column['terms']:

            # Find the term to associate the rule with
            term = Term.query.filter_by(name=term_to_associate).first()

            # If the term is found associate with the column
            if term:
                record.terms.append(term)
                LOGGER.info("Associated column %s to term %s", record.name, term_to_associate)
            else:
                LOGGER.error("Could not find term %s to associate with column %s",
                                term_to_associate,
                                column['name'])

    db.session.add(record)
    db.session.commit()


def add_document(document):
    '''Add a document from a dict'''

    if db.session.query(Document.id).filter_by(name=document['name']).scalar():
        LOGGER.warning("Document %s already exists", document['name'])
        return

    # Remove the table and terms - we'll associate after this
    document_to_load = remove_key(document, 'types', 'terms')

    record = Document(**document_to_load)

    if 'terms' in document:
        for term_to_associate in document['terms']:

            # Find the term to associate the document with
            term = Term.query.filter_by(name=term_to_associate).first()

            # If the term is found associate with the document
            if term:
                record.terms.append(term)
                LOGGER.info("Associated document %s with term %s", record.name, term_to_associate)
            else:
                LOGGER.error("Could not find term %s to associate with document %s",
                                term_to_associate,
                                document['name'])



    for type_to_associate in document['types']:

        # Find the document type to associate the document with
        doc_type = DocumentType.query.filter_by(type=type_to_associate).first()

        # If the term is found associate with the document
        if doc_type:
            record.types.append(doc_type)
            LOGGER.info("Assigned type %s to category %s", record.name, type_to_associate)
        else:
            LOGGER.warning("Added non-existent type %s to associate with document %s",
                           type_to_associate,
                           record.name)
            doc_type = DocumentType(type=type_to_associate)
            db.session.add(doc_type)
            record.types.append(doc_type)

    db.session.add(record)
    db.session.commit()
    LOGGER.info("Loaded %s", document['name'])


def add_link(link):
    '''Add a link from a dict'''

    if db.session.query(Link.id).filter_by(text=link['text']).scalar():
        LOGGER.warning("Link %s already exists", link['text'])
        return

    # Remove the terms - we'll associate after this
    link_to_load = remove_key(link, 'term')

    # Find the Term to associate with
    term = Term.query.filter_by(name=link['term']).first()
    link_to_load['term'] = term

    record = Link(**link_to_load)    

    db.session.add(record)
    db.session.commit()
    LOGGER.info("Loaded %s", link['text'])


def add_related_terms(related_term):
    '''Add related term from a dict'''

    # Find the term to associate the related terms with
    term = Term.query.filter_by(name=related_term['term']).first()

    # If the term is found then we can look to associate
    if term:
        # Do things here
        for term_to_relate in related_term['related_terms']:
            # Find the other term
            rterm = Term.query.filter_by(name=term_to_relate).first()

            if rterm:
                term.relate(rterm)
                LOGGER.info("Added relationship between %s and %s", term.name, rterm.name)
                db.session.commit()
            else:                
                LOGGER.warning("Could not find the related term %s", term_to_relate)
    else:
        LOGGER.warning("Could not find the term %s with which to associate related terms",
                        related_term['term'])


def add_notes(note):
    '''Add notes from a dict'''

    # Remove the rule - we'll associate after this
    note_to_load = remove_key(note, 'rule')

    # Find the Rule to associate with
    rule = Rule.query.filter_by(name=note['rule']).first()
    note_to_load['rule'] = rule

    record = Note(**note_to_load)    

    db.session.add(record)
    db.session.commit()
    LOGGER.info("Loaded note for rule %s", note['rule'])


def load(file_name):
    '''Start the loading process'''
    log_format = "%(asctime)-15s [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    LOGGER.info("Starting import process")

    app.config['SQLALCHEMY_ECHO'] = False

    if not isfile(file_name):
        LOGGER.error("The file does not exist")
    else:
        with open(file_name, 'r') as stream:
            try:
                objects = yaml.load(stream)

                # Should be a dict of lists of dicts
                # If missing the record type then it will just be a list of dicts
                if not isinstance(objects, dict):
                    LOGGER.error("Please check the file format, it appears to be incorrect.")
                    return

                for obj in objects:
                    LOGGER.info("Found %s objects in file", obj)

                if 'person' in objects:
                    LOGGER.info("Loading people from file %s", file_name)
                    for obj in objects['person']:
                        add_person(obj)

                if 'term_status' in objects:
                    LOGGER.info("Loading term status from file %s", file_name)
                    for obj in objects['term_status']:
                        add_term_status(obj)

                if 'document_type' in objects:
                    LOGGER.info("Loading document types from file %s", file_name)
                    for obj in objects['document_type']:
                        add_document_type(obj)

                if 'location' in objects:
                    LOGGER.info("Loading locations from file %s", file_name)
                    for obj in objects['location']:
                        add_location(obj)

                if 'category' in objects:
                    LOGGER.info("Loading categories from file %s", file_name)
                    for obj in objects['category']:
                        add_category(obj)

                if 'terms' in objects:
                    LOGGER.info("Loading terms from file %s", file_name)
                    for obj in objects['terms']:
                        add_term(obj)

                if 'rules' in objects:
                    LOGGER.info("Loading rules from file %s", file_name)
                    for obj in objects['rules']:
                        add_rule(obj)

                if 'tables' in objects:
                    LOGGER.info("Loading tables from file %s", file_name)
                    for obj in objects['tables']:
                        add_table(obj)

                if 'columns' in objects:
                    LOGGER.info("Loading columns from file %s", file_name)
                    for obj in objects['columns']:
                        add_column(obj)

                if 'documents' in objects:
                    LOGGER.info("Loading documents from file %s", file_name)
                    for obj in objects['documents']:
                        add_document(obj)

                if 'links' in objects:
                    LOGGER.info("Loading links from file %s", file_name)
                    for obj in objects['links']:
                        add_link(obj)

                if 'related_terms' in objects:
                    LOGGER.info("Loading term relations from file %s", file_name)
                    for obj in objects['related_terms']:
                        add_related_terms(obj)

                if 'notes' in objects:
                    LOGGER.info("Loading notes from file %s", file_name)
                    for obj in objects['notes']:
                        add_notes(obj)

                LOGGER.info("Import process ended.")

            except yaml.YAMLError as ex:
                print(ex)
