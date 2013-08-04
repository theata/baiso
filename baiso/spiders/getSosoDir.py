from scrapy_redis.spiders import RedisSpider
from scrapy.selector import HtmlXPathSelector
from scrapy import log
import urlparse
import redis

class GetSosoDir(RedisSpider):
    name = 'get_soso_dirs'
    redis_key = 'soso_dirs:start_urls'

    def __init__(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        self.rclient = redis.Redis(connection_pool=pool)

    def parse(self, response):
        query = urlparse.urlparse(response.url).query
        qs = urlparse.parse_qs(query)
        key = qs.get('key')
        index = int(qs.get('lno')[0]) if qs.get('lno') else 1

        hxs = HtmlXPathSelector(response)
        content = hxs.select('//div[contains(@class, "con")]')[1]
        chapter_links = content.select('ul/li/a/@href').extract()
        chapter_names = content.select('ul/li/a/text()').extract()
        chapter_names = [chapter_name.encode('utf-8', 'ignore') for chapter_name in chapter_names]
        chapter_len = len(chapter_links)

        '''get chapter's num of novel'''
        novel_chapters_num_key = "%s:%s" %(key, "novel_chapters_num")
        novel_chapters_num = self.rclient.get(novel_chapters_num_key)
        novel_chapters_num = int(novel_chapters_num) if novel_chapters_num else 0

        start = (index - 1) * 10 + 1
        end = start + chapter_len

        if novel_chapters_num >= end:
            log.msg("%s\tnovel_chapters_num\t%d greater than current end\t%d" %(key, novel_chapters_num, end), level=log.INFO)
        else:
            if novel_chapters_num >= start and novel_chapters_num < end:
                start = novel_chapters_num - novel_chapters_num/10*10 + 1
                end = 11

            if novel_chapters_num < start:
                start = 1
                end = 11

            '''novel_chapter_names_key, novel_chapter_links_key'''
            """novel_chapter_names_key = "%s:%s" %(key, novel_chapter_names)
            novel_chapter_links_key = "%s:%s" %(key, novel_chapter_links)"""

            pipe = self.rclient.pipeline()
            for i in range(start, end):
                j = (index - 1) * 10 + i
                chapter_name_key = "%s:%s:%s" %(key, "chapter_name", j)
                chapter_link_key = "%s:%s:%s" %(key, "chapter_link", j)
                pipe.rpush(chapter_name_key, chapter_names[i - 1])
                pipe.rpush(chapter_link_key, chapter_links[i - 1])
                print '-------------------push---', chapter_links[i - 1]
                pipe.rpush('soso_details:start_urls', chapter_links[i - 1])
            pipe.set(novel_chapters_num_key, novel_chapters_num + end - start)
            pipe.execute()


