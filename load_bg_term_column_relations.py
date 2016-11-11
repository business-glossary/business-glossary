from app import app, db, models
from app.models import Category, Term, Person, TermStatus, Link, Location, Table, Column, DocumentType, Rule

import csv, os

# Define the path where the interface files are

file_path = r"V:\CreditRisk\Staging\TindalA"
# file_path = r"C:\Users\Alan\Projects\bg_interface\bg_interface_status.csv"

file_name = os.path.join(file_path, "bg_interface_columns_term.csv")

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
			
		print "finding", "name", row['name'], "table", row['table']
		c = Column.query.join(Table).filter(Column.name==row['name'], Table.name==row['table']).first()
		
		print "Found column", c.id
		c1 = Column.query.filter_by(id=c.id).first()
		
		t = Term.query.filter_by(term=row['term']).first()

		print "Adding column", c.name, "to term", t.term
		
		t.columns.append(c1)
		db.session.commit()