from app import app, db, models
from app.models import Category, Term, Person, TermStatus, Link, Location, Table, Column, DocumentType, Rule

import csv, os

from os.path import dirname, join

from config import BASE_DIR

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

################################################################################
#
# Load column to term relationships
#
################################################################################

file_name = os.path.join(file_path, "bg_interface_columns_term.csv")

print "\nLoading column to term relationships\n"

with open(file_name, 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:

		# Find the column (table and column)
		c = Column.query.join(Table).filter(Column.name==row['name'], Table.name==row['table']).first()

		if c:
			# Grab the column again
			c1 = Column.query.filter_by(id=c.id).first()

			# Now find the term
			t = Term.query.filter_by(term=row['term']).first()

			if t:
				# If the term exists the add the column to term relationship
				t.columns.append(c1)
				print "Added relationship between column", c.name, "and term", t.term
				db.session.commit()
			else:
				# Else do nothing
				print "Could not find the term", row['term']
		else:
			print "Could not find column %s in table %s" % (row['table'], row['name'])
