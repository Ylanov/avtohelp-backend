from django.contrib.gis.db.models.functions import Distance
from django.contrib.postgres.search import SearchVector
from django.db import models
from django.utils import timezone
from fcm_django import models as fcm_models

from base.models import PushNotificationConfiguration


class FCMDeviceQuerySet(fcm_models.FCMDeviceQuerySet):
    """Firebase Cloud Messaging queryset"""

    def by_geo_position(self, point):
        """Filter by geo position"""

        configuration = PushNotificationConfiguration.get_solo()
        return self.filter(
            user__profilelocation__location__distance_lte=(
                point,
                Distance(m=configuration.radius),
            )
        )

    def annotate_device_geo_position_relevance(self):
        """Is the device geo-position information current?"""

        delta = (timezone.now() - timezone.timedelta(hours=99, minutes=0),)

        return self.annotate(
            geo_position_is_valid=models.Case(
                models.When(
                    user__profilelocation__modified__gte=delta,
                    then=True,
                ),
                output_field=models.BooleanField(default=False),
                default=False,
            )
        )

    def annotate_device_distance_from_assistance_request(
        self, assistance_request
    ):
        """
        Annotate distance between user device location and assistance request
        """
        return self.annotate(
            distance=Distance(
                "user__profilelocation__location",
                assistance_request.location,
            )
        )


class ProfileQuerySet(models.QuerySet):
    """Custom QuerySet for model Profile"""

    def friendly(self, user):
        """
        Queryset that EXCLUDE profiles in which user is owner of blacklist
        or he is a foe and excluded himself
        :param user:
        :type user: object
        :return: ProfileQuerySet
        """
        return (
            self.exclude(user__blacked_user__owner=user)
            .exclude(user__blacklist_owner__foe=user)
            .exclude(user=user)
        )

    def valid(self):
        """Queryset that exclude profiles with null first name and last name"""
        return self.exclude(first_name__isnull=True, last_name__isnull=True)

    def friends(self, user):
        """
        Queryset that return only friends
        :param user:
        :return: QuerySet
        """
        return self.filter(
            # Check if USER is an initiator of friend request (is OWNER)
            models.Q(user__friendlist_user__owner=user)
            |
            # Check if USER is an invited person
            models.Q(user__friendlist_owner__friend=user)
        ).exclude(user=user)

    def annotate_online_status(self):
        """
        Annotate online status
        :return: annotate field online status
        """
        return self.annotate(
            online=models.Case(
                models.When(
                    models.Q(user__onlineuseractivity__user__isnull=False),
                    then=True,
                ),
                default=False,
                output_field=models.BooleanField(default=False),
            )
        )

    def annotate_friend_status(self, user):
        """
        Annotate friend status
        :return: annotated field
        """
        from userprofile.models import FriendList

        return self.annotate(
            friend=models.Case(
                models.When(
                    models.Q(
                        user_id__in=models.Subquery(
                            FriendList.objects.common(user).values(
                                "friend__id"
                            )
                        )
                    )
                    | models.Q(
                        user_id__in=models.Subquery(
                            FriendList.objects.common(user).values("owner__id")
                        )
                    ),
                    then=True,
                ),
                output_field=models.BooleanField(default=False),
                default=False,
            )
        )

    def annotate_foe_status(self, user):
        """
        Annotate foe status
        :return: annotated field
        """
        from .models import BlackList

        return self.annotate(
            foe=models.Case(
                models.When(
                    models.Q(
                        user_id__in=models.Subquery(
                            BlackList.objects.common(user).values("foe__id")
                        )
                    )
                    | models.Q(
                        user_id__in=models.Subquery(
                            BlackList.objects.common(user).values("owner__id")
                        )
                    ),
                    then=True,
                ),
                output_field=models.BooleanField(default=False),
                default=False,
            )
        )

    def annotate_friend_request_status(self, user):
        """
        Annotate annotate friend request status
        :return: annotated field
        """
        return self.annotate(
            friend_request=models.Case(
                models.When(
                    # Check if USER sent friend request
                    models.Q(user__friendrequest_invited__owner=user),
                    then=True,
                ),
                default=False,
                output_field=models.BooleanField(default=False),
            )
        )

    def annotate_full_text_search(self):
        """Full-text search"""
        return self.annotate(
            search=SearchVector(
                "first_name",
                "last_name",
                "user__profilecar__license_plate",
                config="simple",
            )
        )


