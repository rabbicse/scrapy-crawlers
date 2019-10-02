# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.log import logger

from ewg_crawler import db_handler
from ewg_crawler.models import Model

from ewg_crawler.items import EwgCrawlerItem


class EwgSpider(scrapy.Spider):
    name = 'ewg'
    __base_url = 'https://www.ewg.org'
    __search_url = 'https://www.ewg.org/skindeep/search.php?query={}&search_group=ingredients&ptype2='
    allowed_domains = ['ewg.org']
    start_urls = ['http://ewg.org/']

    def start_requests(self):
        # ur = 'https://www.ewg.org/skindeep/search.php?query=ACETYL&search_group=ingredients&ptype2='
        # yield Request(url=ur, meta={'search_key': 'ABYSSINIAN'}, callback=self.parse)

        with open('input_chemical.txt', 'r+') as text_file:
            for line in text_file.readlines():
                line = line.strip().strip(',').strip()
                url = self.__search_url.format(line)
                yield Request(url=url, meta={'search_key': line}, callback=self.parse)

    def parse(self, response):
        try:
            meta = response.meta
            session = db_handler.Session()
            links = response.xpath('//table[@id="table-browse"]/tr/td[@align="center"]/a/@href').getall()
            if not links:
                logger.info('No links found!')
                return

            logger.info('Total records on search page: {}'.format(len(links)))

            for link in links:
                product_url = self.__base_url + link
                query = {'url': product_url, 'spider': self.name}
                q_data = session.query(Model).filter_by(**query).first()
                if not q_data:
                    item = {'url': product_url, 'search_key': meta['search_key']}
                    yield Request(url=product_url, meta={'item': item}, callback=self.parse_details)
                else:
                    logger.debug('URL: {} already exists!'.format(product_url))

            # next page
            try:
                next_links = response.xpath('//div[@id="click_next_number"]/a')
                for next_link in next_links:
                    next_uri_text = next_link.xpath('./text()').get()
                    if 'Next>' in next_uri_text:
                        next_uri = self.__base_url + next_link.xpath('./@href').get()
                        yield Request(url=next_uri, meta={'search_key': meta['search_key']}, callback=self.parse)
            except:
                pass
        except:
            pass
        finally:
            session.close()

    def parse_details(self, response):
        try:
            itm = response.meta['item']

            item = EwgCrawlerItem()
            item['url'] = itm['url']
            item['chemical'] = itm['search_key']
            item['synonyms'] = ''
            item['functions'] = ''

            synonym_text = None
            functions_text = ''
            texts = response.xpath('//p[@class="tinytype"]')
            for text in texts:
                strong = text.xpath('./strong/text()').extract()
                if strong and 'Synonym(s):' in strong:
                    synonym_text = text.xpath('./text()').get().strip()

                if strong and 'Function(s):' in strong:
                    functions_text = text.xpath('./text()').get().strip()

            item['functions'] = functions_text
            if synonym_text:
                synonym_arr = synonym_text.split(';')
                for syn in synonym_arr:
                    eItem = item.copy()
                    eItem['synonyms'] = syn.strip()
                    yield eItem
            else:
                yield item

        except Exception as x:
            logger.error('Error: {}'.format(x))
