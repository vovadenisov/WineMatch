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

def get_int_from_price_str(s):
    return int(re.search(r'\d+', s).group())

def fix_ssl_unverified_err():
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
        ssl._create_default_https_context = _create_unverified_https_context
    except AttributeError:
        pass

def translit(string):
    capital_letters = {
        u'А': u'A',
        u'Б': u'B',
        u'В': u'V',
        u'Г': u'G',
        u'Д': u'D',
        u'Е': u'E',
        u'Ё': u'E',
        u'Ж': u'Zh',
        u'З': u'Z',
        u'И': u'I',
        u'Й': u'Y',
        u'К': u'K',
        u'Л': u'L',
        u'М': u'M',
        u'Н': u'N',
        u'О': u'O',
        u'П': u'P',
        u'Р': u'R',
        u'С': u'S',
        u'Т': u'T',
        u'У': u'U',
        u'Ф': u'F',
        u'Х': u'H',
        u'Ц': u'Ts',
        u'Ч': u'Ch',
        u'Ш': u'Sh',
        u'Щ': u'Sch',
        u'Ъ': u'',
        u'Ы': u'Y',
        u'Ь': u'',
        u'Э': u'E',
        u'Ю': u'Yu',
        u'Я': u'Ya'
    }

    lower_case_letters = {
        ' ': '_',
        u'а': u'a',
        u'б': u'b',
        u'в': u'v',
        u'г': u'g',
        u'д': u'd',
        u'е': u'e',
        u'ё': u'e',
        u'ж': u'zh',
        u'з': u'z',
        u'и': u'i',
        u'й': u'y',
        u'к': u'k',
        u'л': u'l',
        u'м': u'm',
        u'н': u'n',
        u'о': u'o',
        u'п': u'p',
        u'р': u'r',
        u'с': u's',
        u'т': u't',
        u'у': u'u',
        u'ф': u'f',
        u'х': u'h',
        u'ц': u'ts',
        u'ч': u'ch',
        u'ш': u'sh',
        u'щ': u'sch',
        u'ъ': u'',
        u'ы': u'y',
        u'ь': u'',
        u'э': u'e',
        u'ю': u'yu',
        u'я': u'ya'
    }

    translit_string = ""

    for index, char in enumerate(string):
        if char in lower_case_letters.keys():
            char = lower_case_letters[char]
        elif char in capital_letters.keys():
            char = capital_letters[char]
            if len(string) > index+1:
                if string[index+1] not in lower_case_letters.keys():
                    char = char.upper()
            else:
                char = char.upper()
        else:
            try:
                char = str(char)
            except UnicodeEncodeError:
                char = '_'
        translit_string += char

    return translit_string

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
            yield from self.process_wine(*data)#process_function(data[1])
            self.wine_queue.task_done()

    def _rm_non_informative_words(self, title):
        for word in ['Вино', 'г.', ',']:
            title = title.replace(word, '')
        title = title.lower()
        return title.strip()

    @asyncio.coroutine
    def process_wine(self, shop, wine):
        print(shop)
        print(wine)
        shop = self.shops.get(shop)
        wine = self.wines.get(wine)
        url = shop.form_query(self._rm_non_informative_words(wine.title))
        print(url)
        r = requests.get(url, verify=False, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
        if r.status_code not in SUCCESS_STATUS_CODES:
            print('wrong status code'.format(r.status_code))
            return
        if shop.answer_type == 'html':
            wine_data = bs(r.text, 'html.parser')
        elif shop.answer_type == 'json':
            try:
                wine_data = r.json()
            except ValueError:
               print(shop.code)
               print(url)
        process_function = getattr(self, 'parse_{}'.format(shop.code))
        wine2shop = yield from process_function(wine_data, wine.title)
        if not wine2shop:
            print('process function returned null') 
            return
        print(wine2shop)
        wine2shop.update({'shop': shop, 'wine': wine})
        print(WineToShop.objects.create_or_update(**wine2shop))

    def _count_words_simularity(self, name, expected_name):
        return SequenceMatcher(None, name.lower(), expected_name.lower()).ratio()

    @asyncio.coroutine
    #WineStyle -- json
    def parse_winestyle(self, wine, expected_name):
        info = wine.get('AnalyticsImpression')
        if not info:
            print('winestyle: no analytics impession')
            return
        wine_tag = bs(info, 'html.parser').select_one('.analytics-data')
        if not wine_tag: 
            print('winestyle: no wine tag')
            return
        name = wine_tag.attrs.get('data-name')
        price = wine_tag.attrs.get('data-price')
        if not name or not price: 
            print('winestyle: not enoigh data')
            return
        if self._count_words_simularity(name, expected_name) < SIMULARITY_TRESHOLD:
            print('winestyle: not enough simularity')
            return

        products = wine.get('products')
        products_tag = bs(products, 'html.parser')#.select_one('.analytics-data')
        link = products_tag.select_one('form a')
        if not link:
            print(products_tag)
            print('winestyle: no link')
            return
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
        name = wine_items[0].select_one('.title a p').string
        name = re.sub(r'\s+', '', price)
        name = translit(name)
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
        price = wine_items[0].select_one('.price')
        if not price: 
            print('wineshopper: invalid price')
            print(wine_items)
            return 
        price = price.string
        #name = wine_items[0].select_one('.title a p')

        #if self._count_words_simularity(name, expected_name) < SIMULARITY_TRESHOLD:
        #    return
        price = get_int_from_price_str(price)
        url = wine_items[0].select_one('.name a')
        if not url: return
        url_link = url.attrs.get('href')
        return {'price': price, 'url': url_link}

    @asyncio.coroutine
    #Simplewine - html
    def parse_simplewine(self, wine, *args):
        wine_items = wine.select('.category__item_new__inner')
        if not wine_items: return
        price = wine_items[0].select_one('.price .bold').string
        price = re.sub(r'\s+', '', price)
        #name = wine_items[0].select_one('.title a p')

        #if self._count_words_simularity(name, expected_name) < SIMULARITY_TRESHOLD:
        #    return
        price = get_int_from_price_str(price)
        url = wine_items[0].select_one('.category__item_new__pic a')
        if not url: return
        url_link = url.attrs.get('href')
        return {'price': price, 'url': url_link}


class Command(BaseCommand):
    def handle(self, *args, **options):
        fix_ssl_unverified_err()
        loop = asyncio.get_event_loop()
        crawler = WineCrawler()
        loop.run_until_complete(crawler.crawl())
