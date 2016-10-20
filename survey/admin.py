from django.contrib import admin

# Register your models here.
from survey.models import Country, Wine

admin.site.register(Country)
admin.site.register(Wine)
