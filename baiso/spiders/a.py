from scrapy_redis.spiders import RedisSpider
from scrapy.selector import HtmlXPathSelector
from scrapy import log
import urlparse

class SosoDirSpider(RedisSpider):
    name = 'soso'
    redis_key = 'soso_dirs:start_urls'

    def __init__(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        self.rclient = redis.Redis(connection_pool=pool)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        res = urlparse.urlparse(response.url)
        content = hxs.select('//div[contains(@class, "con")]')[1] 
        chapter_links = content.select('ul/li/a/@href').extract()
        chapter_names = content.select('ul/li/a/text()').extract()


