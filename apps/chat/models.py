from django.db import models
from utils.mixins import BaseMixin
from asgiref.sync import async_to_sync


class ChatMessage(BaseMixin):
    """Chat messages"""
    sender = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='recipient')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    room = models.ForeignKey('ChatRoom', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.message


class ChatRoomManager(models.Manager):
    """Manager for model ChatRoom"""

    def get_or_create(self, initiator=None, participant=None, is_public=False):
        """
        Get or Create ChatRoom object for open private chat
        :param initiator:
        :param is_public:
        :param participant:
        :type initiator: Obj or Integer
        :type is_public: Boolean
        :type participant: Obj or Integer
        :return: Obj
        """
        # If initiator and participant are set, then check existence of group chat
        public = self.public()
        if public.exists() and not (initiator and participant):
            obj = public.first()
        else:
            # Check if private room exists
            private = self.room(initiator=initiator, participant=participant)
            if not private:
                obj = self.model(initiator, participant, is_public)
                obj.save()
            else:
                obj = private.first()
        return obj


class ChatRoomQuerySet(models.QuerySet):
    """QuerySet for model ChatRoom"""

    def room(self, initiator, participant):
        """Find if room already exists"""
        return self.filter(models.Q(initiator=initiator, participant=participant) |
                           models.Q(initiator=participant, participant=initiator))

    def public(self):
        """Find if room already exists"""
        return self.filter(is_public=True)


class ChatRoom(BaseMixin):
    """Chat room"""
    initiator = models.ForeignKey('account.User',
                                  on_delete=models.CASCADE,
                                  related_name='initiator',
                                  blank=True, null=True)
    participant = models.ForeignKey('account.User',
                                    on_delete=models.CASCADE,
                                    related_name='participant',
                                    blank=True, null=True)
    is_public = models.BooleanField(default=True)

    objects = ChatRoomQuerySet.as_manager()

    def __str__(self):
        return f'{self.id}'
