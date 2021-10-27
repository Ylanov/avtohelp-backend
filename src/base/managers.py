# type: ignore

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

from account.models import User

#   Logging error messages
logger = logging.getLogger("app")


class PushNotificationManager(models.Manager):
    """PushNotification manager"""

    def make_friend_request_notification(
        self, user: (str, int, object)
    ) -> object:
        """Make common notification for friend request"""
        user_id = user.id if isinstance(user, User) else user
        if User.objects.filter(id=user_id).exists():
            obj = self.model(
                user_id=user_id,
                title=_("New friend request"),
                description=_("A new friend request has been received"),
                event=self.model.FRIEND_REQUEST,
            )
            obj.save()
            return obj

    def make_assistance_request_notification(
        self, user: (str, int, object)
    ) -> object:
        """Make common notification for assistance request"""
        user_id = user.id if isinstance(user, User) else user
        if User.objects.filter(id=user_id).exists():
            obj = self.model(
                user_id=user_id,
                title=_("New assistance request"),
                description=_("New assistance request was published"),
                event=self.model.CREATE_REQUEST,
            )
            obj.save()
            return obj

    def make_new_message_notification(
        self, user: (str, int, object), sender: (str, int, object)
    ) -> object:
        """Make common notification for new chat message"""
        if not isinstance(user, User):
            user_qs = User.objects.filter(id=user)
            if user_qs.exists():
                user = user_qs.first()
            else:
                return None

        if not isinstance(sender, User):
            sender_qs = User.objects.filter(id=sender)
            if sender_qs.exists():
                sender = sender_qs.first()
            else:
                return None

        obj = self.model(
            user=user,
            title=_("New message from chat"),
            description=_("User %s wrote a message") % sender.get_full_name,
            event=self.model.NEW_MESSAGE,
        )
        obj.save()
        return obj

    def make_new_newsletter_notification(
        self, user: (str, int, object), newsletter: (str, int, object)
    ) -> object:
        """Make common notification for new newsletter"""
        user_id = user.id if isinstance(user, User) else user
        from .models import Newsletter

        if newsletter:
            newsletter_qs = Newsletter.objects.filter(id=newsletter)
            if newsletter_qs.exists():
                newsletter = newsletter_qs.first()
            else:
                return None

        if User.objects.filter(id=user_id).exists():
            obj = self.model(
                user_id=user_id,
                title=_("News"),
                description=newsletter.text[:240] + "...",
                event=self.model.NEW_NEWSLETTER,
            )
            obj.save()
            return obj

    def make_newsletter_like_notification(
        self, user: (str, int, object), initiator: (str, int, object)
    ) -> object:
        """Make common notification for newsletter like"""
        user_id = user.id if isinstance(user, User) else user

        if not isinstance(initiator, User):
            initiator_qs = User.objects.filter(id=initiator)
            if initiator_qs.exists():
                initiator = initiator_qs.first()
            else:
                return None

        if User.objects.filter(id=user_id).exists():
            obj = self.model(
                user_id=user_id,
                title=_("Like"),
                description=_("User %s liked your newsletter")
                % initiator.get_full_name,
                event=self.model.NEW_NEWSLETTER_LIKE,
            )
            obj.save()
            return obj

    def make_newsletter_comment_notification(
        self, user: (str, int, object), initiator: (str, int, object)
    ) -> object:
        """Make common notification for newsletter comment"""
        user_id = user.id if isinstance(user, User) else user

        if not isinstance(initiator, User):
            initiator_qs = User.objects.filter(id=initiator)
            if initiator_qs.exists():
                initiator = initiator_qs.first()
            else:
                return None

        if User.objects.filter(id=user_id).exists():
            obj = self.model(
                user_id=user_id,
                title=_("New comment"),
                description=_("User %s comment your newsletter")
                % initiator.get_full_name,
                event=self.model.NEW_NEWSLETTER_COMMENT,
            )
            obj.save()
            return obj
