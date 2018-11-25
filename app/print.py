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

import os
from flask import render_template, Response, send_from_directory
from app.config import BASE_DIR
from app.main.models import Term, Category

#########################################################################################
##                                                                                     ##
##  Print routine                                                                      ##
##                                                                                     ##
#########################################################################################

def old_print_report():

    from markdown import markdown
    import pdfkit
    import flask

    output_filename = 'glossary.pdf'

    terms = Term.query.order_by(Term.name).all()

    html_text = flask.render_template('print/glossary_print.html', terms=terms)

    options = {
        'page-size': 'A4',
        'dpi': 300,
        'margin-top': '20mm',
        'margin-right': '20mm',
        'margin-bottom': '20mm',
        'margin-left': '20mm',
        'encoding': "UTF-8",
        'header-left': "BOQ Credit Risk",
        'header-right': "Full Glossary",
        'header-font-name': 'Roboto',
        'header-font-size': '8',
        'header-spacing': '10',
        'footer-left': '[date], [time]',
        'footer-right': 'Page [page] of [topage]',
        'footer-font-name': 'Roboto',
        'footer-font-size': '8',
        'footer-spacing': '10',
        'no-outline': None
    }

    css = 'C:/Users/Alan/Projects/glossary/print-test/style.css'

    print(html_text)

    pdfkit.from_string(html_text, output_filename, options=options, css=css)


def generate_pdf(filename, categories):
    '''
    Dump all glossary content
    '''

    import pdfkit

    pdf_directory = os.path.join(BASE_DIR, 'app', 'static', 'files')

    # Add wkhtmltopdf directory to path
    path = os.getenv("PATH")
    if "wkhtmltopdf" not in path:
        os.environ["PATH"] += os.pathsep + 'C:/Program Files/wkhtmltopdf/bin'

    if categories:
        print("Categories requested: %s" % categories)
        terms = Term.query.join(Term.categories).filter(Category.id.in_(categories)).order_by(Term.name).all()
        cats = Category.query.filter(Category.id.in_(categories)).all()
        print(terms)
    else:
        #terms = Term.query.order_by(Term.name).limit(10).all()
        terms = Term.query.order_by(Term.name).all()

    html_text = render_template('print/glossary_print.html', terms=terms, categories=cats)

    options = {
        'page-size': 'A4',
        'dpi': 300,
        'margin-top': '20mm',
        'margin-right': '20mm',
        'margin-bottom': '20mm',
        'margin-left': '20mm',
        'encoding': "UTF-8",
        'header-left': "BOQ Credit Risk Analytics",
        'header-right': "Term Definition",
        'header-font-name': 'Roboto',
        'header-font-size': '8',
        'header-spacing': '10',
        'footer-left': '[date], [time]',
        'footer-right': 'Page [page] of [topage]',
        'footer-font-name': 'Roboto',
        'footer-font-size': '8',
        'footer-spacing': '10',
        'no-outline': None
    }

    css = os.path.join(BASE_DIR, 'app', 'static', 'css', 'print_style.css')
    cover = os.path.join(BASE_DIR, 'app', 'templates', 'print', 'cover_page.html')

    directory = os.path.join(os.path.dirname(BASE_DIR), 'bg_interface')

    pdfkit.from_string(html_text, \
                       os.path.join(directory, filename), \
                       options=options, \
                       css=css, \
                       cover=cover)
