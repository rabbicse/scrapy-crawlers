# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.log import logger

from rlocker_crawler import db_handler
from rlocker_crawler.items import RlockerItem
from rlocker_crawler.models import Model


class NaturalinsectcontrolSpider(scrapy.Spider):
    name = 'nctl'
    __base_url = 'https://naturalinsectcontrol.com'
    allowed_domains = ['naturalinsectcontrol.com']
    start_urls = ['https://naturalinsectcontrol.com/shop.php', 'https://naturalinsectcontrol.com/specials.php']

    # def start_requests(self):
    #     uri = 'https://naturalinsectcontrol.com/subcat.php?cat=5&subcat=16'
    #     yield Request(url=uri, callback=self.parse_sub_category)

    def parse(self, response):
        links = response.xpath('//td[@class="shoptile"]/a/@href').getall()
        for link in links:
            uri = self.__base_url + '/' + link

            if '?id=' in uri:
                try:
                    session = db_handler.Session()
                    query = {'url': uri, 'spider': self.name}
                    q_data = session.query(Model).filter_by(**query).first()
                    if not q_data:
                        yield Request(url=uri, callback=self.parse_details)
                    else:
                        logger.debug('URL: {} already exists!'.format(uri))
                except:
                    pass

                finally:
                    session.close()
            else:
                yield Request(url=uri, callback=self.parse_category)

    def parse_category(self, response):
        links = response.xpath('//a[@class="productlink"]/@href').getall()
        for link in links:
            uri = self.__base_url + '/' + link
            yield Request(url=uri, callback=self.parse_sub_category)

    def parse_sub_category(self, response):
        try:
            # print(response.body)
            session = db_handler.Session()
            products = response.xpath('//td[@class="shoptile"]/a/@href').getall()
            for product in products:
                product_url = self.__base_url + '/' + product
                query = {'url': product_url, 'spider': self.name}
                q_data = session.query(Model).filter_by(**query).first()
                if not q_data:
                    yield Request(url=product_url, callback=self.parse_details)
                else:
                    logger.debug('URL: {} already exists!'.format(product_url))
        except Exception as x:
            logger.error('Error parse cate: {}'.format(x))

        finally:
            session.close()

    def parse_details(self, response):
        item = RlockerItem()
        item['url'] = response.url

        try:
            item['item_id'] = response.xpath('//dd[@class="productView-info-value"]/text()').get().strip()
        except:
            pass

        try:
            title = response.xpath('normalize-space(//table[@style="padding-top: 0px;"]/tr//td[2]/span)').get()
            item['title'] = title
        except:
            pass

        try:
            cats = []
            catalogs = response.xpath('//a[@class="paraheader"]/text()').getall()
            for catalog in catalogs:
                if 'Shop' in catalog:
                    continue

                cats.append(catalog.strip())
            item['category'] = ' > '.join(cats)
        except:
            pass

        try:
            im_urls = []
            big_img = response.xpath('//a[@class="productlink"]/@href').get()
            if big_img:
                im_urls.append(self.__base_url + big_img)
            item['images_url'] = '; '.join(im_urls)
        except:
            pass

        try:
            desc = response.xpath('normalize-space(//table[@style="padding-top: 0px;"]/tr//td[2]/p)').getall()
            item['description'] = ' '.join(desc)
        except:
            pass

        try:
            feature_text = response.xpath('normalize-space(//p[contains(., "Features:")])').get()
            item['variations'] = feature_text.replace('Features:', '')
        except:
            pass

        try:
            prices = []
            sizes = []
            size_texts = response.xpath('//input[@name="size"]/@value').getall()
            for size_text in size_texts:
                sp = size_text.split('|')
                prices.append(sp[-1])
                sizes.append(sp[0])

            item['price'] = ', '.join(prices)
            item['weight'] = ', '.join(sizes)
        except:
            pass

        return item
