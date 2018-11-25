# -*- coding: utf-8 -*-
#
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
 
import logging
import csv

from flask import current_app

LOGGER = logging.getLogger("business-glossary.export_data")

from app.main.models import Term

def get_column_associations():
    terms = Term.query.all()

    rows = []

    for term in terms:
        if term.columns:
            for column in term.columns:
                rows.append(
                    {
                        'term': term.name,
                        'table': column.table.location.name + '.' + column.table.name,
                        'column': column.name
                    }
                )
    return rows


def export(file_name):
    '''Start the exporting process'''
    log_format = "%(asctime)-15s [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    LOGGER.info("Starting export process")

    current_app.config['SQLALCHEMY_ECHO'] = False

    rows = get_column_associations()
    keys = rows[0].keys()
    with open(file_name, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(rows)