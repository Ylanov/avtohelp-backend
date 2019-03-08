from django.db import models
from utils.mixins import BaseMixin


class Message(BaseMixin):
    sender = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='receiver')
    message = models.CharField(max_length=1200)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.message
