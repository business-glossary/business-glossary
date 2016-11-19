from flask import Flask, url_for

import unittest

from app import app, db

from app.models import Person, TermStatus, Term

from config import BASE_DIR

class BasicTestCase(unittest.TestCase):

    def _add_term(self):
        p = Person(name='Jo Black')
        ts = TermStatus(status='Approved')
        desc1 = """Comprehensive credit reporting commenced on 12 March 2014 under changes to the Privacy Act."""
        t = Term(term='Comprehensive Credit Reporting', abbreviation='CCR', description=desc1, owner=p, steward=p, status=ts)
        db.session.add(p)
        db.session.add(ts)
        db.session.add(t)
        db.session.commit()
        return(t)

    def setUp(self):

        app.config.from_object('config.TestingConfig')

        self.app = Flask(__name__)

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # creates a test client
        self.client = app.test_client()

        # propogate the exceptions to the test client
        self.client.testing = True

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(self.client is None)

#    def test_app_is_testing(self):
#        print self.app.config
#        self.assertTrue(self.app.config['TESTING'])

    def test_home_status_code(self):

        # send HTTP GET request to the application on specified path
        result = self.client.get('/')

        # asset the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_new_term(self):
        p = Person(name='Jo Black')
        self.assertTrue(p.name == 'Jo Black')
        ts = TermStatus(status='Approved')
        assert ts.status == 'Approved'

        desc1 = """Comprehensive credit reporting commenced on 12 March 2014 under changes to the Privacy Act."""
        t = Term(term='Comprehensive Credit Reporting', abbreviation='CCR', description=desc1, owner=p, steward=p, status=ts)

        db.session.add(p)
        db.session.add(ts)
        db.session.add(t)
        db.session.commit()

        assert t.id == int(t.get_id())

    def test_term(self):
        t = self._add_term()
        self.assertTrue(Term.query.filter_by(id=1).first().term == 'Comprehensive Credit Reporting')

    def test_term_page(self):
        t = self._add_term()

        # send HTTP GET request to the application on specified path
        result = self.client.get(url_for('main.show_term', selected_term=1))
        # asset the status code of the response
        self.assertEqual(result.status_code, 200)

if __name__ == '__main__':
    unittest.main()
