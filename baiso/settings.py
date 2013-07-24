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

USER_AGENT = "Opera/12.02 (Android 4.1; Linux; Opera Mobi/ADR-1111101157; U; en-US) Presto/2.9.201 Version/12.02"

DEFAULT_REQUEST_HEADERS = {
    'Accept': ' text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding' : 'gzip, deflate',
    'Accept-Language' : 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Host': 'k.soso.com',
    'Referer': 'http://k.soso.com/index.jsp',
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': 600,
    'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware': 700,
    'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': 800,
}
