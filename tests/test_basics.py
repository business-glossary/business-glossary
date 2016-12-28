from flask import Flask, url_for

import unittest

from app import app, db

from app.models import TermStatus, Document, DocumentType, Term, Category, Person, Link, Location, Table, Column, Rule

from config import BASE_DIR

class BasicTestCase(unittest.TestCase):

    def _add_term(self):
        p = Person(name='Jo Black')
        ts = TermStatus(status='Approved')
        desc1 = """Comprehensive credit reporting (CCR) commenced on 12 March 2014 under changes to the Privacy Act."""
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

    def test_home_status_code(self):

        # send HTTP GET request to the application on specified path
        result = self.client.get('/')

        # asset the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_new_term(self):
        p = Person(name='Jo Black')
        self.assertTrue(p.name == 'Jo Black')
        self.assertTrue(str(p) == 'Jo Black')

        ts = TermStatus(status='Approved')
        assert ts.status == 'Approved'
        assert str(ts) == 'Approved'

        desc1 = """Comprehensive credit reporting commenced on 12 March 2014 under changes to the Privacy Act."""
        t = Term(term='Comprehensive Credit Reporting', abbreviation='CCR', description=desc1, owner=p, steward=p, status=ts)

        self.assertTrue(str(t) == 'Comprehensive Credit Reporting')

        db.session.add(p)
        db.session.add(ts)
        db.session.add(t)
        db.session.commit()

        assert t.id == int(t.get_id())

    def test_term_relationship(self):
        p = Person(name='Jo Black')
        self.assertTrue(p.name == 'Jo Black')

        ts = TermStatus(status='Approved')
        assert ts.status == 'Approved'

        desc1 = """Comprehensive credit reporting commenced on 12 March 2014 under changes to the Privacy Act."""
        t1 = Term(term='Comprehensive Credit Reporting', abbreviation='CCR', description=desc1, owner=p, steward=p, status=ts)

        desc2 = """A standard jointly developed by the Australian Bureau of Statistics and Statistics New Zealand."""
        t2 = Term(term='Australian and New Zealand Standard Industrial Classification', abbreviation='ANZSIC', description=desc2, owner=p, steward=p, status=ts)

        t1.related_to.append(t2)

        db.session.add(p)
        db.session.add(ts)
        db.session.add(t1)
        db.session.add(t2)
        db.session.commit()

        assert t1.id == int(t1.get_id())
        assert t2.id == int(t2.get_id())

    def test_term_status(self):
        ts = TermStatus(status='Approved')
        db.session.add(ts)
        db.session.commit()
        assert ts.status == 'Approved'

    def test_term_category(self):
        tc = Category(name='Test', description='Test category')
        db.session.add(tc)
        db.session.commit()
        assert tc.name == 'Test'
        self.assertTrue(Category.query.filter_by(id=1).first().name == 'Test')

    def test_model_repr(self):
        self.assertTrue(str(Category(name='Test')) == 'Test')
        self.assertTrue(str(TermStatus(status='Test')) == 'Test')
        self.assertTrue(str(Link(text='Test', address="http://x.com")) == 'Test')
        self.assertTrue(str(Location(name='Test')) == 'Test')
        self.assertTrue(str(Link(text='Test')) == 'Test')
        self.assertTrue(str(Column(name='Test')) == 'Test')
        self.assertTrue(str(Rule(name='Test')) == 'Test')
        self.assertTrue(str(Document(name='Test')) == 'Test')
        self.assertTrue(str(DocumentType(type='Test')) == 'Test')
        self.assertTrue(unicode(DocumentType(type='Test')) == 'Test')
        self.assertTrue(unicode(Table(name='Test')) == 'Test')

    def test_term(self):
        t = self._add_term()
        self.assertTrue(Term.query.filter_by(id=1).first().name == 'Comprehensive Credit Reporting')

    def test_term_page(self):
        t = self._add_term()

        # send HTTP GET request to the application on specified path
        result = self.client.get(url_for('main.show_term', selected_term=1))
        # asset the status code of the response
        self.assertEqual(result.status_code, 200)
        self.assertTrue('Comprehensive Credit' in result.get_data(as_text=True))

    def test_term_assets(self):
        term = self._add_term()

        l = Location(name='test location')
        t = Table(name='test location', location=l)
        c = Column(name='test_column', table=t)
        term.columns.append(c)

        db.session.add(l)
        db.session.add(t)
        db.session.add(c)
        db.session.commit()

        # send HTTP GET request to the application on specified path
        response = self.client.get(url_for('main.show_assets', selected_term=1))
        self.assertTrue('test_column' in response.get_data(as_text=True))

    def test_term_rules(self):
        term = self._add_term()
        r = Rule(identifier='BR001', name='Test Rule', description='', notes='')
        term.rules.append(r)
        db.session.add(r)
        db.session.commit()

        # send HTTP GET request to the application on specified path
        response = self.client.get(url_for('main.show_rules', selected_term=1))
        self.assertTrue('BR001' in response.get_data(as_text=True))
        response = self.client.get(url_for('main.show_rule', selected_rule=1))
        self.assertTrue('BR001' in response.get_data(as_text=True))

    def test_location(self):
        l = Location(name='test location')
        t = Table(name='test_table', location=l)
        c = Column(name='test_column', table=t)

        db.session.add(l)
        db.session.add(t)
        db.session.add(c)
        db.session.commit()

        # send HTTP GET request to the application on specified path
        response = self.client.get(url_for('main.show_location_details', selected_location=1))
        self.assertTrue('test location' in response.get_data(as_text=True))
        response = self.client.get(url_for('main.show_location_tables', selected_location=1))
        self.assertTrue('test_table' in response.get_data(as_text=True))
        response = self.client.get(url_for('main.show_table_details', selected_table=1))
        self.assertTrue('test_table' in response.get_data(as_text=True))
        response = self.client.get(url_for('main.show_table_columns', selected_table=1))
        self.assertTrue('test_column' in response.get_data(as_text=True))

    def test_search(self):
        term = self._add_term()

        l = Location(name='test location')
        t = Table(name='test_table', location=l)
        c = Column(name='test_ccr', table=t)
        term.columns.append(c)

        db.session.add(l)
        db.session.add(t)
        db.session.add(c)
        db.session.commit()

        response = self.client.get(url_for('main.search'))
        self.assertTrue('Search for text in the term' in response.get_data(as_text=True))
        response = self.client.post(url_for('main.search'), data={'search': 'ccr'})
        self.assertTrue('Comprehensive Credit Reporting' in response.get_data(as_text=True))
        self.assertTrue('test_ccr' in response.get_data(as_text=True))

    def test_about(self):
        response = self.client.get(url_for('main.about'))
        self.assertTrue('Business Glossary' in response.get_data(as_text=True))
        self.assertTrue('Version' in response.get_data(as_text=True))

    def test_documents(self):
        term = self._add_term()
        dt = DocumentType(type='Test Plan')
        d = Document(name='Test Document', path='/static/css/custom.css', description='Testing', types=[dt])
        term.documents.append(d)

        db.session.add(dt)
        db.session.add(d)
        db.session.commit()

        response = self.client.get(url_for('main.show_documents', selected_term=1))
        self.assertTrue('Test Document' in response.get_data(as_text=True))

    def test_rule_documents(self):

        term = self._add_term()
        dt = DocumentType(type='Test Plan')
        d = Document(name='Test Document', path='/static/css/custom.css', description='Testing', types=[dt])
        term.documents.append(d)

        r = Rule(identifier='BR001', name='Test Rule', description='', notes='')
        term.rules.append(r)

        r.documents.append(d)
        db.session.add(r)
        db.session.add(dt)
        db.session.add(d)
        db.session.commit()

        response = self.client.get(url_for('main.show_rule_documents', selected_rule=1))
        self.assertTrue('Test Document' in response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
