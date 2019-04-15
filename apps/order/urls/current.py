from django.urls import path

from order.views import current as views

app_name = 'order'

urlpatterns = [
    path('requests/', views.AssistanceRequestListView.as_view(), name='request-list'),
    path('requests/count', views.AssistanceRequestCountView.as_view(), name='requests-count'),
    path('requests/create', views.AssistanceRequestCreateView.as_view(), name='request-create'),
    path('requests/<int:pk>', views.AssistanceRequestDetailView.as_view(), name='request-detail'),
    # path('requests/<int:pk>/update', views.AssistanceRequestUpdateView.as_view(), name='request-update'),
    # path('requests/<int:pk>/delete', views.AssistanceRequestDestroyView.as_view(), name='request-delete')
]