# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


# class FreeindexPipeline(object):
#     def process_item(self, item, spider):
#         return item
from scrapy import log
from scrapy.log import logger

from freeindex import db_handler
from freeindex.models import FreeIndex, db_connect, create_tables


class FreeindexPipeline(object):
    # def process_item(self, item, spider):
    # return item

    def __init__(self):
        """Initializes database connection and sessionmaker.
        Creates tables.
        """
        self.Session = db_handler.Session

    def process_item(self, item, spider):
        """Save deals in the database.
        This method is called for every item pipeline component.
        """
        session = self.Session()

        try:
            model = FreeIndex(**item)
            session.add(model)
            session.commit()
        except Exception as x:
            logger.debug('Exception when db operation: {}'.format(x))
            session.rollback()
            raise
        finally:
            session.close()
        return item
