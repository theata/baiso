#-*- coding:utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.http import FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request

'''baidu dir spider'''


class BaiduDirSpider(BaseSpider):
    name = 'baidu_dirs'
    start_urls = ['http://wap.baidu.com']
    books = ['绝世唐门', '凡人修仙传', '大主宰']

    
    def parse(self, response):
        for book in BaiduDirSpider.books:
            yield FormRequest.from_response(response,
                formdata = {'word': book},
                callback = self.after_submit)
    
    def after_submit(self, response):
        hxs = HtmlXPathSelector(response)
        resitem = hxs.select('//div[contains(@class, "reswrap")]/div/div[contains(@class, resitem)]')[0]
        #print response.status, response.url
        pos = response.url.find("s?") 
        if pos == -1:
            pass
        head_url = response.url[:pos]
        tail_url = resitem.select('a/@href').extract()[0]
        print head_url, tail_url
        novel_url = ''.join([head_url, tail_url[2:]])
        #log.msg("get url %(novel_url)s", level=log.INFO, novel_url)
        yield Request(novel_url,
                callback = self.parse_novel)

    def  parse_novel(self, response):
        hxs = HtmlXPathSelector(response)
        ori_url = hxs.select('//span[contains(@class, "ori_url")]')
        print response.status, response.url
        if not ori_url:
            print 'empty' * 20
            pass




