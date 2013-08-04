from scrapy_redis.spiders import RedisSpider
from scrapy import log
import redis
import hashlib

class GetSosoDetail(RedisSpider):
    name = 'get_soso_details'
    redis_key = 'soso_details:start_urls'

    def __init__(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        self.rclient = redis.Redis(connection_pool=pool)

    def parse(self, response):
        '''write detail page in redis'''
        if response.status == 200:
            hexkey = hashlib.md5(response.url).hexdigest()
            self.rclient.set(hexkey, response.body)
            log.msg("crawl success\t%s" %(response.url,), level=log.INFO)
        else:
            log.msg("crawl failure\t%s\t%d" %(response.url, resposne.status), level=log.INFO)



