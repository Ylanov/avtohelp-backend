from rest_framework.permissions import BasePermission
from chat import models


class ChatMessagePermission(BasePermission):
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if not request.user.is_anonymous:
            room = view.kwargs.get("pk")
            qs = models.ChatRoom.objects.filter(id=room).by_participant(request.user)
            if qs.exists():
                return True
        return False
