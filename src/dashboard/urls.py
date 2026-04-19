from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("logs/<str:service>/", views.logs, name="logs"),
    path("actions/seed-demo/", views.action_seed_demo, name="action-seed-demo"),
    path("actions/clear-cache/", views.action_clear_cache, name="action-clear-cache"),
    path("actions/test-push/", views.action_test_push, name="action-test-push"),
    path("actions/run-tests/", views.action_run_tests, name="action-run-tests"),
]
