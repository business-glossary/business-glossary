#!/usr/bin/python
# -*- encoding: utf-8-*-

import csv
import os

from os.path import dirname, join

from app import app, db, models
from app.models import Location, Table, Column

from config import BASE_DIR

app.config['SQLALCHEMY_ECHO'] = False

###############################################################################
#
# Define the path where the interface files are
#
###############################################################################

# Interface files are placed in a directory name bg_interface at the same level
# as the application directory, i.e.
#
#   - bg_interface
#   - business_glossary
#
# Call os.path.dirname twice to walk up to the parent directory

file_path = join(dirname(BASE_DIR), 'bg_interface')

###############################################################################
#
# Delete all Columns
#
###############################################################################

x = Column.query.delete()

print(x, "columns deleted")

###############################################################################
#
# Load Locations
#
###############################################################################

file_name = os.path.join(file_path, "bg_interface_locations.csv")

print("\nLoading Locations\n")

with open(file_name, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        print(row)

        if db.session.query(Location.id).filter_by(name=row['name']).scalar():
            print("Location", row['name'], "already exists")
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

################################################################################
#
# Load Table Metadata
#
################################################################################

file_name = os.path.join(file_path, "bg_interface_table.csv")

print("\nLoading table metadata...\n")

#try:
with open(file_name, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        print("Loading", row['location'] + "." + row['table'])

        # TODO: Need to test against table and location
        if db.session.query(Table.id).filter_by(name=row['table']).scalar():
            print("Table", row['location'] + "." + row['table'], "already exists")
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
#    db.session.rollback()
#finally:
#    db.session.close()

################################################################################
#
# Load Column Metadata
#
################################################################################

file_name = os.path.join(file_path, "bg_interface_column.csv")

# We had a failure here so need to work on the exception handling

#try:

print("\nLoading column metadata...\n")

with open(file_name, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:

        print("Loading table", row['table'], "column", row['name'])

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

print("Done")
