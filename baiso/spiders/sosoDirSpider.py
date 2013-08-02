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
#import chardet

CHAPTERS_PER_PAGE = 10

'''soso dir spider'''

class sosoDirSpider(BaseSpider):
    name = 'soso_dirs'
    start_urls = ['http://k.soso.com/index.jsp']

    def __init__(self, *args, **kwargs):
        super(sosoDirSpider, self).__init__(*args, **kwargs)
        #log.start('soso_dir.log', log.INFO)
        book_conf = kwargs.get('book_conf')
        self.novel_cnums = {}
        self.rclient = redis.StrictRedis(host='localhost', port=6379, db=0)
        '''read conf'''
        with open(book_conf, "r") as fd:
            self.books = [x.strip() for x in fd.readlines()]
            fd.close()
        '''init chapter_size dict'''
        for book in self.books:
            chapter_size = "%s:%s" %(book, 'chapter_size')
            tmp = self.rclient.get(chapter_size)
            if tmp:
                self.novel_cnums[book] = int(tmp)
            else:
                self.novel_cnums[book] = 0

    def parse(self, response):
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
            novel_type = first.select('a/text()').extract()
            novel_chapter_nums = first.select('p[contains(@class, "info")]/text()').extract()[0]
        else:
            other = hxs.select('//div[contains(@class, "con")]/ul[contains(@class, "list")]/li')[0]
            brief_link = other.select('a/@href').extract()[0]
            novel_type = other.select('a/text()').extract()
            novel_chapter_nums = other.select('p[contains(@class, "info")]/text()').extract()[0]

        novel_type = [elem for elem in novel_type]
        novel_type = ' '.join(novel_type)
            
        novel_chapter_nums = novel_chapter_nums.encode('utf-8', 'ignore')
        novel_chapter_nums = int(re.search(r'\d+', novel_chapter_nums).group(0))
        if not (novel_chapter_nums > self.novel_cnums[_meta['book']]):
            pass

        novel_type = novel_type.encode('utf-8', 'ignore')
        novel_type = re.search(r'\[(.*?)\]', novel_type).group(1)
        brief_link = "%s%s" %("http://k.soso.com", brief_link)
        _meta['novel_type'] = novel_type
        _meta['novel_chapter_nums'] = novel_chapter_nums
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
        chapter_info_key = "%s:%s" %(_meta['book'], 'chapter_info')
        self.rclient.set(chapter_info_key, value)

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
                print 'a'*20, response.url
                pass
            url = "%s%s" %("http://k.soso.com", links[0])
            novel_chapter_nums = response.meta['novel_chapter_nums']
            count = novel_chapter_nums / CHAPTERS_PER_PAGE + 1
            lno = re.findall('lno=\d+', url)[0]
            pos1 = url.find(lno)
            pos2 = pos1 + len(lno)
            dir_urls = ["%slno=%d%s" %(url[:pos1], x, url[pos2:]) for x in range(1, count + 1)]
            print 'b'*20, dir_urls
        except:
            print 'a'*20
            
    
    """def parse_dir(self, response):
        _meta = response.meta
        book = _meta['book']
        log.msg('step\t%s\t%s' %(book, response.url), level=log.INFO)
        hxs = HtmlXPathSelector(response)
        content = hxs.select('//div[contains(@class, "con")]')[1] 
        chapter_links = content.select('ul/li/a/@href').extract()
        chapter_names = content.select('ul/li/a/text()').extract()
        log.msg("chapter_links:%d\tchapter_names:%d" %(len(chapter_links), len(chapter_names)), level=log.INFO)
        tmp = _meta['cur_index']
        _meta['cur_index'] += len(chapter_links)
        if _meta['cur_index'] > self.novel_cnums[book]:
            res = self.novel_cnums[book] - tmp
            if res > 0 and res < len(chapter_links):
                start = res
                chapter_links = chapter_links[start:]
                chapter_names = chapter_names[start:]

            chapter_links_key = "%s:%s" %(book, 'chapter_links')
            chapter_names_key = "%s:%s" %(book, 'chapter_names')
            detail_len = self.rclient.llen('soso_details:start_urls')
            log.msg("detail_len\t%d" %(detail_len), log.INFO)
            pipe = self.rclient.pipeline()
            for chapter_link in chapter_links:
                pipe.rpush('soso_details:start_urls', chapter_link)
                pipe.rpush(chapter_links_key, chapter_link)
            for chapter_name in chapter_names:
                pipe.rpush(chapter_names_key, chapter_name.encode('utf-8', 'ignore'))
            chapter_size = "%s:%s" %(book, 'chapter_size')
            pipe.set(chapter_size, _meta['cur_index'])
            pipe.execute()
            detail_len = self.rclient.llen('soso_details:start_urls')
            log.msg("after crawl %s\tdetail_len\t%d" %(book, detail_len), log.INFO)
        links = hxs.select('//div[contains(@class, "con")]/div[contains(@class, "page")]/p/a/@href').extract()
        tags = hxs.select('//div[contains(@class, "con")]/div[contains(@class, "page")]/p/a/text()').extract()
        next_tag = tags[0].encode('utf-8', 'ignore')
        if next_tag == "下一页":
            next_link = "%s%s" %("http://k.soso.com", links[0])
            yield Request(next_link, 
                meta = _meta,
                callback=self.parse_dir)
        else:
            pass"""
