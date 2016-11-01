# -*- coding: utf-8 -*-

import re
import asyncio
try:
    from asyncio import Queue
except ImportError:
    from asyncio import JoinableQueue as Queue

from difflib import SequenceMatcher
from bs4 import BeautifulSoup as bs
import requests
from django.core.management.base import BaseCommand

from survey.models import Wine, WineShop #code name photo search_url answer_type base_url
from survey.models import WineToShop #wine, shop, price, url

CRAWLER_MAX_WORKERS = 10
SUCCESS_STATUS_CODES = [200, 202, ]
SIMULARITY_TRESHOLD = 0.8

def get_int_from_price_str(s):
    return int(re.search(r'\d+', s).group())

class WineCrawler:
    def __init__(self):
        self.wine_queue = Queue()
        wines = Wine.objects.all()
        self.wines = {w.title: w for w in wines}
        shops = WineShop.objects.all()
        self.shops = {s.code: s for s in shops}

    @asyncio.coroutine
    def crawl(self):
        workers = [asyncio.Task(self.download_wine())
                   for _ in range(CRAWLER_MAX_WORKERS)]
        for wine in self.wines.keys():
            for shop in self.shops.keys():
                yield from self.wine_queue.put((shop, wine))
        yield from self.wine_queue.join()
        for w in workers:
            w.cancel()

    @asyncio.coroutine
    def download_wine(self):
        while True:
            data = yield from self.wine_queue.get()
            try:
                #process_function = getattr(self, 'parse_{}'.format(data[0]))
                yield from self.process_wine(**data)#process_function(data[1])
            except AttributeError:
                pass
            finally:
                self.wine_queue.task_done()

    @asyncio.coroutine
    def process_wine(self, shop, wine):
        shop = self.shops.get(shop)
        wine = self.wines.get(wine)
        url = shop.form_query(wine.title)
        r = requests.get(url)
        if r.status_code not in SUCCESS_STATUS_CODES:
            return
        if shop.answer_type == 'html':
            wine_data = bs(r.text, 'html.parser')
        elif shop.answer_type == 'json':
            wine_data = r.json()
        process_function = getattr(self, 'parse_{}'.format(wine.title))
        wine2shop = process_function(wine_data, wine.title)
        if not wine2shop: return
        wine2shop.update({'shop': shop, 'wine': wine})
        WineToShop.objects.create_or_update(**wine2shop)

    def _count_words_simularity(name, expected_name):
        return SequenceMatcher(None, name, expected_name).ratio()

    @asyncio.coroutine
    #WineStyle -- json
    def parse_winestyle(self, wine, expected_name):
        info = wine.get('AnalyticsImpression')
        if not info: return
        wine_tag = bs(info, 'html.parser').select_one('.analytics-data')
        if not wine_tag: return
        name = wine_tag.attrs.get('data-name')
        price = wine_tag.attrs.get('data-price')
        if not name or not price: return
        if self._count_words_simularity(name, expected_name) < SIMULARITY_TRESHOLD:
            return

        products = wine.get('products')
        products_tag = bs(products, 'html.parser').select_one('.analytics-data')
        link = products_tag.select_one('form a')
        if not link: return
        link_url =  link.attrs.get('href')
        return {'price': int(price), 'url': link_url}

    @asyncio.coroutine
    #Азбука Вкуса -- json
    def parse_av(self, wine, expected_name):
        wines_list = wine.get('list')
        if not wines_list: return
        wine_info = wines_list[0]
        if not wine_info or not wine_info.get('price') or not wine_info.get('name'): return
        if self._count_words_simularity(wine_info.get('name'), expected_name) < SIMULARITY_TRESHOLD:
            return
        return {'price': wine_info.get('price'), 'url': wine_info.get('link')}

    @asyncio.coroutine
    #Ароматный мир -- html
    def parse_amwine(self, wine, expected_name):
        wine_info = wine.select_one('#products_list')
        if not wine_info: return
        wine_items = wine_info.select('.poduct_light')
        if not wine_items: return
        price = wine_items[0].select_one('.price span').string
        name = wine_items[0].select_one('.title a p')
        name = self._to_latin(name)
        if self._count_words_simularity(name, expected_name) < SIMULARITY_TRESHOLD:
            return
        price = get_int_from_price_str(price)
        url = wine_items[0].select_one('.title a')
        if not url: return
        url_link = url.attrs.get('href')
        return {'price': price, 'url': url_link}

    @asyncio.coroutine
    #WineSHopper - HTML
    def parse_wineshopper(self, wine, *args):
        wine_items = wine.select('.product-block')
        if not wine_items: return
        price = wine_items[0].select_one('.clearfix .price').string
        #name = wine_items[0].select_one('.title a p')

        #if self._count_words_simularity(name, expected_name) < SIMULARITY_TRESHOLD:
        #    return
        price = get_int_from_price_str(price)
        url = wine_items[0].select_one('.name a')
        if not url: return
        url_link = url.attr.get('href')
        return {'price': price, 'url': url_link}

    @asyncio.coroutine
    #Simplewine - html
    def parse_simplewine(self, wine, *args):
        wine_items = wine.select('.category__item_new__inner')
        if not wine_items: return
        price = wine_items[0].select_one('.price .bold').string
        price.replace(' ', '')
        #name = wine_items[0].select_one('.title a p')

        #if self._count_words_simularity(name, expected_name) < SIMULARITY_TRESHOLD:
        #    return
        price = get_int_from_price_str(price)
        url = wine_items[0].select_one('.category__item_new__pic a')
        if not url: return
        url_link = url.attr.get('href')
        return {'price': price, 'url': url_link}


class Command(BaseCommand):
    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        crawler = WineCrawler()
        loop.run_until_complete(crawler.crawl())