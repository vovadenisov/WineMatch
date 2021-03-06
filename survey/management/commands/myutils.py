# -*- coding: utf-8 -*-
__author__ = 'alla'
import csv
import tarantool
import requests
import tempfile

from django.core.management.base import BaseCommand
from django.core import files
from django.conf import settings

from survey.models import Wine, Country, Question, Answer, Favorites, Sort, SortToWine
from feedback.models import Feedback

TARANTOOL_CONNCTION = {
    'user': settings.TARANTOOL_USER,
    'password': settings.TARANTOOL_PASSWORD,
    'host': settings.TARANTOOL_URL,
    'port': settings.TARANTOOL_PORT
}

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('command')

    def handle(self, *args, **options):
        if options['command'] == 'wine':
            self.create_all_wines()
        elif options['command'] == 'countries':
            self.create_all_countries()
        elif options['command'] == 'question':
            self.create_taste_questions()
        elif options['command'] == 'formal_question':
            self.create_formal_questions()
        elif options['command'] == 'reset_taste_questions':
            self.reset_taste_questions()
        elif options['command'] == 'all':
            self.create_all()
        elif options['command'] == 'update_wine':
            self.update_wines()
        elif options['command'] == 'delete_all':
            self.delete_all()
        elif options['command'] == 'remove_duplicates':
            self.remove_duplicates()
        elif options['command'] == 'price':
            self.price()
        elif options['command'] == 'add_wine_sort':
            self.add_wine_sort()
        elif options['command'] == 'add_region':
            self.add_region()
        else:
            print ("Command not found!")

    def price(self):
        wines = Wine.objects.all()
        for w in wines:
            shops =[s.price for s in w.get_shops()]
            if len(shops) != 0:
                average_price = round(sum(shops)/len(shops), 1)
                print(average_price)
                print('p', w.price)

    def remove_duplicates(self):
        wines = Wine.objects.all()
        for w in wines:
            shops = [s for s in w.get_shops()]
            res_shops = []
            for s in shops:
                if len(res_shops) != 0:
                    if s.shop.name in [i.shop.name for i in res_shops]:
                        print('delete', w.title, s.shop.name)
                        s.delete()
                    else:
                        res_shops.append(s)
                else:
                    res_shops.append(s)

    def delete_all(self):
        favorites = Favorites.objects.all()
        for f in favorites:
            f.delete()
        feedback = Feedback.objects.all()
        for f in feedback:
            f.delete()
        wines = Wine.objects.all()
        for w in wines:
            w.delete()

    def update_wines(self):
        print('update_wine')
        tnt = tarantool.connect(**TARANTOOL_CONNCTION)
        offset = 0
        length = 100
        tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data
        while len(tuples) > 0 and tuples[0]:
            for t in tuples:
                update_wine(t)
            offset += length
            tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data


    def create_all(self):
        print('create_all')
        self.create_all_countries()
        self.create_all_wines()
        self.create_taste_questions()
        self.create_formal_questions()


    def add_region(self):
        tnt = tarantool.connect(**TARANTOOL_CONNCTION)
        offset = 0
        length = 100
        tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data
        while len(tuples) > 0 and tuples[0]:
            for t in tuples:
                print(t[6])
                try:
                    w = Wine.objects.get(title=t[0])
                    w.region=t[6]
                    w.save()
                except:
                    pass
            offset += length
            tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data


    def add_wine_sort(self):
        self.create_all_sort()
        tnt = tarantool.connect(**TARANTOOL_CONNCTION)
        offset = 0
        length = 100
        tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data
        varieties = []
        while len(tuples) > 0 and tuples[0]:
            for t in tuples:
                list = t[4]
                try:
                    w = Wine.objects.get(title=t[0])
                    for v in list:
                        #if v not in varieties:
                        s = Sort.objects.get(name=v)
                        sort_to_winw = SortToWine(wine=w, sort=s)
                        sort_to_winw.save()
                except:
                    pass
            offset += length
            tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data

    def create_all_sort(self):
        tnt = tarantool.connect(**TARANTOOL_CONNCTION)
        offset = 0
        length = 100
        tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data
        varieties = []
        while len(tuples) > 0 and tuples[0]:
            for t in tuples:
                #print(t[4])
                list = t[4]
                for v in list:
                    if v not in varieties:
                        varieties.append(v)
            offset += length
            tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data
        for v in varieties:
            s = Sort(name=v)
            try:
                s.save()
            except Exception as e:
                pass


    def create_all_wines(self):
        print('create_all_wines')
        print('download wine...')
        tnt = tarantool.connect(**TARANTOOL_CONNCTION)
        offset = 0
        length = 100
        tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data
        while len(tuples) > 0 and tuples[0]:
            for t in tuples:
                create_one_wine(t)
            offset += length
            tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data

    def create_all_countries(self):
        print('create_all_countries')
        tnt = tarantool.connect(**TARANTOOL_CONNCTION)
        offset = 0
        length = 100
        tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data
        while len(tuples) > 0 and tuples[0]:
            for t in tuples:
                insert_contry(t[5])
            offset += length
            tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data

    def create_formal_questions(self):
        questions = {
            'color': ['Красное, белое или розовое?', {'1': 'белое', '2': 'красное', '3': 'розовое', '4': 'все равно'}],
            'sweetness': ['Что насчет сладости?', {'1': 'сухое', '2': 'сладкое', '3': 'полусладкое', '4': 'полусухое', '5': 'все равно'}],
            'aging': ['Любишь выдерженное вино?', {'1': 'да', '2': 'нет', '3': 'все равно'}]
            }
        for q in questions.keys():
            question = Question(question_text=questions[q][0], node=q)
            try:
                question.save()
                answers = questions[q][1]
                for answer in answers.keys():
                    a = Answer(answer_text = answers[answer], question = question, api_response = answer)
                    try:
                        a.save()
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

    def create_taste_questions(self):
        print('create_taste_questions')
        file_name = 'static/csv/questions.csv'
        with open(file_name) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                q = Question(question_text=row[2], node=row[0])
                try:
                    q.save()
                    answers = {'Да': 1, 'Нет': 2}
                    for answer in answers.keys():
                        a = Answer(answer_text = answer, question = q, api_response = answers[answer])
                        try:
                            a.save()
                        except Exception as e:
                            print(e)
                except Exception as e:
                    print(e)

    def _load_file(self, image_url):
        user_agent = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'}
        request = requests.get(image_url, headers=user_agent, stream=True)

        if request.status_code != requests.codes.ok:
            print(request.status_code)
            return None

        file_name = image_url.split('/')[-1]

        lf = tempfile.NamedTemporaryFile()

        for block in request.iter_content(1024 * 8):
            if not block:
                break
            lf.write(block)
        
        return (file_name, files.File(lf))
        
    def reset_taste_questions(self):
        file_name = 'static/csv/questions_new.csv'
        with open(file_name) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 6: continue
                node = row[0]
                question_text = row[4]
                image = row[5]
                
                try:
                    question = Question.objects.get(node = node)
                except Question.DoesNotExist:
                    continue
                    
                print(question.id)
                if question_text:
                    question.question_text = question_text
                    
                if image:
                    img = self._load_file(image)
                    #print(img)
                    if not img: print('invalid url {}\n'.format(image))
                    question.img.save(*img)
                    print(question.img.path)
                question.save()
    

def insert_contry(name):
    print(name)
    c = Country(name = name)
    try:
        c.save()
    except Exception:
        pass

def create_one_wine(wine):
    c = Country.objects.get(name=wine[5])
    path = wine[15]
    try:
        food = wine[21]
    except Exception:
        food = None
    try:
        price = wine[22]
    except Exception:
        price = None
    w = Wine(title = wine[0], img = path, color =wine[2], type =wine[3], country = c, alcohol = wine[8], year = wine[10], stylistic = wine[11], description=wine[13], food = food, price = price)
    try:
        w.save()
    except Exception as e:
        print(e)

def update_wine(wine):
    print(wine)
#    print (Wine.objects.get(pk=2).title)
#    w = Wine.objects.get(title=wine[0])
#    try:
#        food = wine[21]
#    except Exception:
#        food = None
#    try:
#        price = wine[22]
#    except Exception:
#        price = None
#    w.food = food
#    w.price = price
#    w.save()
#    print(w.title)
