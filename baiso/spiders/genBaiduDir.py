#-*- coding:utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.http import FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
from scrapy import log

'''baidu dir spider'''


class GenBaiduDir(BaseSpider):
    name = 'baidu_dirs'
    start_urls = ['http://wap.baidu.com']
    #books = ['绝世唐门', '凡人修仙传', '大主宰']

    def __init__(self, *args, **kwargs):
        super(GetBaiduDir, self).__init__(*args, **kwargs)
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
        for novel in GenBaiduDir.novels:
            yield FormRequest.from_response(response,
                formdata = {'word': novel},
                meta = {'novel': novel},
                callback = self.after_submit)

    def after_submit(self, response):
        _meta = response.meta
        hxs = HtmlXPathSelector(response)
        resitem = hxs.select('//div[contains(@class, "reswrap")]/div/div[contains(@class, resitem)]')[0]
        pos = response.url.find("s?")
        if pos == -1:
            log.msg("can't find novel\t%s" %(_meta['novel']), log=level.INFO)
        else:
            head_url = response.url[:pos]
            tail_url = resitem.select('a/@href').extract()[0]
            print head_url, tail_url
            novel_url = ''.join([head_url, tail_url[2:]])
            #log.msg("get url %(novel_url)s", level=log.INFO, novel_url)
            yield Request(novel_url,
                    callback = self.parse_novel)

    def  parse_novel(self, response):
        hxs = HtmlXPathSelector(response)
        ori_url = hxs.select('//span[contains(@class, "ori_url")]')
        print response.status, response.url
        if not ori_url:
            print 'empty' * 20
            pass




