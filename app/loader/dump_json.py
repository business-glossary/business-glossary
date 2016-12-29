'''Dump data to json'''

import logging

from json import dumps

from app import app
from app.models import Term

LOGGER = logging.getLogger("business-glossary.dump_data")

def dump(file_name):
    '''Dump data to json'''
    log_format = "%(asctime)-15s [%(levelname)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    LOGGER.info("Dump process started")

    app.config['SQLALCHEMY_ECHO'] = False

    # now write output to a file
    data_file = open(file_name, "w")
    # magic happens here to make it pretty-printed
    data_file.write(dumps([i.serialize for i in Term.query.all()], indent=4))
    data_file.close()

    LOGGER.info("File %s created", file_name)
    LOGGER.info("Dump process ended")
