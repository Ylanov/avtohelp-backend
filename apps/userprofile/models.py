from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import Q, Subquery
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from easy_thumbnails.fields import ThumbnailerImageField

from utils import methods
from utils.mixins import BaseMixin


class ProfileQuerySet(models.QuerySet):
    """Custom QuerySet for model Profile"""

    def friendly(self, user):
        """
        Queryset that EXCLUDE profiles in which user is owner of blacklist or he is a foe and excluded himself
        :param user:
        :type user: object
        :return: ProfileQuerySet
        """
        return self.exclude(user_id__in=Subquery(BlackList.objects.common(user).values('foe_id'))).exclude(user=user)

    def friends(self, user):
        """
        Queryset that return only friends
        :param user:
        :return: QuerySet
        """
        return self.filter(user_id__in=Subquery(FriendList.objects.common(user).values('friend'))).exclude(user=user)

    def annotate_online_status(self):
        """
        Annotate online status
        :return: QuerySet object
        """
        return self.annotate(
            online=models.Case(
                models.When(user__onlineuseractivity__isnull=False, then=True),
                output_field=models.BooleanField(default=False),
                default=False
            )
        )


class Profile(BaseMixin):
    """Profile model"""

    user = models.OneToOneField('account.User', on_delete=models.PROTECT)
    first_name = models.CharField(max_length=255, null=True, blank=True,
                                  default=None, verbose_name=_('Name'))
    last_name = models.CharField(max_length=255, null=True, blank=True,
                                 default=None, verbose_name=_('Last name'))
    middle_name = models.CharField(max_length=255, null=True, blank=True,
                                   default=None, verbose_name=_('Middle name'))
    city = models.ForeignKey('catalog.City',
                             on_delete=models.CASCADE,
                             blank=True, null=True, default=None)

    objects = ProfileQuerySet.as_manager()

    class Meta:
        """Meta class."""

        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def get_car_info(self):
        """Get str representation of user car"""
        profile_car = self.user.profilecar_set.first()
        return f'{profile_car.car.mark} {profile_car.car.car_model} {profile_car.color}' if profile_car else None


class ProfileCarManager(models.Manager):
    """Custom Manager for ProfileCar"""
    pass


class ProfileCarQuerySet(models.QuerySet):
    """Custom Query for ProfileCar"""
    pass


class ProfileCar(BaseMixin):
    """User profile car"""

    owner = models.ForeignKey('account.User', on_delete=models.PROTECT)
    car = models.ForeignKey('car.Car', on_delete=models.PROTECT)
    color = models.ForeignKey('car.CarColor', on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=255, verbose_name=_('License plate'))

    class Meta:
        """Meta class"""

        verbose_name = _('Profile car')
        verbose_name_plural = _('Profile cars')


class ProfileLocation(BaseMixin):
    """Profile location"""

    user = models.OneToOneField('account.User', on_delete=models.PROTECT)
    location = gis_models.PointField(_('Location'),
                                     blank=True, null=True, default=None)

    class Meta:
        """Meta class."""

        verbose_name = _('Profile location')
        verbose_name_plural = _('Profile locations')


class ProfileGalleryQuerySet(models.QuerySet):
    """ProfileGallery queryset"""

    def by_user(self, user):
        """Show user profile gallery"""
        return self.filter(profile__user=user)

    def by_profile(self, profile):
        """Show user profile gallery"""
        return self.filter(profile=profile)

    def get_avatar(self, profile):
        """Show user profile avatar"""
        return self.filter(profile=profile, is_main=True)

    def by_status(self, switcher=False):
        """Filter ProfileGallery objects by flag is_main"""
        return self.filter(is_main=switcher)


class ProfileGalleryManager(models.Manager):
    """ProfileGallery manager"""

    def reset_status(self, profile):
        """Reset status is_main"""
        return ProfileGallery.objects.by_profile(profile=profile).by_status(switcher=True).update(is_main=False)


class ProfileGallery(BaseMixin):
    """Profile gallery"""
    THUMBNAIL_KEY = 'gallery'

    profile = models.ForeignKey(
        'Profile',
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE,
        related_name='gallery')
    image = ThumbnailerImageField(upload_to=methods.image_path,
                                  blank=True, null=True, default=None,
                                  verbose_name=_('Image'))
    is_main = models.BooleanField(default=False)

    objects = ProfileGalleryManager.from_queryset(ProfileGalleryQuerySet)()

    class Meta:
        """Meta class."""

        verbose_name = _('Gallery item')
        verbose_name_plural = _('Gallery items')

    def get_image(self, key=None):
        """Get thumbnailed image file."""
        return self.image[key or self.THUMBNAIL_KEY] if self.image else None

    def get_image_url(self, key=None):
        """Get image thumbnail url."""
        return self.get_image(key).url if self.image else None

    def image_tag(self):
        """Admin preview tag."""
        if self.image:
            return mark_safe('<img src="%s" />' % self.get_image_url())
        else:
            return None

    image_tag.short_description = _('Image')
    image_tag.allow_tags = True


