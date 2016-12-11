'''Dump data to yaml'''

import logging

import yaml

from app import app, db, models
from app.models import Category, Term, Person, TermStatus, Link, Location, Table, \
    Column, DocumentType, Rule

from config import BASE_DIR

app.config['SQLALCHEMY_ECHO'] = False

LOGGER = logging.getLogger("business-glossary.dump_data")


class folded_unicode(unicode):
    pass
class literal_unicode(unicode):
    pass

def folded_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='>')
def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(folded_unicode, folded_unicode_representer)
yaml.add_representer(literal_unicode, literal_unicode_representer)

class quoted(str): pass

def quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

class literal(str): pass

def literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(quoted, quoted_presenter)
yaml.add_representer(literal, literal_presenter)

#def ordered_dict_presenter(dumper, data):
#    return dumper.represent_dict(data.items())
#yaml.add_representer(OrderedDict, ordered_dict_presenter)


def return_categories(term):
    '''Return category names as a list when dumping terms'''
    cats = []
    for cat in term.categories:
        cats.append(cat.name)
    return cats

def return_terms(rule):
    '''Return the terms a rule belongs to as a list'''
    terms = []
    for term in rule.terms:
        terms.append(term.term)
    return terms

def prep_terms():
    '''Return terms as a dictionary'''
    LOGGER.info("Dumping Term")
    terms = Term.query.all()

    my_terms = []

    for term in terms:
        my_term = {
            "term": term.term,
            "description": term.description,
            "abbreviation": term.abbreviation,
            "status": term.status.status,
            "categories": return_categories(term),
            "owner": term.owner.name,
            "steward": term.steward.name,
            "created_on": term.created_on,
            "updated_on": term.updated_on
        }
        my_terms.append(my_term)
    return my_terms

def prep_rules():
    '''Return rules as a dictionary'''
    LOGGER.info("Dumping Rule")
    rules = Rule.query.all()

    my_rules = []

    for rule in rules:
        my_rule = {
            "identifier": rule.identifier,
            "name": rule.name,
            "description": rule.description,
            "notes": rule.notes,
            "created_on": rule.created_on,
            "updated_on": rule.updated_on,
            "terms": return_terms(rule)
        }
        my_rules.append(my_rule)
    return my_rules

def prep_person():
    '''Return people as a dictionary'''
    LOGGER.info("Dumping Person")
    people = Person.query.all()
    my_people = []
    for person in people:
        this_person = {
            "name": person.name,
        }
        my_people.append(this_person)
    return my_people

def prep_category():
    '''Return category as a dictionary'''
    LOGGER.info("Dumping Category")
    categories = Category.query.all()
    my_category = []
    for category in categories:
        this_category = {
            "name": category.name,
            "description": category.description
        }
        my_category.append(this_category)
    return my_category

def prep_term_status():
    '''Return term status as a dictionary'''
    LOGGER.info("Dumping TermStatus")
    status = TermStatus.query.all()
    my_status = []
    for stat in status:
        this_status = {
            "status": stat.status,
        }
        my_status.append(this_status)
    return my_status

def prep_location():
    '''Return location as a dictionary'''
    LOGGER.info("Dumping Location")
    locations = Location.query.all()
    my_locations = []
    for location in locations:
        this_location = {
            "name": location.name,
            "host": location.host,
            "description": location.description,
            "path": location.path,
            "notes": location.notes,
        }
        my_locations.append(this_location)
    return my_locations

def prep_document_type():
    '''Return document types as a dictionary'''
    LOGGER.info("Dumping DocumentType")
    types = DocumentType.query.all()
    my_types = []
    for typ in types:
        my_type = {
            "type": typ.type,
        }
        my_types.append(my_type)
    return my_types

def dump(file_name):
    '''Start the dumping process'''
    log_format = "%(asctime)-15s [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    LOGGER.info("Dump process started")

    app.config['SQLALCHEMY_ECHO'] = False

    file_contents = {
        "person": prep_person(),
        "category": prep_category(),
        "document_type": prep_document_type(),
        "term_status": prep_term_status(),
        "location": prep_location(),
        "term": prep_terms(),
        "rule": prep_rules()
    }
    print file_contents
    with open(file_name, 'w') as outfile:
        yaml.safe_dump(file_contents, outfile, default_flow_style=False)

    LOGGER.info("Dump process ended")