from django.db import models
from django.db.models import Subquery
from django.utils.translation import ugettext_lazy as _

from userprofile import models as profile_models
from utils.mixins import BaseMixin


class ChatMessageQuerySet(models.QuerySet):
    """Custom queryset for model ChatMessage"""

    def by_room(self, room_id):
        """Filter by room"""
        return self.filter(room=room_id)


class ChatMessage(BaseMixin):
    """Chat messages"""
    sender = models.ForeignKey('account.User',
                               on_delete=models.CASCADE)
    room = models.ForeignKey('ChatRoom',
                             on_delete=models.CASCADE)
    message = models.TextField()

    objects = ChatMessageQuerySet.as_manager()

    class Meta:
        ordering = ('created',)


class ChatRoomManager(models.Manager):
    """Manager for model ChatRoom"""

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

    def private(self, initiator, participant):
        """Filter by two participants for find private room"""
        return self.filter(is_public=False).filter(participants=initiator).filter(participants=participant)

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