class FriendRequestQuerySet(models.QuerySet):
    """Custom QuerySet for model FriendRequest"""

    def my_requests(self, owner):
        """My requests to add SOMEONE in my friend list"""
        return self.filter(owner=owner)

    def requests(self, invited):
        """Request to add ME in friend list"""
        return self.filter(invited=invited)

    def approved(self):
        """Approved requests"""
        return self.filter(approved=True)

    def not_approved(self):
        """Not approved requests"""
        return self.filter(approved=False)

    def waiting(self, user, invited):
        """Check whether there is a user request"""
        if self.filter(owner=user, invited=invited).exists():
            return True
        else:
            return False


class FriendRequestManager(models.Manager):
    """Custom Manager for FriendRequest model"""

    def make(self, owner, user):
        """Create friend request"""
        obj = self.model(owner=owner, invited=user)
        obj.save()
        return obj


class FriendRequest(BaseMixin):
    """Friend request model"""

    owner = models.ForeignKey('account.User',
                              verbose_name=_('Owner'),
                              on_delete=models.CASCADE)
    invited = models.ForeignKey('account.User',
                                verbose_name=_('Invited user'),
                                related_name='friendrequest_invited',
                                on_delete=models.CASCADE)
    approved = models.BooleanField(default=False, verbose_name=_('Status'))

    objects = FriendRequestManager.from_queryset(FriendRequestQuerySet)()

    class Meta:
        """Meta-class"""
        verbose_name = _('Friend request')
        verbose_name_plural = _('Friend request')

    def approve(self, owner, invited):
        """Approve friend request"""
        # update flag
        self.approved = True
        self.save()
        # create new record in FriendList
        FriendList.objects.create(owner=owner, friend=invited, request=self)
        return self


class FriendListQuerySet(models.QuerySet):
    """Custom QuerySet for model FriendList"""

    def my_list(self, user):
        """Get user friends"""
        return self.filter(owner=user, request__approved=True)

    def common(self, user):
        """Get user friends"""
        return self.filter(Q(owner=user) | Q(friend=user) & Q(request__approved=True))

    def in_list(self, user):
        """User in someones friendlist"""
        return self.filter(friend=user, request__approved=True)

    def are_friends(self, owner, user):
        """Check if user is already a friend"""
        if self.filter(Q(owner=owner, friend=user) | Q(owner=user, friend=owner) & Q(request__approved=True)).exists():
            return True
        else:
            return False


class FriendListManager(models.Manager):
    """Custom Manager for FriendList model"""
    pass


class FriendList(BaseMixin):
    """Friend-list model"""

    owner = models.ForeignKey('account.User',
                              verbose_name=_('Owner'),
                              related_name='friendlist_owner', on_delete=models.CASCADE,)
    friend = models.ForeignKey('account.User',
                               verbose_name=_('Friend'),
                               related_name='friendlist_user',
                               on_delete=models.CASCADE)
    request = models.ForeignKey('FriendRequest',
                                verbose_name=_('Request'),
                                related_name='friendlist_request',
                                on_delete=models.CASCADE)

    objects = FriendListManager.from_queryset(FriendListQuerySet)()

    class Meta:
        """Meta-class"""
        verbose_name = _('Friend list')
        verbose_name_plural = _('Friend lists')


class BlackListQuerySet(models.QuerySet):
    """Custom QuerySet for model BlackList"""

    def my_list(self, user):
        """Users in my blacklist"""
        return self.filter(owner=user)

    def in_list(self, user):
        """User in someones blacklist"""
        return self.filter(foe=user)

    def common(self, user):
        return self.filter(models.Q(owner=user) | models.Q(foe=user))

    def are_foes(self, owner, user):
        """Check if owner has an enemy"""
        if self.filter(Q(owner=owner, foe=user) |
                       Q(owner=user, foe=owner)).exists():
            return True
        else:
            return False


class BlackListManager(models.Manager):
    """Custom Manager for BlackList model"""
    pass


class BlackList(BaseMixin):
    """BlackList model"""

    owner = models.ForeignKey('account.User',
                              verbose_name=_('Owner'),
                              related_name='blacklist_owner', on_delete=models.CASCADE,)
    foe = models.ForeignKey('account.User',
                            verbose_name=_('Foe'),
                            related_name='blacked_user',
                            on_delete=models.CASCADE)

    objects = BlackListManager.from_queryset(BlackListQuerySet)()

    class Meta:
        """Meta-class"""
        verbose_name = _('Black list')
        verbose_name_plural = _('Black lists')
