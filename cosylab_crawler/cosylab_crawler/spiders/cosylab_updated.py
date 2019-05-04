# -*- coding: utf-8 -*-
import json

from cosylab_crawler.items import CosylabUpdatedItem
from scrapy import Request, Spider


class CosylabSpider(Spider):
    name = 'cosylabu'
    allowed_domains = ['cosylab.iiitd.edu.in']
    __search_url = 'https://cosylab.iiitd.edu.in/flavordb/entity_details?id={}'
    __api_url = 'https://cosylab.iiitd.edu.in/flavordb/food_pairing_analysis?id={}'

    def start_requests(self):
        for i in range(1, 973):
            yield Request(url=self.__search_url.format(i), meta={'id': i}, callback=self.parse)

    def parse(self, response):
        item = {'url': response.url, 'name': response.xpath('//div[@id="entity_details"]/h1/text()').get()}
        h5_list = response.xpath('//div[@class="caption"]//h5')
        if h5_list:
            for h5 in h5_list:
                if 'Category:' in str(h5):
                    item['category'] = h5.xpath('.//span[@class="text-capitalize"]/text()').get()
                elif 'Synonyms:' in str(h5):
                    item['synonyms'] = h5.xpath('.//span[@class="text-capitalize"]/text()').get()

        rows = response.xpath('//table[@id="molecules"]//tr')
        for row in rows:
            columns = row.xpath('.//td')
            if not columns or len(columns) < 3:
                continue

            itm = CosylabUpdatedItem(**item)
            itm['common_name'] = columns[0].xpath('normalize-space(./text())').get().strip()
            itm['pubchem_id'] = columns[1].xpath('normalize-space(./a/text())').get().strip()
            itm['flavor_profile'] = columns[2].xpath('normalize-space(./text())').get().strip()

            yield itm
