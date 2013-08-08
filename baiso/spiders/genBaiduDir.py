#-*- coding:utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.http import FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
from scrapy import log
import redis
import re
import urlparse
import simplejson

'''baidu dir spider'''


class GenBaiduDir(BaseSpider):
    name = 'baidu_dirs'
    start_urls = ['http://wap.baidu.com']

    def __init__(self, *args, **kwargs):
        super(GenBaiduDir, self).__init__(*args, **kwargs)
        novel_conf = kwargs.get('novel_conf')
        self.rclient = redis.StrictRedis(host='localhost', port=6379, db=1)
        self.init_novel_data(novel_conf)

    def init_novel_data(self, novel_conf):
        with open(novel_conf, "r") as f:
            self.novels = [x.strip() for x in f.readlines()]
            f.close()

        self.all_novel_chapters_num = {}

        for novel in self.novels:
            novel_chapters_num_key = "%s:%s:%s" %("baidu", novel, 'novel_chapters_num')
            novel_chapters_num = self.rclient.get(novel_chapters_num_key)
            if not novel_chapters_num:
                novel_chapters_num = 0
            self.all_novel_chapters_num[novel] = novel_chapters_num

    def parse(self, response):
        print response.url, response.status
        for novel in self.novels:
            yield FormRequest.from_response(response,
                formdata = {'word': novel},
                meta = {'novel': novel},
                callback = self.after_submit)

    def after_submit(self, response):
        #_meta = response.meta
        hxs = HtmlXPathSelector(response)
        ala_novel_info = hxs.select('//div[contains(@class, "sigma_card_novel")]/div[contains(@class, "ala_novel_info")]')
        href = ala_novel_info.select('div[contains(@class, "ala_novel_title")]/a/@href').extract()[0]
        url = response.url
        try:
            baiduid = re.search('baiduid=([A-Z0-9]+)', url).group(1)
        except:
            log.msg("can not get baiduid", level=log.INFO)
            pass

        pos1 = url.find('s?')
        head = url[:pos1]

        pos2 = href.find('tc?') + len('tc?')
        mid = href[2:pos2]

        dir_url = "%s%s" %(head, mid)

        qsk = ['srd', 'appui', 'ajax', 'alalog', 'gid', 'baiduid', 'ref', 'lid', 'fm', 'order', 'tj', 'sec', 'di', 'src', 'hasRp', 'dir']

        qs_static = {'ajax':'1', 'alalog':'1', 'ref':'www_iphone', 'hasRp':'true', 'dir':'1', 'baiduid':baiduid}

        qs = {}
        qs.update(qs_static)

        qs_dynamic = urlparse.parse_qs(href[2:])
        for k,v in qs_dynamic.iteritems():
            qs[k] = v[0]

        for qw in qsk:
            if qs.get(qw):
                dir_url = "%s%s=%s&" %(dir_url, qw, qs.get(qw))

        dir_url = dir_url[:-1]

        print dir_url


        yield Request(dir_url,
            #meta = _meta,
            callback = self.parse_novel)

    def  parse_novel(self, response):
        data = response.body
        #print 'x'*10, data
        d = simplejson.loads(data)
        if d['status']:
            print 'succcess'
        else:
            print 'failed'
        print d['data']['chapter_num']




