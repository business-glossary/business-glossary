'''Dump data to yaml'''

import logging

import yaml, os

from os.path import dirname, join, isfile

from app import app, db, models
from app.models import Category, Term, Person, TermStatus, Link, Location, Table, \
    Column, DocumentType, Rule

from os.path import dirname, join

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
    cats = []
    for c in term.categories:
        cats.append(c.name)
    return cats

def prep_terms():
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
            "created_at": term.created_on,
            "updated_on": term.updated_on
        }
        my_terms.append(my_term)
    return my_terms

def prep_rules():
    rules = Rule.query.all()

    my_rules = []

    for rule in rules:
        my_rule = {
            "identifier": rule.identifier,
            "name": rule.name,
            "description": rule.description,
            "notes": rule.notes,
            "created_at": rule.created_on,
            "updated_on": rule.updated_on
        }
        my_rules.append(my_rule)
    return my_rules

def prep_people():
    people = Person.query.all()
    my_people = []
    for person in people:
        my_person = {
            "name": person.name,
        }
        my_people.append(my_person)
    return my_people

def prep_document_types():
    types = DocumentType.query.all()
    print "-->", type(types)
    print types
    my_types = []
    for t in types:
        my_type = {
            "type": t.type,
        }
        my_types.append(my_type)
    print my_types

    result = DocumentType.query.all()
    print ">",dict(zip(['type'],result))

#    result_dict = [u.__dict__ for u in DocumentType.query.all()]

#    print "r",result_dict

 #   print "b4"
  ##  for t in db.session.query(DocumentType.id):
    #    print t.__dict__
    #print "after"

    return my_types

def dump(file_name):
    '''Start the dumping process'''
    log_format = "%(asctime)-15s [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    LOGGER.info("Dump process started")

    app.config['SQLALCHEMY_ECHO'] = False

    #file_contents = [
    #    "terms": prep_terms(),
    #    "rules:"
    #]
    file_contents = {"person": prep_people(),
        "document_type": prep_document_types() 
    }
    
    print type(file_contents)

    with open(file_name, 'w') as outfile:
        yaml.safe_dump(file_contents, outfile, default_flow_style=False)

    LOGGER.info("Dump process ended")
