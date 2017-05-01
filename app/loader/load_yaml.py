# -*- coding: utf-8 -*-
'''Script to load data to the application database'''

import logging

import yaml

from os.path import dirname, join, isfile

from app import db, app
from app.models import Term, Rule, Person, TermStatus, DocumentType, Location, Category

from config import BASE_DIR

LOGGER = logging.getLogger("business-glossary.load_data")

#file_path = join(dirname(BASE_DIR), 'bg_interface')
#file_name = os.path.join(file_path, "rules.yaml")

def remove_key(source_dict, *keys):
    '''Remove element(s) from a dictionary'''
    new_dict = dict(source_dict)
    for key in keys:
        del new_dict[key]
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


def load(file_name):
    '''Start the loading process'''
    log_format = "%(asctime)-15s [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    LOGGER.info("Starting import process")

    app.config['SQLALCHEMY_ECHO'] = False

    if not isfile(file_name):
        LOGGER.error("The file does not exist")
    else:
        print("b4 open")
        with open(file_name, 'r') as stream:
            print("after open")
            try:
                print("b4 load")
                print(stream)
                objects = yaml.load(stream)
                print("after load")

                # Should be a dict of lists of dicts
                # If missing the record type then it just be a list of dicts
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

                if 'term' in objects:
                    LOGGER.info("Loading terms from file %s", file_name)
                    for obj in objects['term']:
                        add_term(obj)

                if 'rule' in objects:
                    LOGGER.info("Loading rules from file %s", file_name)
                    for obj in objects['rule']:
                        add_rule(obj)


            except yaml.YAMLError as ex:
                print(ex)
