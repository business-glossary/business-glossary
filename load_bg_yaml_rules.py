from app import app, db, models
from app.models import Category, Term, Person, TermStatus, Link, Location, Table, Column, DocumentType, Rule

import yaml, os

from os.path import dirname, join

from config import BASE_DIR

file_path = join(dirname(BASE_DIR), 'bg_interface')
file_name = os.path.join(file_path, "rules.yaml")

def remove_key(d, key):
    '''Remove an element from a dictionary'''
    r = dict(d)
    del r[key]
    return r

def add_rule(rule):
    '''Add a rule from a dict'''
    
    if db.session.query(Rule.id).filter_by(name=rule['name']).scalar():
        print "Rule", rule['name'], "already exists"
        return
        
    notes = rule['notes'].replace('\\n', '\n').replace('\\r','\r')

    rule_to_load = remove_key(rule, 'term')
    
    record = Rule(**rule_to_load)
    
    
    
#    record = Rule(**{
#        'identifier' : rule['identifier'],
#        'name' : rule['name'],
#        'description' :rule['description'],
#        'notes' : notes
#        })
    db.session.add(record)

    # Get the rule again
    r = Rule.query.filter_by(identifier=rule['identifier']).first()

    # Find the term to associate the rule with
    t = Term.query.filter_by(term=rule['term']).first()

    # If the term is found associate with the rule
    if t:
        t.rules.append(r)
        print "Rule %s loaded" % r.name
    else:
        print "Associated term %s not found for rule %s" % (rule['term'], rule['name'])

    db.session.commit()
    
app.config['SQLALCHEMY_ECHO'] = False

with open(file_name, 'r') as stream:
    try:
        rules = yaml.load(stream)
        for rule in rules:
            add_rule(rule)
    except yaml.YAMLError as ex:
        print(ex)
