from django.db import models
from django.db.models import Q, Subquery
from utils.mixins import BaseMixin
from asgiref.sync import async_to_sync
from userprofile import models as profile_models


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
            private = self.by_paticipants(initiator=initiator, participant=participant)
            if not private:
                obj = self.model(initiator, participant, is_public)
                obj.save()
            else:
                obj = private.first()
        return obj


class ChatRoomQuerySet(models.QuerySet):
    """QuerySet for model ChatRoom"""

    def friendly(self, participant):
        """Only friendly rooms"""
        return self.exclude(participant_id__in=Subquery(
            profile_models.BlackList.objects.common(participant).values('foe_id')))
    
    def friends(self, participant):
        """Filter by friend flag"""
        return self.filter(participant_id__in=Subquery(
            profile_models.FriendList.objects.common(participant).values('friend_id')))

    def by_paticipants(self, initiator, participant):
        """Find if room already exists"""
        return self.filter(Q(initiator=initiator, participant=participant) |
                           Q(initiator=participant, participant=initiator))

    def by_participant(self, participant):
        """Find room by participant"""
        return self.filter(Q(initiator=participant) |
                           Q(participant=participant)).friendly(participant)

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
