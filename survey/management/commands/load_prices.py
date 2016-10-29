# -*- coding: utf-8 -*-
import asyncio
from asyncio import JoinableQueue as Queue
from difflib import SequenceMatcher

from bs4 import BeautifulSoup as bs
import requests
from django.core.management.base import BaseCommand

from survey.models import Wine, WineShop #code name photo search_url answer_type
from survey.models import WineToShop #wine, shop, price

CRAWLER_MAX_WORKERS = 10
SUCCESS_STATUS_CODES = [200, 202, ]
SIMULARITY_TRESHOLD = 0.8


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

    def _extract_wine_info(self, content):  # raises ValueError on broken description
        def _extract_td_by_number(tr, td_number):
            try:
                return tr.find_all('td')[td_number].text.strip()
            except (AttributeError, IndexError):
                return None

        # def _extract_2nd_td(tr):
        #    try:
        #        return tr.find_all('td')[1].text.strip()
        #    except (AttributeError, IndexError):
        #        raise ValueError

        # def _extract_2nd_td_conditionally(expected_name, tr):
        #    try:
        #        if tr.find_all('td')[0].text.strip() != expected_name:
        #            print(tr.find_all('td')[0].text)
        #            print(expected_name)
        #            raise ValueError
        #        return tr.find_all('td')[1].text
        #    except (AttributeError, IndexError):
        #        raise ValueError

        def _get_by_index(list_, index):
            try:
                return list_[index]
            except IndexError:
                return None

        def _tds2hash(td_raws):
            res = {}
            for row in td_raws:
                key = _extract_td_by_number(row, 0)
                value = _extract_td_by_number(row, 1)
                if not key or not value: continue
                res[key] = value
            return res

        soup = bs(content, 'html.parser')
        name = soup.select_one('h1.title').text.strip(' \t\n\r'),  # name
        wine = self.wines.get(name[0])
        if not wine:
            print(name)
            return

        wine.price = soup.select_one('.item-buy__prize').attrs.get('data-price')

        # features -- extended description
        extra_info_bag_of_words = _tds2hash(
            soup.select_one('#characteristics .tabs-content__table.padding').find_all('tr')
        )
        wine.food = extra_info_bag_of_words.get('Гастрономия:').strip(' \t\n\r')  # gastronomy
        if not wine or not wine.food: print(wine.name)
        return wine

    def _save_wine2tnt(self, wine):
        wine.replace()

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
        return {price: int(price)}

    @asyncio.coroutine
    def parse_av(self, wine, *args):
        raise NotImplemented

    @asyncio.coroutine
    def parse_red_white(self, wine, *args):
        raise NotImplemented

    @asyncio.coroutine
    def parse_av(self, wine, *args):
        raise NotImplemented

    @asyncio.coroutine
    def parse_amwine(self, wine, *args):
        raise NotImplemented


    @asyncio.coroutine
    def parse_wineshopper(self, wine, *args):
        raise NotImplemented

    @asyncio.coroutine
    def parse_simplewine(self, wine, *args):
        raise NotImplemented


class Command(BaseCommand):
    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        crawler = WineCrawler()
        loop.run_until_complete(crawler.crawl())