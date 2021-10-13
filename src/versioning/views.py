from rest_framework import generics

from . import (
    models,
    serializers,
)


class VersionView(generics.RetrieveAPIView):
    lookup_field = "version"
    lookup_url_kwarg = "version_code"
    serializer_class = serializers.VersionSerializer
    versioning_class = None

    def get_queryset(self):
        return models.Version.objects.all()
