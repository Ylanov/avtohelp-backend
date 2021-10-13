from django.contrib import admin

from .models import (
    Car,
    CarColor,
    CarMark,
    CarModel,
    CarService,
    CarServiceCategory,
)

common_list_display = ("id", "name", "created", "modified")


@admin.register(Car)
class CarModelAdmin(admin.ModelAdmin):
    """Custom admin page for Car"""

    list_display = ("id", "mark", "car_model", "created", "modified")


@admin.register(CarMark)
class CarMarkModelAdmin(admin.ModelAdmin):
    """Custom admin page for CarMark"""

    list_display = common_list_display


@admin.register(CarModel)
class CarModelModelAdmin(admin.ModelAdmin):
    """Custom admin page for CarModel"""

    list_display = common_list_display


@admin.register(CarColor)
class CarColorModelAdmin(admin.ModelAdmin):
    """Custom admin page for CarColor"""

    list_display = common_list_display


@admin.register(CarService)
class CarServiceModelAdmin(admin.ModelAdmin):
    """Custom admin page for Service"""

    list_display = ("id", "name", "created", "modified")


@admin.register(CarServiceCategory)
class ServiceCategoryModelAdmin(admin.ModelAdmin):
    """Custom admin page for ServiceCategory"""

    list_display = common_list_display
