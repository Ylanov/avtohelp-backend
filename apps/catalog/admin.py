from django.contrib import admin

from catalog.models import (City, CarMark,
                            CarModel, CarColor,
                            ServiceCategory)

common_list_display = ('id', 'name', 'created', 'modified')


class CityModelAdmin(admin.ModelAdmin):
    """Custom admin page for City"""
    list_display = common_list_display


class CarMarkModelAdmin(admin.ModelAdmin):
    """Custom admin page for CarMark"""
    list_display = common_list_display


class CarModelModelAdmin(admin.ModelAdmin):
    """Custom admin page for CarModel"""
    list_display = common_list_display


class CarColorModelAdmin(admin.ModelAdmin):
    """Custom admin page for CarColor"""
    list_display = common_list_display


class ServiceCategoryModelAdmin(admin.ModelAdmin):
    """Custom admin page for ServiceCategory"""
    list_display = common_list_display


# Register your models here.
admin.site.register(City, CityModelAdmin)
admin.site.register(CarMark, CarMarkModelAdmin)
admin.site.register(CarModel, CarModelModelAdmin)
admin.site.register(CarColor, CarColorModelAdmin)
admin.site.register(ServiceCategory, ServiceCategoryModelAdmin)
