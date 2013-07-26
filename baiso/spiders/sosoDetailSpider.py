from scrapy_redis.spiders import RedisSpider
import redis
import hashlib

class sosoDetailSpider(RedisSpider):
    name = 'soso_details'
    redis_key = 'soso_details:start_urls'

    def __init__(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        self.rclient = redis.Redis(connection_pool=pool)
    
    def parse(self, response):
        '''write detail page in redis'''
        if response.status == 200:
            hexkey = hashlib.md5(response.url).hexdigest()
            self.rclient.set(hexkey, response.body)

          
