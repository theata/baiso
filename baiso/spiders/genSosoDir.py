#-*- coding:utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.http import FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
from scrapy import log
import redis
import hashlib
import copy
import re
import simplejson
import urlparse

'''gen soso dir spider'''

class GenSosoDir(BaseSpider):
    name = 'gen_soso_dirs'
    start_urls = ['http://k.soso.com/index.jsp']
    redis_key = 'soso_dirs:start_urls'

    def __init__(self, *args, **kwargs):
        super(GenSosoDir, self).__init__(*args, **kwargs)
        #log.start('soso_dir.log', log.INFO)

        novel_conf = kwargs.get('novel_conf')
        #self.novel_chapters_nums = {}
        self.rclient = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.init_novel_data(novel_conf)

    def init_novel_data(self, novel_conf):
        with open(novel_conf, "r") as f:
            self.novels = [x.strip() for x in f.readlines()]
            f.close()

        self.all_novel_chapters_num = {}

        for novel in self.novels:
            novel_chapters_num_key = "%s:%s" %(novel, 'novel_chapters_num')
            novel_chapters_num = self.rclient.get(novel_chapters_num_key)
            if not novel_chapters_num:
                novel_chapters_num = 0
            self.all_novel_chapters_num[novel] = novel_chapters_num

    def parse(self, response):
        for novel in self.novels:
            yield FormRequest.from_response(response,
                    formdata={'key': novel},
                    meta = {'novel': novel},
                    #headers = SOSO_DIR_REQUEST_HEADERS,
                    callback = self.after_submit)

    def after_submit(self, response):
        _meta = response.meta
        hxs = HtmlXPathSelector(response)
        first = hxs.select('//div[contains(@class, "first bdt")]')
        if first:
            brief_link = first.select('a/@href').extract()[0]
            novel_type = first.select('a/text()').extract()
            novel_chapters_num = first.select('p[contains(@class, "info")]/text()').extract()[0]
        else:
            other = hxs.select('//div[contains(@class, "con")]/ul[contains(@class, "list")]/li')[0]
            brief_link = other.select('a/@href').extract()[0]
            novel_type = other.select('a/text()').extract()
            novel_chapters_num = other.select('p[contains(@class, "info")]/text()').extract()[0]

        novel_type = [elem for elem in novel_type]
        novel_type = ' '.join(novel_type)

        novel_chapters_num = novel_chapters_num.encode('utf-8', 'ignore')
        novel_chapters_num = int(re.search(r'\d+', novel_chapters_num).group(0))

        if novel_chapters_num <= self.all_novel_chapters_num.get(_meta['novel']):
            log.msg("%s\tnot update, the chapter num is\t%s" %(_meta['novel'], novel_chapters_num), level=log.INFO)
        else:
            novel_type = novel_type.encode('utf-8', 'ignore')
            novel_type = re.search(r'\[(.*?)\]', novel_type).group(1)
            brief_link = "%s%s" %("http://k.soso.com", brief_link)
            _meta['novel_type'] = novel_type
            _meta['novel_chapters_num'] = novel_chapters_num

            yield Request(brief_link,
                meta = _meta,
                #headers = SOSO_DIR_REQUEST_HEADERS,
                callback=self.parse_brief)


    def parse_brief(self, response):
        _meta = response.meta
        hxs = HtmlXPathSelector(response)
        try:
            intro = hxs.select('//div[contains(@class, "con")]')[0].select('p').extract()[0]
            pattern = re.compile(r"<p>(.*)<br>")
            match = pattern.match(intro)
            if match:
                intro = match.group(1).encode('utf-8', 'ignore')
            else:
                intro = ''
        except:
            intro = ''

        '''set novel chapter_info'''
        d = {'novel_type': _meta['novel_type'],
            'introduction': intro,
        }
        value = simplejson.dumps(d)
        novel_info_key = "%s:%s" %(_meta['novel'], 'novel_info')
        self.rclient.set(novel_info_key, value)

        dir_link = hxs.select('//div[contains(@class,"con")]/p[contains(@class, "mt1")]/a/@href').extract()[0]
        dir_link = "%s%s" %("http://k.soso.com", dir_link)
        yield Request(dir_link,
            meta = _meta,
            #headers = SOSO_DIR_REQUEST_HEADERS,
            callback=self.extract_dir_url)


    def extract_dir_url(self, response):
        hxs = HtmlXPathSelector(response)
        try:
            links = hxs.select('//div[contains(@class, "con")]/div[contains(@class, "page")]/p/a/@href').extract()
            tags = hxs.select('//div[contains(@class, "con")]/div[contains(@class, "page")]/p/a/text()').extract()
            next_tag = tags[0].encode('utf-8', 'ignore')
            if not next_tag == "下一页":
                self.rclient.rpush(GenSosoDir.redis_key, response.url)
                redis_key_len = self.rclient.llen(GenSosoDir.redis_key)
                log.msg("after put\t%s soso_dir_len is\t%d" %(response.url, redis_key_len), level=log.INFO)
            else:
                url = "%s%s" %("http://k.soso.com", links[0])
                novel_chapters_num = response.meta['novel_chapters_num']
                count = novel_chapters_num / 10 + 1
                lno = re.findall('lno=\d+', url)[0]
                pos1 = url.find(lno)
                pos2 = pos1 + len(lno)
                dir_urls = ["%slno=%d%s" %(url[:pos1], x, url[pos2:]) for x in range(1, count + 1)]
                pipe = self.rclient.pipeline()
                for dir_url in dir_urls:
                    pipe.rpush(GenSosoDir.redis_key, dir_url)
                pipe.execute()
                redis_key_len = self.rclient.llen(GenSosoDir.redis_key)
                log.msg("after put%s\t to \t%s soso_dir_len is\t%d" %(dir_urls[0], dir_urls[-1], redis_key_len), level=log.INFO)
        except:
            log.msg("extract dir url throw exception")


