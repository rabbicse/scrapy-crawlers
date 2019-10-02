# -*- coding: utf-8 -*-
import json
import string

import scrapy
from scrapy import Request, Selector
from scrapy.log import logger

from cloudscene import db_handler
from cloudscene.items import CesItem
from cloudscene.models import Ces


class Ces19Spider(scrapy.Spider):
    name = 'ces19'
    __details_uri = 'https://ces19.mapyourshow.com/7_0/exhibitor/exhibitor-details.cfm?ExhID={}'
    __init_search_uri = 'https://ces19.mapyourshow.com/7_0/search/_search-results.cfm?searchType=exhibitor&exhibitor={}&increment=100'
    __search_uri = 'https://ces19.mapyourshow.com/7_0/search/_search-results.cfm?searchType=exhibitor&getMoreResults=true&exhibitor={}&startRow={}&endRow={}'
    allowed_domains = ['ces19.mapyourshow.com']
    start_urls = ['http://ces19.mapyourshow.com/']

    def start_requests(self):
        # uri = 'https://ces19.mapyourshow.com/7_0/exhibitor/exhibitor-details.cfm?ExhID=T0007383'
        # yield Request(url=uri, callback=self.parse_details, meta={'url': uri})
        # return

        # uri = 'https://ces19.mapyourshow.com/7_0/search/_search-results.cfm?searchType=exhibitor&exhibitor=A&increment=100'
        start = 1
        end = 100
        for c in string.ascii_uppercase:
            uri = self.__init_search_uri.format(c)
            yield Request(url=uri, callback=self.parse, meta={'start': start, 'end': end, 'alpha': c}, headers={'x-requested-with': 'XMLHttpRequest'})

        uri = self.__init_search_uri.format('0')
        yield Request(url=uri, callback=self.parse, meta={'start': start, 'end': end, 'alpha': '0'},
                      headers={'x-requested-with': 'XMLHttpRequest'})

    def parse(self, response):
        try:
            session = db_handler.Session()
            json_data = json.loads(response.body)
            if json_data['SUCCESS']:
                has_data = False
                sel = Selector(text=str(json_data['DATA']['BODYHTML']))
                try:
                    id_list = sel.xpath('//tr/@data-exhid').getall()
                    has_data = len(id_list) > 0
                    for id in id_list:
                        details_uri = self.__details_uri.format(id)
                        query = {'url': details_uri}
                        q_data = session.query(Ces).filter_by(**query).first()
                        if not q_data:
                            yield Request(url=details_uri, callback=self.parse_details, meta={'url': details_uri})
                        else:
                            logger.debug('URL: {} already exists!'.format(details_uri))
                except Exception as x:
                    print(x)
                finally:
                    if has_data:
                        start = response.meta['start'] + 100
                        end = response.meta['end'] + 100
                        alpha = response.meta['alpha']
                        uri = self.__search_uri.format(alpha, start, end)
                        yield Request(url=uri, callback=self.parse, meta={'start': start, 'end': end, 'alpha': alpha},
                                      headers={'x-requested-with': 'XMLHttpRequest'})
        except Exception as ex:
            pass
        finally:
            session.close()


    def parse_details(self, response):
        item = CesItem()
        item['url'] = response.meta['url']
        try:
            item['name'] = response.xpath('normalize-space(//h1[@class="sc-Exhibitor_Name"])').get()
        except:
            pass

        try:
            item['address'] = response.xpath('normalize-space(//p[@class="sc-Exhibitor_Address"])').get()
        except:
            pass

        try:
            recs = response.xpath('//a[@class="mys-vert-align-middle mys-grey jq-title"]')
            for rec in recs:
                rec_text = rec.xpath('normalize-space(./strong)').get()
                if 'Brands' in rec_text:
                    item['brands'] = rec.xpath('normalize-space(following-sibling::div)').get()

                if 'Product Categories' in rec_text:
                    item['categories'] = rec.xpath('normalize-space(following-sibling::div)').get()

                if 'Company Contacts' in rec_text:
                    item['contacts'] = rec.xpath('normalize-space(following-sibling::div)').get()
        except:
            pass

        try:
            item['phone'] = response.xpath('normalize-space(//p[@class="sc-Exhibitor_PhoneFax"])').get().strip()
        except:
            pass

        try:
            item['website'] = response.xpath('//p[@class="sc-Exhibitor_Url"]/a/@href').get().strip()
        except:
            pass

        return item
