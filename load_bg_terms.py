import logging

import csv

from os.path import dirname, join

from app import app, db
from app.models import Category, Term, Person, TermStatus, Link, DocumentType, Rule

from config import BASE_DIR

app.config['SQLALCHEMY_ECHO'] = False

LOGGER = logging.getLogger("business-glossary.load_data")

def load_term_status(file_name):
    '''
    Load term status from CSV file

    :param file_Name: The name of the CSV file to load from
    '''
    LOGGER.info("Loading term status")

    with open(file_name, 'rt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            LOGGER.info("Loaded %s", row['status'])

            record = TermStatus(**{
                'status' : row['status']
                })
            db.session.add(record)
            db.session.commit()


def load_categories(file_name):
    '''
    Load categories from CSV file

    :param file_Name: The name of the CSV file to load from
    '''
    LOGGER.info("Loading categories")

    with open(file_name, 'rt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            LOGGER.info("Loaded %s", row['category'])

            record = Category(**{
                'name' : row['category'],
                'description' : row['description']
                })
            db.session.add(record)
            db.session.commit()



def load_document_types(file_name):
    '''
    Load document types from CSV file

    :param file_Name: The name of the CSV file to load from
    '''
    LOGGER.info("Loading document types")

    with open(file_name, 'rt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            LOGGER.info("Loaded %s", row['document_type'])

            record = DocumentType(**{
                'type' : row['document_type']
                })
            db.session.add(record)
            db.session.commit()



def load_persons(file_name):
    '''
    Load people from CSV file

    :param file_Name: The name of the CSV file to load from
    '''
    LOGGER.info("Loading people")

    with open(file_name, 'rt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            LOGGER.info("Loaded %s", row['person'])

            record = Person(**{
                'name' : row['person']
                })
            db.session.add(record)
            db.session.commit()


def load_terms(file_name):
    '''
    Load terms from CSV file

    :param file_Name: The name of the CSV file to load from
    '''
    LOGGER.info("Loading terms")

    with open(file_name, 'rt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            LOGGER.info("Loaded %s", row['name'])

            s = TermStatus.query.filter_by(status=row['status']).first()
            o = Person.query.filter_by(name=row['owner']).first()
            st = Person.query.filter_by(name=row['steward']).first()

            record = Term(**{
                'name' : row['name'],
                'short_description' : row['short_description'],
                'long_description' : row['long_description'],
                'abbreviation' : row['abbreviation'],
                'status' : s,
                'owner' : o,
                'steward' : st
                })
            db.session.add(record)

            db.session.commit()


def load_term_categories(file_name):
    '''
    Load term category relationships from CSV file

    :param file_Name: The name of the CSV file to load from
    '''
    LOGGER.info("Loading term to category associations")

    with open(file_name, 'rt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            LOGGER.info("Associated %s with the %s category", row['term'], row['category'])

            t = Term.query.filter_by(name=row['term']).first()
            c = Category.query.filter_by(name=row['category']).first()

            t.categories.append(c)

            db.session.commit()


def load_links(file_name):
    '''
    Load links from CSV file

    :param file_Name: The name of the CSV file to load from
    '''
    LOGGER.info("Loading links")

    with open(file_name, 'rt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            LOGGER.info("Loaded %s", row['text'])

            record = Link(**{
                'text' : row['text'],
                'address' : row['address']
                })
            db.session.add(record)

            t = Term.query.filter_by(name=row['term']).first()
            l = Link.query.filter_by(text=row['text']).first()

            t.links.append(l)

            db.session.commit()


def load_rules(file_name):
    '''
    Load rules from CSV file

    :param file_Name: The name of the CSV file to load from
    '''
    LOGGER.info("Loading rules")

    with open(file_name, 'rt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:

            notes = row['notes'].replace('\\n', '\n').replace('\\r', '\r')

            # Add the rule
            record = Rule(**{
                'identifier' : row['identifier'],
                'name' : row['name'],
                'description' : row['description'],
                'notes' : notes
                })
            db.session.add(record)

            # Get the rule again
            r = Rule.query.filter_by(identifier=row['identifier']).first()

            # Find the term to associate with
            t = Term.query.filter_by(name=row['term']).first()

            # If the term is found associate with the rule
            if t:
                t.rules.append(r)
                LOGGER.info("Rule %s loaded", r.name)
            else:
                LOGGER.warning("Associated term %s not found for rule %s", row['term'], row['name'])

            db.session.commit()

if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)-15s [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    LOGGER.info("Load process started")

    # Interface files are placed in a directory name bg_interface at the same level
    # as the application directory, i.e.
    #
    #   - bg_interface
    #   - business_glossary
    #
    # Call os.path.dirname twice to walk up to the parent directory

    FILE_PATH = join(dirname(BASE_DIR), 'bg_interface')

    db.drop_all()
    db.create_all()

    load_term_status(join(FILE_PATH, "bg_interface_status.csv"))
    load_categories(join(FILE_PATH, "bg_interface_category.csv"))
    load_document_types(join(FILE_PATH, "bg_interface_document_type.csv"))
    load_persons(join(FILE_PATH, "bg_interface_person.csv"))
    load_terms(join(FILE_PATH, "bg_interface_terms.csv"))
    load_term_categories(join(FILE_PATH, "bg_interface_categories.csv"))
    load_links(join(FILE_PATH, "bg_interface_links.csv"))
    load_rules(join(FILE_PATH, "bg_interface_rules.csv"))

    LOGGER.info("Load process ended")