# -*- coding: utf-8 -*-
import scrapy
import logging
import sys
import json
import os
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from libraries.constants import Constants as SpecificCons

class DesaparecidosSpider(scrapy.Spider):

    specific_cons = SpecificCons()

    name = "fbiTopTen"
    initUrl = "https://www.fbi.gov/wanted/topten"

    startUrls = [initUrl]
    jsonUserData = None
    __allowed = ("jsonUserData")

    data_most_wanted = []
    count = 0

    def __init__(self, *args, **kwargs):
        logger = logging.getLogger('scrapy.spidermiddlewares.httperror')
        logger.setLevel(logging.ERROR)
        super(DesaparecidosSpider, self).__init__(*args, **kwargs)
        for k, v in kwargs.items():
            if( k in self.__class__.__allowed):
                setattr(self, k, v)
        self.jsonUserData = json.loads(self.jsonUserData)

    def camel_case(self, s):
        s = re.sub(r"(_|-)+", " ", s).title().replace(" ", "")
        return ''.join([s[0].lower(), s[1:]])

    def start_requests(self):
        for url in self.startUrls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        params = '&_layouteditor=true&display_fields=%28%27image%27%2C%29&display_type=wanted-grid-natural&limit=15&sort_on=getObjPositionInParent&SearchableText='
        u = json.loads(response.xpath('//div[@class="pat-queryfilter"]/@data-pat-queryfilter').get())['ajaxResults']['url']+params
        url = u+self.jsonUserData.get('name', '')
        yield scrapy.Request(url=url, callback=self.list_wanted, dont_filter=True)

    def list_wanted(self, response):
        wanted = response.xpath('//ul/li[@class="portal-type-person castle-grid-block-item"]/a/@href').getall()
        self.count = len(wanted)
        for i in wanted:
             yield scrapy.Request(url=i, callback=self.data_wanted, dont_filter=True)

    def data_wanted(self, response):
        name = response.xpath('//h1[@class="documentFirstHeading"]/text()').get().title()
        alias = response.xpath('//div[@class="wanted-person-aliases"]/p/text()').get().replace('“','').replace('"','').replace('” ','').split(', ')
        reward = response.xpath('//div[@class="wanted-person-reward"]/p/text()').get()
        coution = response.xpath('//div[@class="wanted-person-caution"]/p/text()').get()
        dict_one = {}
        table = response.xpath('//table[@class="table table-striped wanted-person-description"]/tbody/tr')
        for row in table:
            key = self.camel_case(row.xpath('td[1]//text()').extract_first().replace('(s)','s'))
            info = {key : row.xpath('td[2]//text()').extract_first().replace('"','')}
            dict_one.update(info)

        dict_two = {'name': name, 'alias': alias, 'reward':reward, 'coution':coution, 'descriptionData':dict_one}
        self.data_most_wanted.append(dict_two)
        info = self.specific_cons.WANTEDS.format(wanteds=json.dumps(self.data_most_wanted),)
        if len(json.loads(info)['mostWanted']) == self.count:
            self.data_most_wanted.clear()
            yield json.loads(info)
