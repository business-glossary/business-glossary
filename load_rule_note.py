
import logging
import yaml
import argparse
import os
from os.path import dirname, join, isfile

from app.core import create_app
from app.config import config

application = create_app('production').app_context().push()

from app.main.models import Rule, Note
from app.loader import load_yaml
from app.extensions import db

LOGGER = logging.getLogger("business-glossary.load_data")


def add_rule_note(rule_note):
    '''Add a rule note'''

    #########################################################
    ## Add the rule note
    #########################################################

    record = Note(**{
                'note' : rule_note['rule_note']
                })

    db.session.add(record)

    #########################################################
    ## Now associate with a rule
    #########################################################

    # Find the rule to associate this note
    rule = Rule.query.filter_by(name = rule_note['name']).first()

    # If the rule is found associate the note with the rule
    if rule:
        rule.comments.append(record)
        LOGGER.info("Added rule note to rule %s", rule.name)
    else:
        LOGGER.warning("Rule %s does not exist - we will create it", rule_note['name'])
        rule = Rule(identifier='BR_xxx',
                    name=rule_note['name'],
                    description='*To be completed*',
                    notes='*To be completed*'
                    )

        db.session.add(rule)
        rule.comments.append(record)

    db.session.commit()
    LOGGER.info("Loaded rule note for rule %s", rule_note['name'])

    
def clear_notes():
    # Delete all rule notes prior to reload   
    try:
        num_rows_deleted = db.session.query(Note).delete()
        db.session.commit()
    except:
        db.session.rollback()

    LOGGER.info("%s rules deleted" % num_rows_deleted)
    

def load(file_name):
    '''Start the loading process'''
    log_format = "%(asctime)-15s [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    LOGGER.info("Starting import process")
    
    if not isfile(file_name):
        LOGGER.error("The file does not exist")
    else:
        with open(file_name, 'rt') as stream:
            try:
                objects = yaml.load(stream)
                LOGGER.info("Found %s number of rule notes", len(objects))
                for obj in objects:
                    LOGGER.info("Found %s elements in this rule note", len(obj))
                    for x in obj:
                         LOGGER.info("Found %s", x)
                    add_rule_note(obj)                         

            except yaml.YAMLError as ex:
                print(ex)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    
    parser.add_argument("source", help="Source YAML file or directory containing YAML files")
    args = parser.parse_args()
    
    clear_notes()
    
    if os.path.isfile(args.source):
        load(args.source)
    elif os.path.isdir(args.source):
        for filename in os.listdir(args.source):
            full_file_name = os.path.join(args.source, filename)
            print(full_file_name)
            load(full_file_name)

    else:
        LOGGER.error("Argument specified is neither a file nor a directory")
