import csv
import os

from os.path import dirname, join

from app import app, db, models
from app.models import Category, Term, Person, TermStatus, Link, Location, Table, Column, DocumentType, Rule

from config import BASE_DIR

app.config['SQLALCHEMY_ECHO'] = False

###############################################################################
#
# Define the path where the interface files are
#
###############################################################################
#
# Interface files are placed in a directory name bg_interface at the same level
# as the application directory, i.e.
#
#   - bg_interface
#   - business_glossary
#
# Call os.path.dirname twice to walk up to the parent directory
#
###############################################################################

file_path = join(dirname(BASE_DIR), 'bg_interface')

###############################################################################
#
# Drop and recreate all tables
#
###############################################################################

db.drop_all()
db.create_all()

################################################################################
#
# Load TermStatus
#
################################################################################

file_name = os.path.join(file_path, "bg_interface_status.csv")

print("\nLoading status\n")

with open(file_name, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        print(row['status'])

        record = TermStatus(**{
            'status' : row['status']
            })
        db.session.add(record)
        db.session.commit()

################################################################################
#
# Load Category
#
################################################################################

file_name = os.path.join(file_path, "bg_interface_category.csv")

print("\nLoading categories\n")

with open(file_name, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        print(row['category'])

        record = Category(**{
            'name' : row['category'],
            'description' : row['description']
            })
        db.session.add(record)
        db.session.commit()

################################################################################
#
# Load DocumentType
#
################################################################################

file_name = os.path.join(file_path, "bg_interface_document_type.csv")

print("\nLoading types\n")

with open(file_name, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        print(row['document_type'])

        record = DocumentType(**{
            'type' : row['document_type']
            })
        db.session.add(record)
        db.session.commit()

################################################################################
#
# Load Person
#
################################################################################

file_name = os.path.join(file_path, "bg_interface_person.csv")

print("\nLoading people\n")

with open(file_name, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        print(row['person'])

        record = Person(**{
            'name' : row['person']
            })
        db.session.add(record)
        db.session.commit()


################################################################################
#
# Load Terms
#
################################################################################

file_name = os.path.join(file_path, "bg_interface_terms.csv")

print("\nLoading terms\n")

with open(file_name, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        print(row)

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

################################################################################
#
# Load Term Categories
#
################################################################################

file_name = os.path.join(file_path, "bg_interface_categories.csv")

print("\nLoading categories\n")

with open(file_name, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        print(row)

        t = Term.query.filter_by(name=row['term']).first()
        c = Category.query.filter_by(name=row['category']).first()

        t.categories.append(c)

        db.session.commit()

################################################################################
#
# Load Links
#
################################################################################

file_name = os.path.join(file_path, "bg_interface_links.csv")

print("\nLoading links\n")

with open(file_name, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        print(row)

        record = Link(**{
            'text' : row['text'],
            'address' : row['address']
            })
        db.session.add(record)

        t = Term.query.filter_by(name=row['term']).first()
        l = Link.query.filter_by(text=row['text']).first()

        t.links.append(l)

        db.session.commit()

################################################################################
#
# Load Rules
#
################################################################################

file_name = os.path.join(file_path, "bg_interface_rules.csv")

print("\nLoading rules\n")

with open(file_name, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:

        notes = row['notes'].replace('\\n', '\n').replace('\\r','\r')

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
            print("Rule %s loaded" % r.name)
        else:
            print("Associated term %s not found for rule %s" % (row['term'], row['name']))

        db.session.commit()
