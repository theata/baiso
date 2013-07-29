#-*- coding:utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.http import FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
from scrapy import log
#from ..settings import SOSO_DIR_REQUEST_HEADERS
import redis
import hashlib
import copy
import re
import simplejson

'''soso dir spider'''

class sosoDirSpider(BaseSpider):
    name = 'soso_dirs'
    start_urls = ['http://k.soso.com/index.jsp']

    def __init__(self, *args, **kwargs):
        super(sosoDirSpider, self).__init__(*args, **kwargs)
        #log.start('soso_dir.log', log.INFO)
        book_conf = kwargs.get('book_conf')
        self.chapter_links = []
        self.chapter_names = []
        self.rclient = redis.StrictRedis(host='localhost', port=6379, db=0)
        with open(book_conf, "r") as fd:
            self.books = [x.strip() for x in fd.readlines()]
            fd.close()
        print self.books

    def parse(self, response):
        log.msg("This is a info", level=log.INFO)
        for book in self.books:
            yield FormRequest.from_response(response,
                    formdata={'key': book},
                    meta = {'book': book},
                    #headers = SOSO_DIR_REQUEST_HEADERS,
                    callback = self.after_submit)

    def after_submit(self, response):
        _meta = response.meta
        hxs = HtmlXPathSelector(response)
        first = hxs.select('//div[contains(@class, "first bdt")]')
        if first:
            brief_link = first.select('a/@href').extract()[0]
            novel_type = first.select('a/text()').extract()[0]
            print '11111111111111111111'
        else:
            other = hxs.select('//div[contains(@class, "con")]/ul[contains(@class, "list")]/li')[0]
            brief_link = other.select('a/@href').extract()[0]
            novel_type = other.select('a/text()').extract()[1]
            print '2222222222222222222222'
        novel_type = novel_type.encode('utf-8', 'ignore')
        #print 'novel_type', novel_type
        novel_type = re.search(r'\[(.*?)\]', novel_type).group(1)
        brief_link = "%s%s" %("http://k.soso.com", brief_link)
        #print 'novel_type', novel_type, 'brief_link', brief_link
        _meta['novel_type'] = novel_type
        yield Request(brief_link, 
            meta = _meta,
            #headers = SOSO_DIR_REQUEST_HEADERS,
            callback=self.parse_brief)


    def parse_brief(self, response):
        _meta = response.meta
        hxs = HtmlXPathSelector(response)
        intro = hxs.select('//div[contains(@class, "con")]')[0].select('p').extract()[0]
        pattern = re.compile(r"<p>(.*)<br>")
        match = pattern.match(intro)
        if match:
            intro = match.group(1).encode('utf-8', 'ignore')
        else:
            intro = ''
        _meta['intro'] = intro
        dir_link = hxs.select('//div[contains(@class,"con")]/p[contains(@class, "mt1")]/a/@href').extract()[0]
        dir_link = "%s%s" %("http://k.soso.com", dir_link)
        yield Request(dir_link, 
            meta = _meta,
            #headers = SOSO_DIR_REQUEST_HEADERS,
            callback=self.parse_dir)
    
    def parse_dir(self, response):
        _meta = response.meta
        book = _meta['book']
        hxs = HtmlXPathSelector(response)
        content = hxs.select('//div[contains(@class, "con")]')[1] 
        chapter_links = content.select('ul/li/a/@href').extract()
        chapter_names = content.select('ul/li/a/text()').extract()
        if len(chapter_links) == len(chapter_names):       
            for chapter_link in chapter_links:
                self.chapter_links.append(chapter_link)
            for chapter_name in chapter_names:
                self.chapter_names.append(chapter_name.encode('utf-8', 'ignore'))
        links = hxs.select('//div[contains(@class, "con")]/div[contains(@class, "page")]/p/a/@href').extract()
        tags = hxs.select('//div[contains(@class, "con")]/div[contains(@class, "page")]/p/a/text()').extract()
        next_tag = tags[0].encode('utf-8', 'ignore')
        if next_tag == "下一页":
            next_link = "%s%s" %("http://k.soso.com", links[0])
            yield Request(next_link, 
                meta = _meta,
                #headers = SOSO_DIR_REQUEST_HEADERS,
                callback=self.parse_dir)
        else:
            chapter_links = copy.copy(self.chapter_links)
            chapter_names = copy.copy(self.chapter_names)
            chapter_size = len(chapter_links)
            chapter_size_key = "%s:%s" %(book, "chapter_size")
            dir_size = self.rclient.get(chapter_size_key)
            if  dir_size:
                if chapter_size - dir_size > 0:
                    chapter_links = chapter_links[:chapter_size - dir_size]
                    chapter_names = chapter_names[:chapter_size - dir_size]
                    log.msg("%s\tappend new\t%d\tchapters" %(book, chapter_size-dir_size), level=log.INFO)
                    self.rclient.set(hex_chapter_size_key, chapter_size)
                else:
                    log.msg("%s\tnot update" %(book), level=log.INFO)
            else:
                log.msg("%s\tfirst crawl has\t%d\tchapters" %(book, chapter_size), level=log.INFO)
                self.rclient.set(chapter_size_key, chapter_size)
            
            if not dir_size or (chapter_size - dir_size) > 0:
                chapter_links_key = "%s:%s" %(book, 'chapter_links')
                chapter_names_key = "%s:%s" %(book, 'chapter_names')
                chapter_info_key = "%s:%s" %(book, 'chapter_info')
                detail_len = self.rclient.llen('soso_details:start_urls')
                log.msg("detail_len\t%d" %(detail_len), log.INFO)
                pipe = self.rclient.pipeline()
                for chapter_link in chapter_links:
                    pipe.rpush('soso_details:start_urls', chapter_link)
                    pipe.rpush(chapter_links_key, chapter_link)
                for chapter_name in chapter_names:
                    pipe.rpush(chapter_names_key, chapter_name)

                if not dir_size:
                    d = {'novel_type': _meta['novel_type'],
                        'introduction': _meta['intro'],
                    }
                value = simplejson.dumps(d)
                pipe.set(chapter_info_key, value)
            pipe.execute()

            detail_len = self.rclient.llen('soso_details:start_urls')
            log.msg("after crawl %s\tdetail_len\t%d" %(book, detail_len), log.INFO)

            self.chapter_links = []
            self.chapter_names = []





