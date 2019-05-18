# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.log import logger

from rlocker_crawler import db_handler
from rlocker_crawler.items import RlockerItem
from rlocker_crawler.models import Model


class HawthornegcSpider(scrapy.Spider):
    name = 'hawthornegc'
    __base_url = 'http://hawthornegc.ca'
    allowed_domains = ['hawthornegc.ca']
    start_urls = ['http://hawthornegc.ca/']

    def start_requests(self):
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        #     'Upgrade-Insecure-Requests': '1',
        #     'Connection': 'keep-alive',
        #     'Host': 'www.hawthornegc.ca',
        #     'Referer': 'https://www.hawthornegc.ca/',
        #     'Accept-Language': 'en-US,en;q=0.5',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        # yield Request(url='https://www.hawthornegc.ca/', callback=self.parse, headers=headers)

        uri = 'https://www.hawthornegc.ca/shop/bycategory/fans-ventilation-ducting#page=0'
        yield Request(url=uri, callback=self.parse_category)

    def parse(self, response):
        links = response.xpath('//ul[@class="ProductsNavigation dropdown-menu ColumnWidth4 "]//li[@class="non-header"]/a/@href').getall()
        for link in links:
            print(self.__base_url + link)

    def parse_category(self, response):
        try:

            content = response.xpath('//div[@class="container"]/@data-content').get()
            print(content)


            session = db_handler.Session()
            products = response.xpath('//a[@class="thumbnail"]/@href').getall()
            for product in products:
                product_url = product
                print(product_url)
                # query = {'url': product_url, 'spider': self.name}
                # q_data = session.query(Model).filter_by(**query).first()
                # if not q_data:
                #     yield Request(url=product_url, callback=self.parse_details)
                # else:
                #     logger.debug('URL: {} already exists!'.format(product_url))
        except:
            pass

        finally:
            session.close()

    def parse_details(self, response):
        item = RlockerItem()
        item['url'] = response.url

        # try:
        #     item['item_id'] = response.xpath('//dd[@class="productView-info-value"]/text()').get().strip()
        # except:
        #     pass

        try:
            title = response.xpath('//h1[@itemprop="name"]/text()').get()
            item['title'] = title
        except:
            pass

        try:
            cats = []
            catalogs = response.xpath('//nav[@class="breadcrumbs"]/ul/li/a/span[@itemprop="title"]/text()').getall()
            for catalog in catalogs:
                if 'Home' in catalog:
                    continue

                cats.append(catalog.strip())
            item['category'] = ' > '.join(cats)
        except:
            pass

        try:
            item['price'] = response.xpath('normalize-space(//span[@class="regular-price"])').get()
        except:
            pass

        try:
            im_urls = []
            big_imgs = response.xpath('//a[@class="cloud-zoom-gallery"]/@href').getall()
            if big_imgs and len(big_imgs) > 0:
                for big_img in big_imgs:
                    im_urls.append(big_img)
            item['images_url'] = '; '.join(im_urls)
        except:
            pass

        try:
            desc = response.xpath('normalize-space(//div[@class="box-collateral"])').get()
            item['description'] = desc
        except:
            pass

        return item



