# -*- coding: utf-8 -*-

import re
import os
import secrets
import inspect
import traceback
from lxml import etree
from urllib.parse import urljoin
from ..parser import Parser

class Javbus(Parser):
    
    source = 'javbus'

    expr_number = '/html/head/meta[@name="keywords"]/@content'
    expr_title = '/html/head/title/text()'
    expr_studio = '//span[contains(text(),"製作商:")]/../a/text()'
    expr_studio2 = '//span[contains(text(),"メーカー:")]/../a/text()'
    expr_director = '//span[contains(text(),"導演:")]/../a/text()'
    expr_directorJa = '//span[contains(text(),"監督:")]/../a/text()'
    expr_series = '//span[contains(text(),"系列:")]/../a/text()'
    expr_series2 = '//span[contains(text(),"シリーズ:")]/../a/text()'
    expr_label = '//span[contains(text(),"系列:")]/../a/text()'
    expr_cover = '//a[@class="bigImage"]/@href'
    expr_release = '/html/body/div[5]/div[1]/div[2]/p[2]/text()'
    expr_runtime = '/html/body/div[5]/div[1]/div[2]/p[3]/text()'
    expr_actor = '//div[@class="star-name"]/a'
    expr_actorphoto = '//div[@class="star-name"]/../a/img'
    expr_extrafanart = '//div[@id="sample-waterfall"]/a/@href'
    expr_tags = '/html/head/meta[@name="keywords"]/@content'
    expr_uncensored = '//*[@id="navbar"]/ul[1]/li[@class="active"]/a[contains(@href,"uncensored")]'

    def search(self, number):
        self.number = number
        try:
            self.detailurl = 'https://www.seejav.cfd/' + number
            self.htmlcode = self.getHtml(self.detailurl)
            htmltree = etree.fromstring(self.htmlcode,etree.HTMLParser())
            result = self.dictformat(htmltree)
            return result
        except Exception as e:
            print(e)
            traceback.format_exc()
            return 404
            # self.searchUncensored(number)

    # def searchUncensored(self, number):
    #     """ 二次搜索无码
    #     """
    #     self.imagecut = 0
    #     self.uncensored = True

    #     w_number = number.replace('.', '-')
    #     if self.specifiedUrl:
    #         self.detailurl = self.specifiedUrl
    #     else:
    #         self.detailurl = 'https://www.javbus.red/' + w_number
    #     self.htmlcode = self.getHtml(self.detailurl)
    #     if self.htmlcode == 404:
    #         return 404
    #     htmltree = etree.fromstring(self.htmlcode, etree.HTMLParser())
    #     result = self.dictformat(htmltree)
    #     return result

    def getNum(self, htmltree):
        return super().getNum(htmltree).split(',')[0]

    def getTitle(self, htmltree):
        title = super().getTitle(htmltree)
        title = str(re.findall('^.+?\s+(.*) - JavBus$', title)[0]).strip()
        return title

    def getStudio(self, htmltree):
        if self.uncensored:
            return self.getTreeElement(htmltree, self.expr_studio2)
        else:
            return self.getTreeElement(htmltree, self.expr_studio)

    def getCover(self, htmltree):
        return urljoin("https://www.seejav.cfd", super().getCover(htmltree)) 

    def getRuntime(self, htmltree):
        return super().getRuntime(htmltree).strip(" ['']分鐘")

    def getActors(self, htmltree):
        actors = super().getActors(htmltree)
        b=[]
        for i in actors:
            b.append(i.attrib['title'])
        return b
    
    def getActorPhoto(self, htmltree):
        actors = self.getTreeAll(htmltree, self.expr_actorphoto)
        d = {}
        for i in actors:
            p = i.attrib['src']
            if "nowprinting.gif" in p:
                continue
            t = i.attrib['title']
            d[t] = urljoin("https://www.seejav.cfd", p)
        return d

    def getDirector(self, htmltree):
        if self.uncensored:
            return self.getTreeElement(htmltree, self.expr_directorJa)
        else:
            return self.getTreeElement(htmltree, self.expr_director)

    def getSeries(self, htmltree):
        if self.uncensored:
            return self.getTreeElement(htmltree, self.expr_series2)
        else:
            return self.getTreeElement(htmltree, self.expr_series)

    def getTags(self, htmltree):
        tags = self.getTreeElement(htmltree, self.expr_tags).split(',')
        return tags[2:]

    def getOutline(self, htmltree):
        if self.morestoryline:
            from .storyline import getStoryline
            return getStoryline(self.number , uncensored = self.uncensored,
                                proxies=self.proxies, verify=self.verify)
        return ''
