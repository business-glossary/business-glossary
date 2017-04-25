import logging

import csv

from os.path import dirname, join

from app import app, db
from app.models import Term, Table, Column

from config import BASE_DIR

LOGGER = logging.getLogger("business-glossary.load_data")

app.config['SQLALCHEMY_ECHO'] = False


def load_column_term(file_name):
    '''
    Load column to term relationships from CSV file

    :param file_Name: The name of the CSV file to load from
    '''
    LOGGER.info("Loading column to term relationships")

    with open(file_name, 'rt') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:

            # Find the column (table and column)
            c = Column.query.join(Table).filter(Column.name == row['name'], Table.name == row['table']).first()

            if c:
                # Grab the column again
                c1 = Column.query.filter_by(id=c.id).first()

                # Now find the term
                t = Term.query.filter_by(name=row['term']).first()

                if t:
                    # If the term exists the add the column to term relationship
                    t.columns.append(c1)
                    LOGGER.info("Added relationship between column %s and term %s", c.name, t.name)
                    db.session.commit()
                else:
                    # Else do nothing
                    LOGGER.warning("Could not find the term %s", row['term'])
            else:
                LOGGER.info("Could not find column %s in table %s", row['table'], row['name'])

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

    load_column_term(join(FILE_PATH, "bg_interface_columns_term.csv"))

    LOGGER.info("Load process ended")
