from django.urls import path
from order.views import current as views


app_name = 'order'

urlpatterns = [
    path('', views.AssistanceRequestListView.as_view(), name='request-list'),
    # path('create', views.AssistanceRequestCreate.as_view(), name='request-create')
]