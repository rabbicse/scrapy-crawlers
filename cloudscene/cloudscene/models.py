#! -*- coding: utf-8 -*-

"""
Web Scraper Project
Scrape data from a regularly updated website livingsocial.com and
save to a database (postgres).
Database models part - defines table for storing scraped data.
Direct run will create the table.
"""

from sqlalchemy import create_engine, Column, Integer, UnicodeText
from sqlalchemy.ext.declarative import declarative_base

from cloudscene import settings

DeclarativeBase = declarative_base()


def db_connect():
    """Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance.
    """
    connection_str = 'mysql+mysqldb://%s:%s@%s:3306/%s?charset=utf8&use_unicode=1' % (
        settings.DATABASE['username'], settings.DATABASE['password'], settings.DATABASE['host'],
        settings.DATABASE['database'])
    return create_engine(connection_str)


def create_tables(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)


class CloudScene(DeclarativeBase):
    """Sqlalchemy deals model"""
    __tablename__ = "cloudscene"
    __table_args__ = {
        'mysql_charset': 'utf8'
    }

    def __init__(self, **kwargs):
        cls_ = type(self)
        for k in kwargs:
            if hasattr(cls_, k):
                setattr(self, k, kwargs[k])

    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)
    operator = Column(UnicodeText)
    address = Column(UnicodeText)
    market = Column(UnicodeText)
    country = Column(UnicodeText)
    website = Column(UnicodeText)
    telephone = Column(UnicodeText)
    email = Column(UnicodeText)
    url = Column(UnicodeText)

class Europages(DeclarativeBase):
    """Sqlalchemy deals model"""
    __tablename__ = "europages"
    __table_args__ = {
        'mysql_charset': 'utf8'
    }

    def __init__(self, **kwargs):
        cls_ = type(self)
        for k in kwargs:
            if hasattr(cls_, k):
                setattr(self, k, kwargs[k])

    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)
    country = Column(UnicodeText)
    city = Column(UnicodeText)
    supplier = Column(UnicodeText)
    website = Column(UnicodeText)
    desc = Column(UnicodeText)
    url = Column(UnicodeText)


class Ces(DeclarativeBase):
    """Sqlalchemy deals model"""
    __tablename__ = "ces"
    __table_args__ = {
        'mysql_charset': 'utf8'
    }

    def __init__(self, **kwargs):
        cls_ = type(self)
        for k in kwargs:
            if hasattr(cls_, k):
                setattr(self, k, kwargs[k])

    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)
    address = Column(UnicodeText)
    brands = Column(UnicodeText)
    categories = Column(UnicodeText)
    contacts = Column(UnicodeText)
    email = Column(UnicodeText)
    phone = Column(UnicodeText)
    website = Column(UnicodeText)
    url = Column(UnicodeText)