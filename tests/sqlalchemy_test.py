"""Test serializing sqlalchemy models"""

import unittest

import jsonpickle

from helper import SkippableTest

try:
    import sqlalchemy as sqa
    from sqlalchemy.ext import declarative
    from sqlalchemy.orm import Session
    HAS_SQA = True
except ImportError:
    HAS_SQA = False

if HAS_SQA:

    Base = declarative.declarative_base()

    class Table(Base):
        __tablename__ = 'table'
        id = sqa.Column(sqa.Integer, primary_key=True)
        name = sqa.Column(sqa.Text)
        value = sqa.Column(sqa.Float)


class SQLAlchemyTestCase(SkippableTest):

    def setUp(self):
        """Create a new sqlalchemy engine for the test"""

        if HAS_SQA:
            url = 'sqlite:///:memory:'
            self.engine = sqa.create_engine(url)
            Base.metadata.drop_all(self.engine)
            Base.metadata.create_all(self.engine)
            self.should_skip = False
        else:
            self.should_skip = True

    def test_sqlalchemy_roundtrip_with_detached_session(self):
        """Test cloned SQLAlchemy objects detached from any session"""

        if self.should_skip:
            return self.skip('sqlalchemy is not installed')

        expect = Table(name='coolness', value=11.0)

        session = Session(bind=self.engine, expire_on_commit=False)
        session.add(expect)
        session.commit()

        jsonstr = jsonpickle.dumps(expect)
        actual = jsonpickle.loads(jsonstr)

        # actual is a shadow object; it cannot be added to the same
        # session otherwise sqlalchemy will detect an identity conflict.
        # To make this work we use expire_on_commit=True so that sqlalchemy
        # allows us to do read-only operations detached from any session.

        self.assertEqual(expect.id, actual.id)
        self.assertEqual(expect.name, actual.name)
        self.assertEqual(expect.value, actual.value)

    def test_sqlalchemy_roundtrip_with_two_sessions(self):
        """Test cloned SQLAlchemy objects attached to a secondary session"""

        if self.should_skip:
            return self.skip('sqlalchemy is not installed')

        expect = Table(name='coolness', value=11.0)

        session = Session(bind=self.engine, expire_on_commit=False)
        session.add(expect)
        session.commit()

        jsonstr = jsonpickle.dumps(expect)
        actual = jsonpickle.loads(jsonstr)

        # actual is a shadow object; it cannot be added to the same
        # session otherwise sqlalchemy will detect an identity conflict.
        # To make this work we use expire_on_commit=True so that sqlalchemy
        # allows us to do read-only operations detached from any session.

        self.assertEqual(expect.id, actual.id)
        self.assertEqual(expect.name, actual.name)
        self.assertEqual(expect.value, actual.value)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SQLAlchemyTestCase, 'test'))
    return suite


if __name__ == '__main__':
    unittest.main()
