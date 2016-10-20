# -*- coding: utf-8 -*-
__author__ = 'alla'
import csv
import tarantool
import requests
import tempfile

from django.core.management.base import BaseCommand
from django.core import files
from django.conf import settings

from survey.models import Wine, Country, Question, Answer

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
        else:
            print ("Command not found!")

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
    w = Wine.objects.get(title=wine[0])
    try:
        food = wine[21]
    except Exception:
        food = None
    try:
        price = wine[22]
    except Exception:
        price = None
    w.food = food
    w.price = price
    w.save()
    print(w.title)
