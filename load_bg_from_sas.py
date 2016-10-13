from app import app, db, models
from app.models import Category, Term, Person, TermStatus, Link, Location, Table, Column, DocumentType, Rule

import csv

db.create_all()

# Load TermStatus

file_name = r"V:\CreditRisk\Staging\TindalA\bg_interface_status.csv"

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
		print (row['status'])

		record = TermStatus(**{
			'status' : row['status']
			})
		db.session.add(record)
		db.session.commit()

# Load Category

file_name = r"V:\CreditRisk\Staging\TindalA\bg_interface_category.csv"

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
		print (row['category'])

		record = Category(**{
			'name' : row['category'],
			'description' : row['description']
			})
		db.session.add(record)
		db.session.commit()
		
# Load DocumentType

file_name = r"V:\CreditRisk\Staging\TindalA\bg_interface_document_type.csv"

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
		print (row['document_type'])

		record = DocumentType(**{
			'type' : row['document_type']
			})
		db.session.add(record)
		db.session.commit()			

# Load Person

file_name = r"V:\CreditRisk\Staging\TindalA\bg_interface_person.csv"

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
		print (row['person'])

		record = Person(**{
			'name' : row['person']
			})
		db.session.add(record)
		db.session.commit()				

		
# ##############################################################################
#
# Load Terms
#
# ##############################################################################

file_name = r"V:\CreditRisk\Staging\TindalA\bg_interface_terms.csv"

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
		print row

		s = TermStatus.query.filter_by(status=row['status']).first()
		o = Person.query.filter_by(name=row['owner']).first()
		st = Person.query.filter_by(name=row['steward']).first()

		record = Term(**{
			'term' : row['term'],
			'description' : row['description'],
			'abbreviation' : row['abbreviation'],
			'status' : s,
			'owner' : o,
			'steward' : st
			})
		db.session.add(record)

		db.session.commit()
		
# ##############################################################################
#
# Load Term Categories
#
# ##############################################################################

file_name = r"V:\CreditRisk\Staging\TindalA\bg_interface_categories.csv"

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
		print row

		t = Term.query.filter_by(term=row['term']).first()
		c = Category.query.filter_by(name=row['category']).first()

		t.categories.append(c)

		db.session.commit()		

# ##############################################################################
#
# Load Links
#
# ##############################################################################

file_name = r"V:\CreditRisk\Staging\TindalA\bg_interface_links.csv"

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
		print row

		record = Link(**{
			'text' : row['text'],
			'address' : row['address']
			})
		db.session.add(record)
		
		t = Term.query.filter_by(term=row['term']).first()
		l = Link.query.filter_by(text=row['text']).first()
		
		t.links.append(l)

		db.session.commit()		
		
# ##############################################################################
#
# Load Rules
#
# ##############################################################################

file_name = r"V:\CreditRisk\Staging\TindalA\bg_interface_rules.csv"

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
		print row

		t = Term.query.filter_by(term=row['term']).first()

		record = Rule(**{
			'identifier' : row['identifier'],
			'name' : row['name'],
			'description' : row['description']
			})
		db.session.add(record)
		
		r = Rule.query.filter_by(identifier=row['identifier']).first()
		
		t.rules.append(r)

		db.session.commit()