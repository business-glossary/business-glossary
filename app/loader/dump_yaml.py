'''Dump data to yaml'''

import logging
import textwrap
import yaml

from app import app
from app.models import Category, Term, Person, TermStatus, Location, \
    DocumentType, Rule, Note, Table, Column

app.config['SQLALCHEMY_ECHO'] = False

LOGGER = logging.getLogger("business-glossary.dump_data")


class literal(str): pass
def literal_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
yaml.add_representer(literal, literal_representer)


def return_categories(term):
    '''Return category names as a list when dumping terms'''
    categories = []
    for category in term.categories:
        categories.append(category.name)
    return categories


def return_terms(rule):
    '''Return the terms a rule belongs to as a list'''
    terms = []
    for term in rule.terms:
        terms.append(term.name)
    return terms


def prep_terms():
    '''Return terms as a dictionary'''
    LOGGER.info("Dumping Term")

    terms = Term.query.all()
    my_terms = []

    for term in terms:
        my_term = {
            "name": term.name,
            "short_description": literal(prepare_string(term.short_description)),
            "long_description": literal(prepare_string(term.long_description)),
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


def prepare_rule_notes():
    '''Returns rule notes as a dictionary'''
    LOGGER.info("Dumping Rule Notes")

    notes = Note.query.all()
    my_notes = []

    for note in notes:
        # print("note_type: %s" % note.note_type)
        my_note = {
            "note": literal(prepare_string(note.note)),
            "note_type": note.note_type,
            "rule": note.rules.name,
            "created_on": note.created_on,
            "updated_on": note.updated_on
        }
        my_notes.append(my_note)
    return my_notes


def prep_rules():
    '''Return rules as a dictionary'''
    LOGGER.info("Dumping Rule")

    rules = Rule.query.all()
    my_rules = []

    for rule in rules:
        my_rule = {
            "identifier": rule.identifier,
            "name": rule.name,
            "description": literal(prepare_string(rule.description)),
            "notes": literal(prepare_string(rule.notes)),
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
    for term_status in status:
        this_status = {
            "status": term_status.status,
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


def prep_tables():
    '''Return tables as a dictionary for dumping'''
    LOGGER.info("Dumping tables")
    tables = Table.query.all()
    my_tables = []
    for table in tables:
        this_table = {
            "name": table.name,
            "description": table.description,
            "location": table.location.name
        }
        new_table = dict((k, v) for k, v in this_table.items() if v)
        my_tables.append(new_table)
    return my_tables


def prep_columns():
    '''Return columns as a dictionary for dumping'''
    LOGGER.info("Dumping columns")
    columns = Column.query.all()
    my_columns = []
    for column in columns:
        this_column = {
            "name": column.name,
            "description": column.description,
            "type": column.type,
            "length": column.length,
            "format": column.format,
            "table": column.table.name
        }
        new_column = dict((k, v) for k, v in this_column.items() if v)
        my_columns.append(new_column)
    return my_columns


def prep_document_type():
    '''Return document types as a dictionary'''
    LOGGER.info("Dumping DocumentType")
    types = DocumentType.query.all()
    my_types = []
    for doc_type in types:
        my_type = {
            "type": doc_type.type,
        }
        my_types.append(my_type)
    return my_types


def prepare_string(data):
    '''Conform a string'''
    if len(data.splitlines()) > 1:
        # If multi-line, loop through each line wrap that line and then join
        # it back together
        new_lines = []
        for line in data.splitlines():
            wrap = textwrap.fill(line, 100)
            new_lines.append(wrap)

        new_string = "\n".join(new_lines)
    else:
        new_string = textwrap.fill(data, 100)
    return new_string


def dump_term(rule, file_name):
    log_format = "%(asctime)-15s [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    LOGGER.info("Dump process started")

    rules = Rule.query.all()

    for rule in rules:

        data = rule.description

        print("\n********************************************************")
        print("The rule is %s" % rule.name)

        print("There are %s lines" % len(data.splitlines()))

        print("--------------------------------------------------------")
        print("The before description is:")
        print(data)

        print("--------------------------------------------------------")
        print("The after description is:")
        print(prepare_string(data))

        data = rule.notes

        print("--------------------------------------------------------")
        print("The before notes is:")
        print(data)

        print("--------------------------------------------------------")
        print("The after notes is:")
        print(prepare_string(data))


        print("--------------------------------------------------------")
        print("YAML Dump: \n")
        my_rule = {
            "identifier": rule.identifier,
            "name": rule.name,
            "description": literal(prepare_string(rule.description)),
            "notes": prepare_string(rule.notes),
            "created_on": rule.created_on,
            "updated_on": rule.updated_on,
            "terms": return_terms(rule)
        }

        print(yaml.dump(my_rule, allow_unicode=True))


def dump_termx(term, file_name):
    log_format = "%(asctime)-15s [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    LOGGER.info("Dump process started")

    rules = Rule.query.all()

    for rule in rules:

        data = rule.description

        print("\n********************************************************")
        print("The term is %s" % rule.name)

        print("There are %s lines" % len(data.splitlines()))

        print("--------------------------------------------------------")
        print("The before description is:")
        print(data)

        print("--------------------------------------------------------")
        print("YAML Dump: \n")
        my_term = {
            "name": term.name,
            "short_description": term.short_description,
            "long_description": literal(prepare_string(term.long_description)),
            "abbreviation": term.abbreviation,
            "status": term.status.status,
            "categories": return_categories(term),
            "owner": term.owner.name,
            "steward": term.steward.name,
            "created_on": term.created_on,
            "updated_on": term.updated_on
        }

        print(yaml.dump(my_term))


def dump(file_name):
    '''Start the dumping process'''
    log_format = "%(asctime)-15s [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    LOGGER.info("Dump process started")

    app.config['SQLALCHEMY_ECHO'] = False

    file_contents_1 = {
        "person": prep_person(),
        "category": prep_category(),
        "document_type": prep_document_type(),
        "term_status": prep_term_status(),
        "location": prep_location()
    }

    file_contents_2 = {
        "terms": prep_terms()
    }

    file_contents_3 = {
        "rules": prep_rules()
    }

    file_contents_4 = {
        "notes": prepare_rule_notes()
    }

    file_contents_5 = {
        "columns": prep_columns(),
        "tables": prep_tables()
    }

    with open(file_name, 'w') as outfile:
        outfile.write("# People, Categories, Document Types and Status\n\n")
        yaml.dump(file_contents_1, outfile, default_flow_style=False, allow_unicode=True)
        outfile.write("\n# Terms\n\n")
        yaml.dump(file_contents_2, outfile, default_flow_style=False, allow_unicode=True)
        outfile.write("\n# Rules\n\n")
        yaml.dump(file_contents_3, outfile, default_flow_style=False, allow_unicode=True)
        outfile.write("\n# Rule Notes\n\n")
        yaml.dump(file_contents_4, outfile, default_flow_style=False, allow_unicode=True)
        outfile.write("\n# Tables and Columns\n\n")
        yaml.dump(file_contents_5, outfile, default_flow_style=False, allow_unicode=True)

    LOGGER.info("File %s created", file_name)
    LOGGER.info("Dump process ended")
