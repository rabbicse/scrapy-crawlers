# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
from scrapy.log import logger

from rlocker_crawler import db_handler
from rlocker_crawler.items import RlockerItem
from rlocker_crawler.models import Model


class EddiswholesaleSpider(scrapy.Spider):
    # name = 'eddiswholesale'
    name = 'eddiswholesale_updated'
    __user = 'greenleafhydroponicscanada@gmail.com'
    __password = 'Familyfirst1.'
    __base_url = 'http://eddiswholesale.com'
    __img_base_uri = 'https://eddiswholesale-2.azureedge.net'
    allowed_domains = ['eddiswholesale.com']
    start_urls = ['http://eddiswholesale.com/']

    __headers = {'accept-encoding': 'gzip, deflate, br',
                 'accept-language': 'en-US,en;q=0.9,bn;q=0.8',
                 'cache-control': 'no-cache',
                 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                 'origin': 'https://www.eddiswholesale.com',
                 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
                 'x-requested-with': 'XMLHttpRequest'}

    def start_requests(self):
        uri = 'https://www.eddiswholesale.com/user-login?returnurl=my-account'
        yield Request(url=uri, callback=self.parse)

    def parse(self, response):
        print(response.headers)
        uri = 'https://www.eddiswholesale.com/ecomwgtlogin/login'
        post_param = {'UserName': self.__user,
                      'Password': self.__password,
                      'RememberMe': 'true',
                      'ReturnUrl': 'my-account',
                      'LostPasswordEmail': 'email@email.com',
                      'clearStatusQueue': 'true'}
        yield FormRequest(url=uri, formdata=post_param, headers=self.__headers, callback=self.parse_myaccount)

    def parse_myaccount(self, response):
        yield Request(url='https://www.eddiswholesale.com/my-account', callback=self.parse_myaccount1)

    def parse_myaccount1(self, response):
        yield Request(url='http://eddiswholesale.com/', callback=self.parse_data)

    def parse_data(self, response):
        links = response.xpath('//div[@class="span4"]/ul/li/a/@href').getall()
        for link in links:
            cat_url = self.__base_url + link
            yield Request(url=cat_url, callback=self.parse_category)

    def parse_category(self, response):
        try:
            session = db_handler.Session()
            products = response.xpath('//a[@class="product-title"]/@href').getall()
            for product in products:
                product_url = self.__base_url + product
                query = {'url': product_url, 'spider': self.name}
                q_data = session.query(Model).filter_by(**query).first()
                if not q_data:
                    yield Request(url=product_url, callback=self.parse_details, meta={'url': product_url})
                else:
                    logger.debug('URL: {} already exists!'.format(product_url))
        except:
            pass

        finally:
            session.close()

    def parse_details(self, response):
        item = RlockerItem()
        item['url'] = response.meta['url']

        try:
            item['item_id'] = response.xpath('//p[@class="product-details-code"]/text()').get().replace(
                'Product Code:', '').strip()
        except:
            pass

        title = ''
        try:
            title = response.xpath('//title/text()').get()
            item['title'] = title
        except:
            pass

        try:
            cats = []
            catalogs = response.xpath('//ul[@class="breadcrumb"]/li/a')
            for catalog in catalogs:
                t = catalog.xpath('./@title').get()
                if 'Home' in t or 'Catalog' in t:
                    continue

                cats.append(t.strip())
            item['category'] = ' > '.join(cats)
        except:
            pass

        # try:
        #     item['price'] = response.xpath('//span[@id="lblPriceRetailNoPriceValue"]/text()').get()
        # except:
        #     pass

        try:
            im_urls = []
            big_img = response.xpath('//img[@id="product-detail-gallery-main-img"]/@data-zoom-image').get()
            if big_img:
                im_urls.append(self.__img_base_uri + big_img)
            item['images_url'] = '; '.join(im_urls)
        except:
            pass

        try:
            desc = response.xpath('normalize-space(//div[@class="product-details-desc"])').get()
            desc = desc.replace(title, '').strip()
            item['description'] = desc
        except:
            pass

        try:
            price = response.xpath('normalize-space(//strong[@class="price price-current"])').get()
            item['price'] = price
        except:
            pass

        # print(item)
        return item
