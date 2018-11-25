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

from os.path import join, isdir, dirname
import time

import click
from flask import current_app
from flask.cli import with_appcontext

from app.extensions import db
from app.loader import load_yaml, dump_yaml

@click.group()
def data():
    '''Data commands.'''


@data.command()
@with_appcontext
def clear():
    '''Clear everything from the database.'''
    db.drop_all()
    db.create_all()


@data.command('load')
@click.argument('filename')
@with_appcontext
def load_data(filename):
    '''Load all glossary data from YAML file.'''
    load_yaml.load(filename)


@data.command('dump')
@click.argument('directory')
@with_appcontext
def dump_data(directory):
    '''Dump all glossary data to YAML file.'''

    timestr = time.strftime("%Y%m%d-%H%M%S")

    if directory == "None":
        file_path = join(dirname(BASE_DIR), 'bg_interface')
    else:
        file_path = directory

    if not isdir(file_path):
        print("The directory %s does not exist" % file_path)
        return

    file_name = join(file_path, "bg_export_" + timestr)

    dump_yaml.dump(file_name + ".yaml")
