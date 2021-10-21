# type: ignore

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import (
    BooleanField,
    Case,
    Q,
    QuerySet,
    When,
)

from .choices import (
    AVAILABLE,
    CANCELED,
    EXPIRED,
)


class AssistanceRequestQuerySet(QuerySet):
    def by_user(self, user):
        """Filter request by user"""
        return self.filter(user=user)

    def by_status(self, status):
        """Filter by status"""
        return self.filter(status=status)

    def available(self, user):
        """Filter by valid requests"""
        return self.ordinary(user=user).filter(status=AVAILABLE)

    def expired(self):
        """Filter by valid requests"""
        return self.filter(status=EXPIRED)

    def canceled(self):
        """Filter by valid requests"""
        return self.filter(status=CANCELED)

    def ordinary(self, user):
        """
        Queryset that EXCLUDE requests in which user is owner
        of blacklist or he sis a foe and excluded himself
        :param user:
        :type user: object
        :return: AssistanceRequestQuerySet
        """
        return self.exclude(
            Q(user__blacklist_owner__foe=user)
            | Q(user__blacked_user__owner=user)
        )

    def annotate_distance(
        self,
        raw_coordinates: list = None,
        latitude: float = None,
        longitude: float = None,
        point: Point = None,
    ):
        """
        Annotate service distance from position
        raw_coordinates can contain -
        - latitude (index 0),
        - longitude (index 1),

        point parameter is Point object
        """
        if raw_coordinates:
            x, y = (
                raw_coordinates.split(",")[0],
                raw_coordinates.split(",")[1],
            )
            return self.annotate(
                distance=Distance(
                    "location", Point(float(x), float(y), srid=4326)
                )
            )
        elif latitude and longitude:
            return self.annotate(
                distance=Distance(
                    "location",
                    Point(float(latitude), float(longitude), srid=4326),
                )
            )
        elif point:
            return self.annotate(
                distance=Distance("location", point, srid=4326)
            )
        else:
            return self

    def annotate_owner_status(self, user):

        return self.annotate(
            is_owner=Case(
                When(user=user, then=True),
                output_field=BooleanField(default=False),
                default=False,
            )
        )
