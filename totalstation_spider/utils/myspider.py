#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from scrapy.http import HtmlResponse
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy_splash import SplashJsonResponse, SplashTextResponse, SplashResponse
from scrapy_splash import SplashRequest
from ..utils import default_script

from ..utils import get_headers


class SplashRedisCrawlSpider(RedisCrawlSpider):

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        _spider = super(SplashRedisCrawlSpider, cls).from_crawler(crawler, *args, **kwargs)
        # obj.setup_redis(crawler)
        return _spider

    # 重写CrawlSpider 的这个方法
    def _requests_to_follow(self, response):
        if not isinstance(response, (HtmlResponse, SplashJsonResponse, SplashTextResponse, SplashResponse)):
            return
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [lnk for lnk in rule.link_extractor.extract_links(response)
                     if lnk not in seen]
            if links and rule.process_links:
                # 修改process_links方法，增加一个参数 response.url，用来作为过滤条件
                links = rule.process_links(links, response.url)
            for link in links:
                seen.add(link)
                r = self._build_request(n, link)
                yield rule.process_request(r)

    def _build_request(self, rule, link):
        # 重要！！！！！这里重写父类方法，特别注意，需要传递meta={'rule': rule, 'link_text': link.text}
        # 详细可以查看 CrawlSpider 的源码

        headers = get_headers()
        meta = {'rule': rule, 'link_text': link.text}
        # TODO args 考虑是否需要修改，这里的wait是否需要根据环境变量来获取
        args = {'wait': 5, 'url': link.url, 'lua_source': default_script}
        r = SplashRequest(url=link.url, callback=self._response_downloaded, meta=meta, splash_headers=headers,
                          endpoint='execute', headers=headers, args=args)
        r.meta.update(rule=rule, link_text=link.text)
        return r

