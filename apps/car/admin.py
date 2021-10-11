from django.contrib import admin
from car.models import Car, CarMark, CarModel, CarColor, CarService, CarServiceCategory


common_list_display = ("id", "name", "created", "modified")


class CarModelAdmin(admin.ModelAdmin):
    """Custom admin page for Car"""

    list_display = ("id", "mark", "car_model", "created", "modified")


class CarMarkModelAdmin(admin.ModelAdmin):
    """Custom admin page for CarMark"""

    list_display = common_list_display


class CarModelModelAdmin(admin.ModelAdmin):
    """Custom admin page for CarModel"""

    list_display = common_list_display


class CarColorModelAdmin(admin.ModelAdmin):
    """Custom admin page for CarColor"""

    list_display = common_list_display


class CarServiceModelAdmin(admin.ModelAdmin):
    """Custom admin page for Service"""

    list_display = ("id", "name", "created", "modified")


class ServiceCategoryModelAdmin(admin.ModelAdmin):
    """Custom admin page for ServiceCategory"""

    list_display = common_list_display


# Register your models here.
admin.site.register(Car, CarModelAdmin)
admin.site.register(CarMark, CarMarkModelAdmin)
admin.site.register(CarModel, CarModelModelAdmin)
admin.site.register(CarColor, CarColorModelAdmin)
admin.site.register(CarService, CarServiceModelAdmin)
admin.site.register(CarServiceCategory, ServiceCategoryModelAdmin)
