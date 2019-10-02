# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request
from scrapy.middleware import logger

from cloudscene import db_handler
from cloudscene.items import CloudsceneItem


class CloudsceneCrawlerSpider(scrapy.Spider):
    name = 'cloudscene_crawler'
    allowed_domains = ['cloudscene.com']
    __page_uri = 'https://cloudscene.com/browse/data-centers?page={}'
    # start_urls = ['https://cloudscene.com/browse/data-centers?page=5']

    def start_requests(self):
        try:
            # uri = 'https://cloudscene.com/data-center/japan/tokyo/equinix-ty2'
            # yield Request(url=uri, callback=self.parse_details)
            for i in range(1, 434):
                uri = self.__page_uri.format(i)
                yield Request(url=uri, callback=self.parse)
        except Exception as x:
            logger.error('Error when start: {}'.format(x))

    def parse(self, response):
        try:
            records = response.xpath('//a[@class="card-view full"]/@href').getall()
            for record in records:
                yield Request(url=record, callback=self.parse_details)
        except Exception as x:
            logger.error('Error when parse: {}'.format(x))

    def parse_details(self, response):
        try:
            item = CloudsceneItem()
            item['url'] = response.url
            try:
                item['name'] = response.xpath('//h2[@class="asset-name"]/text()').get().strip()
            except:
                pass

            try:
                item['operator'] = response.xpath('//span[@itemprop="name"]/text()').get().strip()
            except:
                pass

            try:
                addresses = response.xpath('//div[@class="asset-address"]//p/text()').getall()
                item['address'] = ' '.join(addresses)
            except:
                pass
            try:
                item['country'] = response.xpath('//div[@class="asset-address"]//a/text()').get().strip()
            except:
                pass

            try:
                web_m = re.search(r'(?i)var\s*passSiteLink\=\"([^\"]*)\"', str(response.body), re.MULTILINE)
                if web_m:
                    item['website'] = web_m.group(1)
            except:
                pass

            try:
                itms = response.xpath('//li[@itemprop="itemListElement"]/a/span[@itemprop="name"]/text()').getall()
                markets = []
                for itm in itms[1:3]:
                    markets.append(str(itm))
                markets.reverse()
                print(markets)
                item['market'] = ', '.join(markets)
            except:
                pass

            try:
                telephone = response.xpath('//a[@class="phone-link"]/@href').get()
                telephone = str(telephone).replace('tel:', '')
                item['telephone'] = telephone
            except:
                pass

            return item
        except Exception as x:
            logger.error('Error when parse: {}'.format(x))
