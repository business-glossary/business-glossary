from app import app, db, models
from app.models import Category, Term, Person, TermStatus, Link, Location, Table, Column, DocumentType, Rule

db.create_all()

# Create document types

dt1 = DocumentType(type='Specification')
db.session.add(dt1)

# Create status

s1 = TermStatus(status='Draft')
s2 = TermStatus(status='Approved')
db.session.add(s1)
db.session.add(s2)

# Create categories

c1 = Category(name='Risk', description='Risk related terms.')
c2 = Category(name='APRA', description='Term related to APRA regulations.')
db.session.add(c1, c2)

# Create people

p1 = Person(name='Jo Black')
p2 = Person(name='Fred Young')
db.session.add(p1)
db.session.add(p2)

# Create a link

l1 = Link(text='Australian and New Zealand Standard Industrial Classification',
	address='http://www.abs.gov.au/AUSSTATS/abs@.nsf/Lookup/1292.0Main+Features12006%20(Revision%202.0)?OpenDocument')

l2 = Link(text='Financial System Inquiry',
	address='http://fsi.gov.au/publications/final-report/chapter-3/credit-reporting/')

l3 = Link(text='Credit Reporting - Office of the Australian Information Commissioner',
	address='https://www.oaic.gov.au/privacy-law/privacy-act/credit-reporting')

l4 = Link(text='Privacy (Credit Reporting) Code 2014 (Version 1.2)',
	address='https://www.oaic.gov.au/privacy-law/privacy-registers/privacy-codes/privacy-credit-reporting-code-2014-version-1-2')

# Create terms

desc1 = """Comprehensive credit reporting commenced on 12 March 2014 under changes to the Privacy Act and is the most significant change to Australia's credit reporting system in over 25 years. Comprehensive credit reporting changes the level of consumer credit information that can be held on an individual's credit file.
"""

desc2 = """A standard jointly developed by the Australian Bureau of Statistics and Statistics New Zealand in order to make it easier to compare industry statistics between the two countries.
"""

print l3

t1 = Term(term='Comprehensive Credit Reporting', abbreviation='CCR', description=desc1, owner=p1, steward=p2, status=s1)
t2 = Term(term='Australian and New Zealand Standard Industrial Classification', abbreviation='ANZSIC', description=desc2, owner=p1, steward=p2, status=s2)

t1.categories.append(c1)
t1.categories.append(c2)

t2.categories.append(c1)

db.session.add(l1)
db.session.add(l2)
db.session.add(l3)
db.session.add(l4)

db.session.add(t1)
db.session.add(t2)

print "%s contains %s links" % (t1.term, t1.links.count())

t1.links.append(l1)

t1.links.append(l3)

print "%s contains %s links" % (t1.term, t1.links.count())

t2.links.append(l1)

db.session.commit()

t = Term.query.filter_by(id=1).first()

print "%s contains %s links" % (t.term, t.links.count())

print "%s contains %s links" % (t.term, t.links.count())

l1 = Link.query.filter_by(id=2).first()
print l1.text
t.links.append(l1)

l2 = Link.query.filter_by(id=4).first()
t.links.append(l2)
db.session.commit()

# Create Table and Columns

l = Location(name='PROD_DB', description='/data/prod/risk_mart');

t = Table(name='ACCOUNT_HISTORY', location=l)

c1 = Column(name='DATE_KEY', type='NUM', length='8', format='DATE9.', table=t)
c2 = Column(name='ACCOUNT_ID', type='NUM', length='8', format='21.', table=t)
c3 = Column(name='APPLICATION_ID', type='NUM', length='8', format='3.', table=t)
c4 = Column(name='BALANCE_AMT', type='NUM', length='8', format='20.', table=t)

db.session.add(l)
db.session.add(t)
db.session.add(c1)
db.session.add(c2)
db.session.add(c3)
db.session.add(c4)

# Create Business Rule

t = Term.query.filter_by(id=1).first()
r = Rule(identifier='BR_001', name='New Customer Rule', description='This is a new customer rule', notes='Detailed description of the rule.  Typically written in structured English or pseudo code.  Consider using a flowchart or UML activity diagram to depict procedural logic.')
t.rules.append(r)
db.session.add(r)

print "Rule", r.identifier, "created"

db.session.commit()
