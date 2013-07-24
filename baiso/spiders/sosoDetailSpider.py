from scrapy_redis.spiders import RedisSpider
import redis

class sosoDetailSpider(RedisSpider):
    name = "sosoDetailSpider"


    def __init__(self):
        self.rclient = redis.StrictRedis(host='localhost', port=6379, db=0)
    

    def parser(self, response):
        print 'xxxxxxxxxxxxxxxxxxxxx'
        print response 
        print 'ooooooooooooooooooooo'

          
