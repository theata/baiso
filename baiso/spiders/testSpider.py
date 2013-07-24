from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector


class testSpider(BaseSpider):
    name = 'testSpider'
    start_urls = ['http://b.wap.soso.com/novel/detail.jsp?sid=ATIEmIAuTt4vXi3rA4HjpqpE&ipos=0&nn=%E5%A4%A7%E4%B8%BB%E5%AE%B0&type=%E6%90%9C%E5%B0%8F%E8%AF%B4&url=http%3A%2F%2Fread.qidian.com%2Fbookreader%2F2750457%252C46354696.aspx&pos=1&id=18312054131516090789&icfa=1304075&cmd=16693548951842619394&s=1&md=16693548951842633516&ssid=02a0dd64534f5195ff563768534f413a&g_ut=2&key=%E5%A4%A7%E4%B8%BB%E5%AE%B0%20%E5%A4%A9%E8%9A%95%E5%9C%9F%E8%B1%86']

    def parse(self, response):
        print 'xxxxxxxxxxxxxxxxxx'
        print response.body
        print 'ooooooooooooooooooo'
