from django.db import models
from django.db.models import Q, Subquery
from channels.db import database_sync_to_async
from userprofile import models as profile_models
from utils.mixins import BaseMixin
from django.utils.translation import ugettext_lazy as _


class ChatMessageManager(models.Manager):
    """Custom manager for model ChatMessage"""

    @database_sync_to_async
    def make(self):
        """Bulk create chat messages"""
        pass


class ChatMessageQuerySet(models.QuerySet):
    """Custom queryset for model ChatMessage"""
    pass


class ChatMessage(BaseMixin):
    """Chat messages"""
    room = models.ForeignKey('ChatRoom', on_delete=models.CASCADE)

    objects = ChatMessageManager.from_queryset(ChatMessageQuerySet)()

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
    name = models.CharField(max_length=24,
                            blank=True, default=None, null=True)
    participants = models.ManyToManyField('account.User',
                                          related_name='participants')
    is_public = models.BooleanField(default=False)

    objects = ChatRoomQuerySet.as_manager()

    def __str__(self):
        return f'{self.id}'


class ChatRole(BaseMixin):
    """Chat user role"""

    MODERATOR = 0
    PARTICIPANT = 1

    ROLE_CHOICES = (
        (MODERATOR, _('Moderator')),
        (PARTICIPANT, _('Participant'))
    )

    user = models.ForeignKey('account.User',
                             related_name='user_role',
                             on_delete=models.CASCADE)
    room = models.ForeignKey('ChatRoom',
                             related_name='room_role',
                             on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, verbose_name=_('Role'),
                                            default=PARTICIPANT, blank=True, null=True)
