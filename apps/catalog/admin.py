from django.contrib import admin
from catalog.models import (City, Car, CarMark,
                            CarModel, CarColor,
                            ServiceCategory, Service)

# Register your models here.
admin.site.register(City)
admin.site.register(Car)
admin.site.register(CarMark)
admin.site.register(CarModel)
admin.site.register(CarColor)
admin.site.register(ServiceCategory)
admin.site.register(Service)
