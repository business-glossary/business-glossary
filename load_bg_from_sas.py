from app import app, db, models
from app.models import Category, Term, Person, TermStatus, Link, Table, Column, DocumentType, Rule

import csv

###############################################################################
#
# Load Table Metadata
#
###############################################################################

file_name = r"V:\CreditRisk\Staging\TindalA\bg_interface_table.csv"

try:
	with open(file_name, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=',')
		for row in reader:
			print (row['location'], row['table'])
			
			record = Table(**{
				'name' : row['table'],
				'location' : row['location'],
				})
			db.session.add(record)

			db.session.commit()
			
except:
	db.session.rollback()
finally:
	db.session.close()

###############################################################################
#
# Load Column Metadata
#
###############################################################################

file_name = r"V:\CreditRisk\Staging\TindalA\bg_interface_column.csv"

# We had a failure here so need to work on the exception handling

#try:

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
		print row
		
		t = Table.query.filter_by(name=row['table']).first()
		
		record = Column(**{
			'name' : row['name'],
			'type' : row['type'],
			'length' : row['length'],
			'format' : row['format'],
			'table' : t
			})
		db.session.add(record) # Add all the records

		db.session.commit() # Attempt to commit all the records
			
#except:
	#db.session.rollback() # Rollback the changes on error
#finally:
	#db.session.close() # Close the connection
