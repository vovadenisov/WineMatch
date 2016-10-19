# -*- coding: utf-8 -*-
__author__ = 'alla'
from django.core.management.base import BaseCommand
from survey.models import Wine, Country, Question, Answer
import csv
import tarantool

TARANTOOL_CONNCTION = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'port': 3311
}

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('command')

    def handle(self, *args, **options):
        if options['command'] == 'wine':
            self.download_all_wines()
        elif options['command'] == 'countries':
            self.download_all_countries()
        elif options['command'] == 'question':
            self.download_taste_questions()
        elif options['command'] == 'formal_question':
            self.create_formal_questions()
        elif options['command'] == 'all':
            self.create_all()
        else:
            print ("Command not found!")

    def create_all(self):
        self.download_all_countries()
        self.download_all_wines()
        self.download_taste_questions()
        self.create_formal_questions()

    def download_all_wines(self):
        print('download ...')
        tnt = tarantool.connect(**TARANTOOL_CONNCTION)
        offset = 0
        length = 100
        tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data
        while len(tuples) > 0 and tuples[0]:
            for t in tuples:
                create_one_wine(t)
            offset += length
            tuples = tnt.call('wine.find_by_chunk', [offset, length, False ]).data

    def download_all_countries(self):
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

    def download_taste_questions(self):
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
    w = Wine(title = wine[0], img = path, color =wine[2], type =wine[3], country = c, alcohol = wine[8], year = wine[10], stylistic = wine[11], description=wine[13], food = wine[14])
    try:
        w.save()
    except Exception as e:
        print(e)
