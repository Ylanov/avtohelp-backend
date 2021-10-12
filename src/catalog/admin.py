from django.contrib import admin

from catalog.models import City

common_list_display = ("id", "name", "created", "modified")


class CityModelAdmin(admin.ModelAdmin):
    """Custom admin page for City"""

    list_display = common_list_display


# Register your models here.
admin.site.register(City, CityModelAdmin)
