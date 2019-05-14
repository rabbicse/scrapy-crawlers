# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request, FormRequest
from scrapy.log import logger

from rlocker_crawler import db_handler
from rlocker_crawler.items import RlockerItem
from rlocker_crawler.models import Model


class PgardenSpider(scrapy.Spider):
    name = 'pgarden'
    __base_url = 'https://professionalgardening.com'
    allowed_domains = ['professionalgardening.com']
    start_urls = ['https://professionalgardening.com/products']

    # def start_requests(self):
    #     uri = 'https://professionalgardening.com/ProductDetail/101190_Sugar-Peak-Flowering-245---1l--1-Qt'
    #     yield Request(url=uri, callback=self.parse_details)

    def parse(self, response):
        product_links = response.xpath('//ul[@id="products"]/li/a/@href').getall()
        for product_link in product_links:
            product_url = self.__base_url + product_link
            yield Request(url=product_url, callback=self.parse_products)

    def parse_products(self, response):
        session = db_handler.Session()
        try:
            p_links = response.xpath('//div[@class="product-description-title"]/a/@href').getall()
            logger.info('Total links: {}'.format(len(p_links)))
            for p_link in p_links:
                details_url = self.__base_url + p_link
                query = {'url': details_url, 'spider': self.name}
                q_data = session.query(Model).filter_by(**query).first()
                if not q_data:
                    yield Request(url=details_url, callback=self.parse_details)
                else:
                    logger.debug('URL: {} already exists!'.format(details_url))
        except:
            pass
        finally:
            session.close()

        next_link = response.xpath('//li[@class="nextLink "]')
        if next_link:
            href_l = next_link.xpath('./a/@href').get()
            if not href_l:
                return

            m = re.search(r'\(\'([^\']*?)\'', href_l)
            if not m:
                return

            k = m.group(1)
            form_data = {'__EVENTTARGET': k}  # 'ctl00$ContentPlaceHolder2$C002$pagesList$ctl10$LinkButton4'}
            view_state = response.xpath('//input[@id="__VIEWSTATE"]/@value').get()
            __VIEWSTATEGENERATOR = response.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value').get()
            __EVENTVALIDATION = response.xpath('//input[@id="__EVENTVALIDATION"]/@value').get()
            form_data['__VIEWSTATE'] = view_state
            form_data['__VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
            form_data['__EVENTVALIDATION'] = __EVENTVALIDATION

            yield FormRequest(url=response.url, formdata=form_data, callback=self.parse_products)

    def parse_details(self, response):
        item = RlockerItem()
        item['url'] = response.url

        id = response.url.split('/')[-1].split('_')[0]
        item['item_id'] = id
        title = response.xpath('//h1[@class="pageTitle"]/text()').get()
        item['title'] = title.strip() if title else ''
        li_list = response.xpath('//div[@class="product-breadcrumb"]//li/a/text()').getall()
        if li_list and len(li_list) > 1:
            item['category'] = li_list[1]
        brand = response.xpath('//div[@class="item-brand2"]/a/text()').get()
        item['brand'] = brand.strip() if brand else ''

        images = response.xpath('//ul[@id="gallery"]//a[@id="zoom-me"]/@href').getall()
        item['images_url'] = '; '.join([self.__base_url + im for im in images])

        item['price'] = response.xpath('//span[@class="priceLarge"]/text()').get()

        item['description'] = response.xpath('//span[@class="itemDesc"]/text()').get()

        varients = []
        varient_tags = response.xpath('//div[@class="product-similar-inner"]//tr')
        for varient_tag in varient_tags:
            tds = varient_tag.xpath('.//td')
            if tds and len(tds) >= 3:
                txt = tds[2].xpath('./text()').get()
                varients.append(txt)
        item['variations'] = ', '.join(varients)
        if len(varients) > 0:
            item['weight'] = varients[0]

        return item
