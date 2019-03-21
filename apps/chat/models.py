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
    sender = models.ForeignKey('account.User',
                               on_delete=models.CASCADE)
    room = models.ForeignKey('ChatRoom',
                             on_delete=models.CASCADE)
    message = models.TextField()

    objects = ChatMessageManager.from_queryset(ChatMessageQuerySet)()

    class Meta:
        ordering = ('created',)


class ChatRoomManager(models.Manager):
    """Manager for model ChatRoom"""

    def get_or_create(self, initiator, participant, public):
        """
        Get or Create ChatRoom object for open private chat
        :param initiator:
        :param public:
        :param participant:
        :type initiator: Obj or Integer
        :type public: Boolean
        :type participant: Obj or Integer
        :return: Obj
        """
        # Check if room exists
        room_qs = self.by_participants(initiator=initiator, participant=participant, public=public)
        if not room_qs:
            obj = self.make(participants=[initiator, participant], public=public)
            obj.save()
        else:
            obj = room_qs.first()
        return obj

    def make(self, public: bool, participants):
        """Make ChatRoom object"""
        obj = self.model(is_public=public)
        obj.save()
        for participant in participants:
            obj.participants.add(participant)
        return obj


class ChatRoomQuerySet(models.QuerySet):
    """QuerySet for model ChatRoom"""

    def friendly(self, participant):
        """Only friendly rooms"""
        return self.exclude(participants__id__in=Subquery(
            profile_models.BlackList.objects.common(participant).values('foe_id')))

    def friends(self, participant):
        """Filter by friend flag"""
        return self.filter(participants_id__in=Subquery(
            profile_models.FriendList.objects.common(participant).values('friend_id')))

    def by_participants(self, initiator, participant, public: bool):
        """Find if room already exists"""
        return self.filter(participants=initiator, is_public=public).filter(participants=participant, is_public=public)

    def by_participant(self, participant):
        """Find room by participant"""
        return self.filter(participants=participant).friendly(participant)

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

    objects = ChatRoomManager.from_queryset(ChatRoomQuerySet)()


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
