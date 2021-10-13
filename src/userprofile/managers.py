from django.db import models

from .query_set import (
    FCMDeviceQuerySet,
    ProfileGalleryQuerySet,
)


class FCMDeviceManager(models.Manager):
    def get_queryset(self):
        return FCMDeviceQuerySet(self.model)


class ProfileGalleryManager(models.Manager):
    """ProfileGallery manager"""

    def reset_status(self, profile):
        """Reset status is_main"""
        return (
            ProfileGalleryQuerySet()
            .by_profile(profile=profile)
            .by_status(switcher=True)
        )


class FriendRequestManager(models.Manager):
    """Custom Manager for FriendRequest model"""

    def make(self, owner, user):
        """Create friend request"""
        obj = self.model(owner=owner, invited=user)
        obj.save()
        obj.send_push_notification()
        return obj


class BlackListManager(models.Manager):
    """Custom Manager for BlackList model"""

    pass
