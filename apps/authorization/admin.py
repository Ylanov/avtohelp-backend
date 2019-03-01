from django.contrib import admin
from .models import SMSCode

# Register your models here.
admin.site.register(SMSCode)
# NOTE: самому удобно пользоваться такой админкой? а клиенту или другим членам команды?
# FIXIT: сделай хоть фильтры по статусу и определи list_display чтоли
