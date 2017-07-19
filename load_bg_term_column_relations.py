#   Copyright 2017 Alan Tindale, All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import os
import logging
import csv

from app import create_app
from app import db
from app.models import Term, Table, Column
from config import BASE_DIR

LOGGER = logging.getLogger("business-glossary.load_data")

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

    app = create_app(os.getenv('BG_CONFIG') or 'default')
    app.config['SQLALCHEMY_ECHO'] = False

    # Interface files are placed in a directory name bg_interface at the same level
    # as the application directory, i.e.
    #
    #   - bg_interface
    #   - business_glossary
    #
    # Call os.path.dirname twice to walk up to the parent directory

    FILE_PATH = os.path.join(os.path.dirname(BASE_DIR), 'bg_interface')

    load_column_term(os.path.join(FILE_PATH, "bg_interface_columns_term.csv"))

    LOGGER.info("Load process ended")
