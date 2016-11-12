from app import app, db, models
from app.models import Category, Term, Person, TermStatus, Link, Location, Table, Column, DocumentType, Rule

import csv, os

# Define the path where the interface files are

#file_path = r"V:\CreditRisk\Staging\TindalA"
file_path = r"C:\Users\Alan\Projects\bg_interface"

file_name = os.path.join(file_path, "bg_interface_columns_term.csv")

print "\nLoading column to term relationships\n"

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:

		c = Column.query.join(Table).filter(Column.name==row['name'], Table.name==row['table']).first()

		if c:
			c1 = Column.query.filter_by(id=c.id).first()

			t = Term.query.filter_by(term=row['term']).first()

			if t:
				t.columns.append(c1)
				print "Added relationship between column", c.name, "and term", t.term
				db.session.commit()
			else:
				print "Could not find the term", row['term']
		else:
			print "Could not find column %s in table %s" % (row['table'], row['name'])