class ProfileGalleryQuerySet(models.QuerySet):
    """ProfileGallery queryset"""

    def by_user(self, user):
        """Show user profile gallery"""
        return self.filter(profile__user=user)

    def by_profile(self, profile):
        """Show user profile gallery"""
        return self.filter(profile=profile)


class FriendRequestQuerySet(models.QuerySet):
    """
    Custom QuerySet for model FriendRequest
    """

    def from_me(self, owner):
        """My requests to add SOMEONE in my friend list"""
        return self.filter(owner=owner)

    def to_me(self, invited):
        """Request to add ME in friend list"""
        return self.filter(invited=invited)

    def common(self, owner, invited):
        """Common request"""
        return self.filter(
            models.Q(owner=owner, invited=invited)
            | models.Q(owner=invited, invited=owner) & models.Q(approved=False)
        )

    def from_me_to_user(self, owner, invited):
        """Return queryset with existed friend request"""
        return self.filter(owner=owner, invited=invited, approved=False)

    def common_by_user(self, user):
        """My requests to add SOMEONE in my friend list"""
        return self.filter(
            models.Q(owner=user)
            | models.Q(invited=user) & models.Q(approved=False)
        )

    def approved(self):
        """Approved requests"""
        return self.filter(approved=True)

    def not_approved(self):
        """Not approved requests"""
        return self.filter(approved=False)

    def waiting(self, user, invited):
        """Check whether there is a user request"""
        if self.filter(owner=user, invited=invited, approved=False).exists():
            return True
        else:
            return False


class FriendListQuerySet(models.QuerySet):
    """Custom QuerySet for model FriendList"""

    def my_list(self, user):
        """Get user friends"""
        return self.filter(owner=user)

    def common(self, user):
        """Get user friends"""
        return self.filter(
            models.Q(owner=user) | models.Q(friend=user)
        ).filter(friend__profile__last_name__isnull=False)

    def by_profiles(self, owner, friend):
        """Get user friend by profiles"""
        return self.filter(
            models.Q(owner__profile=owner) & models.Q(friend__profile=friend)
            | models.Q(owner__profile=friend) & models.Q(friend__profile=owner)
        )

    def by_users(self, owner, friend):
        """Get user friend" by users"""
        return self.filter(
            models.Q(owner=owner) & models.Q(friend=friend)
            | models.Q(owner=friend) & models.Q(friend=owner)
        )

    def in_list(self, user):
        """User in someones friendlist"""
        return self.filter(friend=user)

    def are_friends(self, owner, user):
        """Check if user is already a friend"""
        if self.filter(
            models.Q(owner=owner, friend=user)
            | models.Q(owner=user, friend=owner)
        ).exists():
            return True
        else:
            return False


class BlackListQuerySet(models.QuerySet):
    """Custom QuerySet for model BlackList"""

    def my_list(self, user):
        """Users in my blacklist"""
        return self.filter(owner=user)

    def in_list(self, user):
        """User in someones blacklist"""
        return self.filter(foe=user)

    def in_my_list(self, owner, foe):
        """User in my blacklist"""
        return self.filter(owner__profile=owner, foe__profile=foe)

    def by_profiles(self, owner, foe):
        """User in my blacklist"""
        return self.filter(owner__profile=owner, foe__profile=foe)

    def common(self, user):
        return self.filter(models.Q(owner=user) | models.Q(foe=user))

    def are_foes(self, owner, user):
        """Check if owner has an enemy"""
        if self.filter(
            models.Q(owner=owner, foe=user) | models.Q(owner=user, foe=owner)
        ).exists():
            return True
        else:
            return False


class ProfileLocationQuerySet(models.QuerySet):
    def nearby(self):
        pass
