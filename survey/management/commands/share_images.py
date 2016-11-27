# -*- coding: utf-8 -*-
import io
import math

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from survey.models import Wine  #code name photo search_url answer_type base_url
from application.settings import MEDIA_ROOT

CRAWLER_MAX_WORKERS = 10
SUCCESS_STATUS_CODES = [200, 202, ]
SIMULARITY_TRESHOLD = 0.5

class Command(BaseCommand):
    def _clean_title(self, title):
        title = title.replace('Вино', '')
        return title.strip()

    def _generate_image(self, wine_img, wine_title):
        result_pic = io.BytesIO()
        with Image(filename=wine_img).clone() as wine:
            height = wine.height
            width = wine.width
            wine.rotate(35)
            with Image(filename=MEDIA_ROOT + '/background.png').clone() as background:
                background.composite(wine, left=-int(width * math.cos(55.0 / 180 * math.pi)), top=int(0.5 * background.height - 3.0 * height / 8))
                with Drawing() as context:
                    context.font = MEDIA_ROOT + '/PTN77F.ttf'
                    context.font_size = 44
                    context.fonx_weight = 'bold'
                    context.fill_color = Color('#ffffff')
                    context.text(
                        x=41, y=52,
                        body='Я пью ' + wine_title
                    )
                    context(background)
                    background.save(file=result_pic)
                    return result_pic

    def _process_wine(self, wine):
        image2share = self._generate_image(
            wine.absolute_img_path,
            #wine.img.url.split('/')[-1],
            self._clean_title(wine.title)
        )
        filename = 'share_' + wine.img.url.split('/')[-1]
        print(filename)
        wine.image2share.save(filename, ContentFile(image2share.getvalue()), False)
        image2share.close()
         
    def handle(self, *args, **options):
        for wine in Wine.objects.all():
            if not wine.img: continue
            self._process_wine(wine)
            break
