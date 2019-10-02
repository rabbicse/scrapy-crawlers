# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.log import logger

from cloudscene import db_handler
from cloudscene.models import CloudScene, Europages, Ces


class CloudscenePipeline(object):
    def __init__(self):
        """Initializes database connection and sessionmaker.
        Creates tables.
        """
        self.Session = db_handler.Session

    def process_item(self, item, spider):
        """Save deals in the database.
        This method is called for every item pipeline component.
        """
        logger.info('Trying to insert data for spider: {}'.format(spider.name))
        session = self.Session()

        try:
            query = {'url': item['url']}

            if spider.name == 'cloudscene_crawler':
                q_data = session.query(CloudScene).filter_by(**query).first()
                if q_data:
                    logger.warning('URL: {} already exists!'.format(item['url']))
                    return

                model = CloudScene(**item)
                session.add(model)

            if spider.name == 'europages':
                q_data = session.query(Europages).filter_by(**query).first()
                if q_data:
                    logger.warning('URL: {} already exists!'.format(item['url']))
                    return

                model = Europages(**item)
                session.add(model)

            if spider.name == 'ces19':
                q_data = session.query(Ces).filter_by(**query).first()
                if q_data:
                    logger.warning('URL: {} already exists!'.format(item['url']))
                    return

                model = Ces(**item)
                session.add(model)

            session.commit()
        except Exception as x:
            logger.debug('Exception when db operation: {}'.format(x))
            session.rollback()
            raise
        finally:
            session.close()

        return item
