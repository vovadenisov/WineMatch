# -*- coding: utf-8 -*-

import re
import asyncio
try:
    from asyncio import JoinableQueue as Queue
except ImportError:
    from asyncio import Queue
    
from difflib import SequenceMatcher
from bs4 import BeautifulSoup as bs
import requests
from django.core.management.base import BaseCommand

from survey.models import Wine, WineShop #code name photo search_url answer_type base_url
from survey.models import WineToShop #wine, shop, price, url

CRAWLER_MAX_WORKERS = 10
SUCCESS_STATUS_CODES = [200, 202, ]
SIMULARITY_TRESHOLD = 0.5

def fix_ssl_unverified_err():
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
        ssl._create_default_https_context = _create_unverified_https_context
    except AttributeError:
        pass

class WineCrawler:
    def __init__(self):
        wines = WineToShop.objects.filter(shop_id=5) #simplewine shop id
        self.wine_queue = Queue()
        self.wines = {w.id: w for w in wines}

    @asyncio.coroutine
    def crawl(self):
        workers = [asyncio.Task(self.download_wine())
                   for _ in range(CRAWLER_MAX_WORKERS)]
        for wine in self.wines.keys():
            yield from self.wine_queue.put(wine)
        yield from self.wine_queue.join()
        for w in workers:
            w.cancel()

    @asyncio.coroutine
    def download_wine(self):
        while True:
            wine_id = yield from self.wine_queue.get()
            yield from self.process_wine(wine_id)#process_function(data[1])
            self.wine_queue.task_done()

    def _rm_non_informative_words(self, title):
        for word in ['Вино', 'г.', ',']:
            title = title.replace(word, '')
        title = title.lower()
        return title.strip()

    @asyncio.coroutine
    def process_wine(self, wine_id):
        wine = self.wines.get(wine_id)
        url = wine.url
        print(url)
        r = requests.get(url, verify=False, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
        if r.status_code not in SUCCESS_STATUS_CODES:
            print('wrong status code'.format(r.status_code))
            return
        wine_data = bs(r.text, 'html.parser')
        title_translit = yield from self.parse_wine(wine_data)
        if not title_translit:
            print('process function returned null') 
            return
        print(title_translit)
        Wine.objects.filter(id=wine.wine_id).update(translit_title=title_translit)


    @asyncio.coroutine
    #Simplewine - html
    def parse_wine(self, wine, *args):
        title = wine.select_one('.item__context__description .code')
        if not title: return
        title = title.string.split(',')
        if len(title) > 1: return title[1]
        return title[0]
       


class Command(BaseCommand):
    def handle(self, *args, **options):
        fix_ssl_unverified_err()
        loop = asyncio.get_event_loop()
        crawler = WineCrawler()
        loop.run_until_complete(crawler.crawl())
