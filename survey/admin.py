from django.contrib import admin

# Register your models here.
from survey.models import Country, Wine, WineShop, WineToShop, Question

class BrokenWinesFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'сломанные цены'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'brokenwines'

    def lookups(self, request, model_admin):
        return (
            ('less_200', 'меньше 200 рублей'),
        )

    def queryset(self, request, queryset):
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'less_200':
            return queryset.filter(price__lte=200)

class Wine2ShopAdmin(admin.ModelAdmin):
    list_filter = (BrokenWinesFilter,)
    search_fields = ["wine__title"]
    list_display = ["wine", "price", "shop"]

admin.site.register(Country)
admin.site.register(Wine)
admin.site.register(Question)
admin.site.register(WineShop)
admin.site.register(WineToShop, Wine2ShopAdmin)
