#!/usr/bin/python
# -*- encoding: utf-8-*-

import logging

import csv

from os.path import dirname, join

from app import app, db
from app.models import Location, Table, Column

from config import BASE_DIR

LOGGER = logging.getLogger("business-glossary.load_data")

app.config['SQLALCHEMY_ECHO'] = False

def load_locations(file_name):
    '''
    Load locations from CSV file

    :param file_Name: The name of the CSV file to load locations from
    '''

    LOGGER.info("Loading locations...")

    with open(file_name, 'rt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            if db.session.query(Location.id).filter_by(name=row['name']).scalar():
                LOGGER.info("Location %s already exists", row['name'])
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
                LOGGER.info("Location %s added", row['name'])


def load_tables(file_name):
    '''
    Load table metadata from CSV file

    :param file_Name: The name of the CSV file to load table metadata from

    .. todo:: Need to test against table and location
    '''

    LOGGER.info("Loading table metadata...")

    with open(file_name, 'rt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            LOGGER.info("Loading %s.%s", row['location'], row['table'])

            # TODO: Need to test against table and location
            if db.session.query(Table.id).filter_by(name=row['table']).scalar():
                LOGGER.info("Table %s.%s already exists", row['location'], row['table'])
            else:
                l = Location.query.filter_by(name=row['location']).first()

                record = Table(**{
                    'name' : row['table'],
                    'description' : row['description'],

                    'location' : l
                    })
                db.session.add(record)
                db.session.commit()

################################################################################
#
# Load Column Metadata
#
################################################################################

def load_columns(file_name):
    '''
    Load columns from CSV file

    :param file_Name: The name of the CSV file to load column metadata from
    '''
    LOGGER.info("Loading column metadata...")

    with open(file_name, 'rt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:

            LOGGER.info("Loading table %s column %s", row['table'], row['name'])

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

if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)-15s [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    LOGGER.info("Load process started")

    # Interface files are placed in a directory name bg_interface at the same level
    # as the application directory, i.e.
    #
    #   - bg_interface
    #   - business_glossary
    #
    # Call os.path.dirname twice to walk up to the parent directory

    FILE_PATH = join(dirname(BASE_DIR), 'bg_interface')

    # Delete all Columns

    cols_deleted = Column.query.delete()

    LOGGER.info("%s columns deleted", cols_deleted)

    load_locations(join(FILE_PATH, "bg_interface_locations.csv"))
    load_tables(join(FILE_PATH, "bg_interface_table.csv"))
    load_columns(join(FILE_PATH, "bg_interface_column.csv"))

    LOGGER.info("Load process ended")
