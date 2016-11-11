#!/usr/bin/python
# -*- encoding: utf-8-*-

from app import app, db, models
from app.models import Category, Term, Person, TermStatus, Link, Location, Table, Column, DocumentType, Rule

import csv,os

# Define the path where the interface files are

file_path = r"V:\CreditRisk\Staging\TindalA"
# file_path = r"C:\Users\Alan\Projects\bg_interface\bg_interface_status.csv"

# Delete all rows from table

x = Column.query.delete()

print x, "rows deleted"

# ##############################################################################
#
# Load Locations
#
# ##############################################################################

file_name = os.path.join(file_path, "bg_interface_locations.csv")

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
		print row

		if db.session.query(Location.id).filter_by(name=row['name']).scalar():
			print "Location", row['name'], "already exists"
		else:	
			record = Location(**{
				'name' : row['name'],
				'host' : row['host'],
				'description' : row['description'],
				'path' : row['path'],
				'notes' : row['notes']
				})
			
			db.session.add(record)
			db.session.commit()
		
# ##############################################################################
#
# Load Table Metadata
#
# ##############################################################################

file_name = os.path.join(file_path, "bg_interface_table.csv")

print "Loading table metadata..."

#try:
with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
		print "Loading", row['location'] + "." + row['table']

		# TODO: Need to test against table and location
		if db.session.query(Table.id).filter_by(name=row['table']).scalar():
			print "Table", row['location'] + "." + row['table'], "already exists"
		else:
			l = Location.query.filter_by(name=row['location']).first()

			record = Table(**{
				'name' : row['table'],
				'description' : row['description'],

				'location' : l
				})
			db.session.add(record)
			db.session.commit()
			
#except:
#	db.session.rollback()
#finally:
#	db.session.close()

# ##############################################################################
#
# Load Column Metadata
#
# ##############################################################################

file_name = os.path.join(file_path, "bg_interface_column.csv")

# We had a failure here so need to work on the exception handling

#try:

print
print "Loading column metadata..."

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
	
		print "Loading table", row['table'], "column", row['name']
		
		t = Table.query.filter_by(name=row['table']).first()
		
		record = Column(**{
			'name' : row['name'],
			'description' : row['description'],
			'type' : row['type'],
			'length' : row['length'],
			'format' : row['format'],
			'table' : t
			})
		db.session.add(record)

		db.session.commit()
			
#except:
	#db.session.rollback() # Rollback the changes on error
#finally:
	#db.session.close() # Close the connection

print "Done"
