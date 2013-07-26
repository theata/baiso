# Scrapy settings for baiso project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'baiso'

SPIDER_MODULES = ['baiso.spiders']
NEWSPIDER_MODULE = 'baiso.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'baiso (+http://www.yourdomain.com)'

#DOWNLOAD_TIMEOUT = 60
#DOWNLOAD_DELAY = 2
COOKIES_ENABLED = True
COOKIES_DEBUG = True
#RETRY_ENABLE = False
#DEPTH_LIMIT = 3
#LOG_FILE = 'crawl.log'
#LOG_LEVEL = 'INFO'

USER_AGENT = "Opera/12.02 (Android 4.1; Linux; Opera Mobi/ADR-1111101157; U; en-US) Presto/2.9.201 Version/12.02"

SOSO_DIR_REQUEST_HEADERS = {
    'Accept': ' text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding' : 'gzip, deflate',
    'Accept-Language' : 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Host': 'k.soso.com',
    #'Host': 'b2.wap.soso.com',
    'Referer' : 'http://k.soso.com/index.jsp',
    'User-Agent' : USER_AGENT,
}

SOSO_DETAIL_REQUEST_HEADERS = {
    'Accept': ' text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding' : 'gzip, deflate',
    'Accept-Language' : 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Host': 'b2.wap.soso.com',
    #'Referer' : 'http://k.soso.com/index.jsp',
    'User-Agent' : USER_AGENT,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': 600,
    'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware': 700,
    'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': 800,
}


# enables scheduling storing requests queue in redis
#SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# don't cleanup redis queues, allows to pause/resume crawls
#SCHEDULER_PERSIST = True

# Schedule requests using a priority queue. (default)
#SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'

# Schedule requests using a queue (FIFO).
#SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderQueue'

# Schedule requests using a stack (LIFO).
#SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderStack'

# Max idle time to prevent the spider from being closed when distributed crawling
# this only work if queue class is SpiderQueue or SpiderStack
# and may also block the same time when your spider start at the first time (because the queue is empty).
#SCHEDULER_IDLE_BEFORE_CLOSE = 10


# store scraped item in redis for post-processing
#ITEM_PIPELINES = [
#    'scrapy_redis.pipelines.RedisPipeline',
#]
