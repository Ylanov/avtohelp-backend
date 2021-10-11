from django.shortcuts import render
from rest_framework import views
from rest_framework.permissions import AllowAny


class IndexView(views.APIView):
    """Main page view"""

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return render(request, template_name="index/index.html")
