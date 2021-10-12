from rest_framework import generics, status
from rest_framework.response import Response

from ..models import FCMDevice
from ..serializers import current as serializers


class FCMDeviceViewSet(generics.GenericAPIView):
    """FCMDevice registration view.

    * Pair of fields **registration_id** and **type** should be unique.
    * In case of requested device existance, existing device will be returned
      instead of creating new one.
    """

    serializer_class = serializers.FCMDeviceSerializer
    lookup_fields = (
        "registration_id",
        "type",
    )

    queryset = FCMDevice.objects.all()

    def post(self, request, *args, **kwargs):
        """Override post method."""
        FCMDevice.objects.filter(user_id=self.request.user.id).delete()

        instance = self.get_object_or_none()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK if instance else status.HTTP_201_CREATED,
        )

    def get_object_or_none(self):
        """Object as result and the view is displaying or None."""
        queryset = self.get_queryset()  # get the base queryset
        queryset = self.filter_queryset(queryset)  # apply any filter backends
        # generate filter
        filter_params = {
            f: self.request.data.get(f)
            for f in self.lookup_fields
            if self.request.data.get(f)
        }

        # get object and check permissions or return None
        obj = queryset.filter(**filter_params).first()
        obj and self.check_object_permissions(self.request, obj)
        return obj
