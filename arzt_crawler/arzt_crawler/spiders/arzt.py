# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request
from scrapy.log import logger

from arzt_crawler import db_handler
from arzt_crawler.items import ArztCrawlerItem
from arzt_crawler.models import Model


class ArztSpider(scrapy.Spider):
    name = 'arzt'
    __base_url = 'https://www.arzt-auskunft.de'
    allowed_domains = ['arzt-auskunft.de']
    start_urls = ['https://www.arzt-auskunft.de/facharztgebiete/']

    def start_requests(self):
        uri = 'https://www.arzt-auskunft.de/arzt/innere-medizin-und-kardiologie/kassel/dr-karl-friedrich-appel-2125337'
        item = {'url': uri}
        yield Request(url=uri, meta={'item': item}, callback=self.parse_details)

    def parse(self, response):
        links = response.xpath('//ul[@class="iqw"]//li/a/@href').getall()
        for link in links:
            yield Request(url=link, callback=self.parse_products)
            break

    def parse_products(self, response):
        try:
            session = db_handler.Session()
            products = response.xpath('//a[@class="btn-detail"]/@href').getall()
            for product in products:
                product_url = self.__base_url + '/' + product
                query = {'url': product_url, 'spider': self.name}
                q_data = session.query(Model).filter_by(**query).first()
                if not q_data:
                    item = {'url': product_url}
                    yield Request(url=product_url, meta={'item': item}, callback=self.parse_details)
                else:
                    logger.debug('URL: {} already exists!'.format(product_url))
                break
        except:
            pass
        finally:
            session.close()

    def parse_details(self, response):
        item = ArztCrawlerItem(**response.meta['item'])
        try:
            item['name'] = response.xpath('//h1[@itemprop="name"]/text()').get().replace('\r\n', '').strip()
        except:
            pass

        try:
            item['full_address'] = response.xpath('normalize-space(//span[@itemprop="address"])').get()
            item['address'] = response.xpath('normalize-space(//span[@itemprop="streetAddress"])').get()
            item['post_code'] = response.xpath('normalize-space(//span[@itemprop="postalCode"])').get()
            item['city'] = response.xpath('normalize-space(//span[@itemprop="addressLocality"])').get()
        except:
            pass

        try:
            item['telephone'] = response.xpath('normalize-space(//span[@itemprop="telephone"])').get()
        except:
            pass

        try:
            text = response.xpath('//div[@class="col-sm-6"]').get()
            m = re.search(r'Fax\:\<\/strong\>\<\/div\>(.*?)\<br', str(text), re.MULTILINE)
            if m:
                item['fax'] = m.group(1)
        except Exception as x:
            print(x)

        print(item)
