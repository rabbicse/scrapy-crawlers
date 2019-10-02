# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request

from cloudscene.items import EuropagesItem


class EuropagesSpider(scrapy.Spider):
    name = 'europages'
    __page_uri = 'https://www.europages.co.uk/companies/pg-{}/computer.html'
    allowed_domains = ['europages.co.uk']
    start_urls = ['http://europages.co.uk/']

    def start_requests(self):
        # 1566
        for i in range(1, 1567):
            uri = self.__page_uri.format(i)
            yield Request(url=uri, callback=self.parse)

    def parse(self, response):
        records = response.xpath('//li[@class="list-article vcard"]')
        print('Total records: {}'.format(len(records)))
        for record in records:
            yield self.parse_item(record)

    def parse_item(self, record):
        item = EuropagesItem()
        try:
            rec = record.xpath('.//a[@class="company-name display-spinner"]')
            item['name'] = rec.xpath('.//@title').get()
            item['url'] = rec.xpath('.//@href').get()
        except:
            pass

        try:
            item['desc'] = record.xpath('normalize-space(.//span[@class="description"])').get()
        except:
            pass

        try:
            supplier = record.xpath('normalize-space(.//span[@class="keywords"])').get()
            supplier = re.sub(r'(?i)Supplier of\:', '', supplier).strip()
            item['supplier'] = supplier
        except:
            pass

        try:
            web = record.xpath('.//div[@class="website"]/span[@class="image"]/a/@href').get()
            if web:
                item['website'] = web
            else:
                item['website'] = ''
        except Exception as x:
            print(x)

        try:
            item['country'] = record.xpath('normalize-space(.//span[@class="country-name"])').get()
            item['city'] = record.xpath('normalize-space(.//span[@class="street-address postal-code locality"])').get()

        except:
            pass

        return item