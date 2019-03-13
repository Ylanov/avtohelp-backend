from django.db import models
from utils.mixins import BaseMixin
from asgiref.sync import async_to_sync


class ChatMessage(BaseMixin):
    """Chat messages"""
    sender = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='receiver')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    room = models.ForeignKey('ChatRoom', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.message


class ChatRoom(BaseMixin):
    """Chat room"""
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
