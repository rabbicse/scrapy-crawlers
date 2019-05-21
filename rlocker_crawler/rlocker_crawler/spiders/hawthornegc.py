# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import Request
from scrapy.log import logger

from rlocker_crawler import db_handler
from rlocker_crawler.items import RlockerItem
from rlocker_crawler.models import Model


class HawthornegcSpider(scrapy.Spider):
    name = 'hawthornegc'
    __base_url = 'https://www.hawthornegc.ca'
    allowed_domains = ['hawthornegc.ca']
    start_urls = ['https://hawthornegc.ca/']

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive',
            'Host': 'www.hawthornegc.ca',
            'Referer': 'https://www.hawthornegc.ca/',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        yield Request(url='https://www.hawthornegc.ca/', callback=self.parse, headers=headers)

        # uri = 'https://www.hawthornegc.ca/shop/bycategory/fans-ventilation-ducting#page=0'
        # yield Request(url=uri, callback=self.parse_category)

        # itm = {'brand': 'Hurricane',
        #        'category': 'Fans / Ventilation / Ducting',
        #        'item_id': '22824',
        #        'title': 'Replacement Bracket for Hurricane® & EcoPlus® Wall Mount Fans',
        #        'url': 'https://www.hawthornegc.ca/shop/product/replacement-bracket-for-hurricane-wall-mount-fans?categoryId=fans-ventilation-ducting'}
        # yield Request(url=itm['url'], meta={'item': itm, 'image': ''}, callback=self.parse_details)

    def parse(self, response):
        links = response.xpath(
            '//ul[@class="ProductsNavigation dropdown-menu ColumnWidth4 "]//li[@class="non-header"]/a/@href').getall()
        for link in links:
            cat_link = self.__base_url + link
            yield Request(url=cat_link, callback=self.parse_category)

    def parse_category(self, response):
        try:
            session = db_handler.Session()
            content = response.xpath('//div[@class="container"]/@data-content').get()
            json_data = json.loads(content)

            products = json_data['partFamilies']
            if products and len(products) > 0:
                for product in products:
                    if 'url' not in product:
                        continue

                    details_url = self.__base_url + product['url']
                    query = {'url': details_url, 'spider': self.name}
                    q_data = session.query(Model).filter_by(**query).first()
                    if not q_data:
                        itm = {}
                        if 'id' in product:
                            itm['item_id'] = str(product['id'])

                        if 'name' in product:
                            itm['title'] = product['name']

                        if 'brandName' in product:
                            itm['brand'] = product['brandName']

                        if 'categoryName' in product:
                            itm['category'] = product['categoryName']

                        if 'categoryName' in product:
                            itm['category'] = product['categoryName']

                        image = ''
                        if 'image' in product:
                            image = product['image']

                        yield Request(url=details_url, meta={'item': itm, 'image': image}, callback=self.parse_details)
                    else:
                        logger.debug('URL: {} already exists!'.format(details_url))
        except:
            pass

        finally:
            session.close()

    def parse_details(self, response):
        item = RlockerItem(**response.meta['item'])
        item['url'] = response.url

        try:
            json_data = json.loads(
                response.xpath('normalize-space(//div[@id="prodImgContainer"]/@data-partfamily)').get())
            if json_data:
                if 'Description' in json_data:
                    item['description'] = json_data['Description']
        except:
            pass

        images = []
        try:
            content = response.xpath('normalize-space(//div[@id="prodImgContainer"]/@data-content)').get()
            json_images = json.loads(content)
            for json_image in json_images:
                images.append(json_image['UrlOriginal'])
        except:
            pass
        item['images_url'] = '; '.join(images)

        try:
            prices = []
            json_data = json.loads(
                response.xpath('normalize-space(//div[@id="product-page-container"]/@data-content-part-list)').get())
            if json_data:
                for j_data in json_data['Parts']:
                    if 'EachMsrp' in j_data:
                        p = '$' + str(j_data['EachMsrp'])
                        prices.append(p)
            item['price'] = ', '.join(prices)
        except:
            pass

        return item
