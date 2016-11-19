[![Build Status](https://travis-ci.org/atindale/business-glossary.svg?branch=master)](https://travis-ci.org/atindale/business-glossary)

# Business Glossary

A simple business glossary to store and disseminate business taxonomy and vocabulary.

## Running the Application

```
git clone https://github.com/atindale/business-glossary.git
cd business-glossary
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
python create_db.py
python manage.py runserver
```

## Setup

Running the above commands will create an application using the development configuration by default. This uses an SQLite database named glossary_dev.db.

You can also define two environment variables to control the configuration and database it should use.

```
DEV_DATABASE_URL=mysql://username:password@localhost/db_name
BG_CONFIG=config.TestingConfig
```

You can set `DEV_DATABASE_URL`, `TEST_DATABASE_URL` or `PROD_DATABASE_URL` or all three and set the required configuration to use with `BG_CONFIG`

Copyright 2016 Alan Tindale
