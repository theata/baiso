from scrapy_redis.spiders import RedisSpider
from scrapy.selector import HtmlXPathSelector

class MySpider(RedisSpider):
    name = 'myspider'

    def parse(self, response):  
        print 'xxxxxxxxxxxxxxxxxxxxxx'
        hxs = HtmlXPathSelector(response)
        print 'oooooooooooooooooooooo'
