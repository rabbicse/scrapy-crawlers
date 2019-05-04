# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request

from alle_crawler.items import AlleCrawlerItem


class AlleSpider(scrapy.Spider):
    name = 'alle'
    __page_url = 'https://www.alle-immobilien.ch/en/buy/house/?pageNum={}'
    allowed_domains = ['alle-immobilien.ch']
    # start_urls = ['https://www.alle-immobilien.ch/en/buy/house/']

    def start_requests(self):
        for i in range(1, 1500):
            yield Request(url=self.__page_url.format(i), callback=self.parse)

    def parse(self, response):
        results = response.xpath('//a[@class="row search-results__list__item"]')
        for result in results:
            try:
                item = AlleCrawlerItem()
                item['listing_url'] = result.xpath('./@href').get()
                item['title'] = result.xpath('.//h2/text()').get()
                address = result.xpath(
                    'normalize-space(.//div[@class="col-xs-6 col-lg-3 tag__block tag__address"]/div[@class="tag-holder"])').get()
                item['address'] = address.replace('Address', '').strip()

                tags = result.xpath('.//div[@class="col-xs-6 col-lg-3 tag__block"]')
                item['surface'] = tags[0].xpath('normalize-space(.//div[@class="tag-holder"])').get()
                item['rooms'] = tags[1].xpath('normalize-space(.//div[@class="tag-holder"])').get()
                item['price'] = result.xpath('normalize-space(.//div[@class="price-tag"])').get()
                yield item
            except:
                pass

        # next_tag = response.xpath('//a[@data-gtm-id="search-results-paging-next-page"]/@href').get()
        # if next_tag and next_tag != '':
        #     yield Request(url=next_tag, callback=self.parse)
