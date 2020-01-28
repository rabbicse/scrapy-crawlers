# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import urllib.parse


class DubizzleSpider(scrapy.Spider):
    name = 'dubizzle'
    allowed_domains = ['dubai.dubizzle.com']
    start_urls = [
        '''https://dubai.dubizzle.com/en/property-for-rent/residential/?filters=(listed_by.value%3A%22LA%22)''']
    __base_uri = 'https://dubai.dubizzle.com'

    def parse(self, response):
        links = response.xpath('//a[@class="listing-link"]/@href').extract()
        for link in links:
            # print(link)
            next_uri = self.__base_uri + urllib.parse.unquote_plus(link)
            print(next_uri)
            yield Request(url=next_uri, callback=self.parse_details)
            break

    def parse_details(self, response):
        print(response.body)
        data = response.xpath('//h1[@data-ui-id="listing-title"]/text()').extract()
        print(data)
