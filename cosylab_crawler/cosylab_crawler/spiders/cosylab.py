# -*- coding: utf-8 -*-
import json
import urllib.parse

from scrapy import Request, Spider

from cosylab_crawler.items import CosylabItem


class CosylabSpider(Spider):
    name = 'cosylab'
    allowed_domains = ['cosylab.iiitd.edu.in']
    __search_url = 'https://cosylab.iiitd.edu.in/flavordb/food_pairing?id={}'
    __api_url = 'https://cosylab.iiitd.edu.in/flavordb/food_pairing_analysis?id={}'

    def start_requests(self):
        for i in range(1, 973):
            yield Request(url=self.__search_url.format(i), meta={'id': i}, callback=self.parse)

    def parse(self, response):
        meta = {'id': response.meta['id'], 'url': response.url,
                'name': response.xpath('//div[@id="entity_details"]/h1/text()').get()}

        h5_list = response.xpath('//div[@class="caption"]//h5')
        if h5_list:
            for h5 in h5_list:
                if 'Category:' in str(h5):
                    meta['category'] = h5.xpath('.//span[@class="text-capitalize"]/text()').get()
                elif 'Synonyms:' in str(h5):
                    meta['synonyms'] = h5.xpath('.//span[@class="text-capitalize"]/text()').get()

        yield Request(url=self.__api_url.format(meta['id']), meta=meta, callback=self.parse_json)

    def parse_json(self, response):
        # TODO: This is a hack we need to check it later
        j_data = json.loads(response.body)
        json_data = json.loads(j_data)
        for j in json_data:
            item = CosylabItem()
            if 'url' in response.meta:
                item['url'] = response.meta['url']
            if 'name' in response.meta:
                item['name'] = response.meta['name']
            if 'category' in response.meta:
                item['category'] = response.meta['category']
            if 'synonyms' in response.meta:
                item['synonyms'] = response.meta['synonyms']

            js_data = json_data[j]
            j_data = js_data['entity_details']
            item['entity_name'] = j_data['name']
            item['entity_category'] = j_data['category']
            item['wiki_page'] = j_data['wiki']

            mols = js_data['common_molecules']
            item['num_of_sharedFlavor'] = len(mols)
            yield item

