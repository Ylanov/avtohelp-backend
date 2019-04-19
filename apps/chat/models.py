from django.db import models
from django.db.models import Subquery
from django.utils.translation import ugettext_lazy as _

from userprofile import models as profile_models
from utils.mixins import BaseMixin, ImageMixin

from utils import tasks

from django.conf import settings

NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS = True

MSG_TYPE_MESSAGE = 0  # For standard messages
MSG_TYPE_WARNING = 1  # For yellow messages
MSG_TYPE_ALERT = 2  # For red & dangerous alerts
MSG_TYPE_MUTED = 3  # For just OK information that doesn't bother users
MSG_TYPE_ENTER = 4  # For just OK information that doesn't bother users
MSG_TYPE_LEAVE = 5  # For just OK information that doesn't bother users

MESSAGE_TYPES_CHOICES = (
    (MSG_TYPE_MESSAGE, 'MESSAGE'),
    (MSG_TYPE_WARNING, 'WARNING'),
    (MSG_TYPE_ALERT, 'ALERT'),
    (MSG_TYPE_MUTED, 'MUTED'),
    (MSG_TYPE_ENTER, 'ENTER'),
    (MSG_TYPE_LEAVE, 'LEAVE'),
)

MESSAGE_TYPES_LIST = [
    MSG_TYPE_MESSAGE,
    MSG_TYPE_WARNING,
    MSG_TYPE_ALERT,
    MSG_TYPE_MUTED,
    MSG_TYPE_ENTER,
    MSG_TYPE_LEAVE,
]


class ChatMessageQuerySet(models.QuerySet):
    """Custom queryset for model ChatMessage"""

    def by_room(self, room_id):
        """Filter by room"""
        return self.filter(room=room_id)

    def annotate_read_status(self, user):
        return self.annotate(
            read=models.Case(
                models.When(
                    id__in=Subquery(ChatReadMessage.objects.filter(user=user).values('message_id')),
                    then=True),
                output_field=models.BooleanField(default=False),
                default=False
            )
        )


class ChatMessageManager(models.Manager):
    """Custom manager for model ChatMessage"""

    def make(self, sender, room_id, message):
        """Create chat message"""
        obj = self.model(sender=sender, room_id=room_id, message=message)
        obj.save()
        # obj.send_push_notifications()
        return obj


class ChatMessage(BaseMixin):
    """Chat messages"""
    sender = models.ForeignKey('account.User',
                               on_delete=models.CASCADE)
    room = models.ForeignKey('ChatRoom',
                             on_delete=models.CASCADE)
    message = models.TextField()

    objects = ChatMessageManager.from_queryset(ChatMessageQuerySet)()

    class Meta:
        """Meta class"""
        ordering = ('created',)

    def send_push_notifications(self):
        """Sent push notification to all users in chat room exclude sender"""
        if settings.USE_CELERY:
            tasks.notify_chat_participants.delay(
                sender_id=self.sender.id,
                participants=self.room.participants.all().exclude(id=self.sender.id).values('id'))
        else:
            tasks.notify_chat_participants(
                sender_id=self.sender_id,
                participants=self.room.participants.all().exclude(id=self.sender.id).values('id'))


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


class ChatRoom(BaseMixin, ImageMixin):
    """Chat room"""
    name = models.CharField(max_length=24,
                            blank=True, default=None, null=True)
    participants = models.ManyToManyField('account.User',
                                          related_name='participants')
    is_public = models.BooleanField(default=False)

    objects = ChatRoomManager.from_queryset(ChatRoomQuerySet)()

    @property
    def group_name(self):
        """
        Returns the Channels Group name that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return "room-%s" % self.id


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


class ChatReadMessageQuerySet(models.QuerySet):
    """QuerySets for model ChatReadMessage"""
    pass


class ChatReadMessageManager(models.Manager):
    """Manager for model ChatReadMessage"""

    def read(self, user, message):
        """Create a new object"""
        obj = self.model(user=user, message=message)
        obj.save()
        return obj


class ChatReadMessage(BaseMixin):
    """Model for fixation read/unread messages in room"""
    user = models.ForeignKey('account.User',
                             on_delete=models.CASCADE)
    message = models.ForeignKey('ChatMessage',
                                on_delete=models.CASCADE)

    objects = ChatReadMessageManager.from_queryset(ChatReadMessageQuerySet)()

    class Meta:
        """Meta class"""
        ordering = ('created',)
