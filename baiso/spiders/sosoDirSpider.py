#-*- coding:utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.http import FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
import redis


'''soso dir spider'''

class sosoDirSpider(BaseSpider):
    name = 'sosoDirSpider'
    start_urls = ['http://k.soso.com/index.jsp']

    def __init__(self):
        self.detail_list = []
        self.rclient = redis.StrictRedis(host='localhost', port=6379, db=0)

    def parse(self, response):
        return [FormRequest.from_response(response,
                    formdata={'key': '大主宰 天蚕土豆'},
                    #formdata={'key': '重生到穷途末世abcdefaefa 无疆君'},
                    #formdata={'key': '终极圣灵 天玄者'},
                    callback = self.after_submit)]

    def after_submit(self, response):
        hxs = HtmlXPathSelector(response)
        first = hxs.select('//div[contains(@class, "first bdt")]')
        if first:
            brief_link = first.select('a/@href').extract()[0]
        else:
            other = hxs.select('//div[contains(@class, "con")]/ul[contains(@class, "list")]/li')[0]
            brief_link = other.select('a/@href').extract()[0]
        brief_link = "%s%s" %("http://k.soso.com", brief_link)
        yield Request(brief_link, callback=self.parse_brief)


    def parse_brief(self, response):
        hxs = HtmlXPathSelector(response)
        dir_link = hxs.select('//div[contains(@class,"con")]/p[contains(@class, "mt1")]/a/@href').extract()[0]
        dir_link = "%s%s" %("http://k.soso.com", dir_link)
        yield Request(dir_link, callback=self.parse_dir)
        print self.detail_list
    
    def parse_dir(self, response):
        hxs = HtmlXPathSelector(response)
        content = hxs.select('//div[contains(@class, "con")]')[1] 
        chapters = content.select('ul/li/a/@href').extract()

        for chapter in chapters:
            self.detail_list.append(chapter)
        links = hxs.select('//div[contains(@class, "con")]/div[contains(@class, "page")]/p/a/@href').extract()
        tags = hxs.select('//div[contains(@class, "con")]/div[contains(@class, "page")]/p/a/text()').extract()
        next_tag = tags[0].encode('utf-8', 'ignore')
        if next_tag == "下一页":
            next_link = "%s%s" %("http://k.soso.com", links[0])
            yield Request(next_link, callback=self.parse_dir)
        else:
            print 'xxxxxxxxxxxxxxxxxxxxxxxxxx', len(self.detail_list)
            pipe = self.rclient.pipeline()
            for detail in self.detail_list:
                pipe.rpush('sosoDetailSpider:start_urls', detail)
            pipe.execute()





