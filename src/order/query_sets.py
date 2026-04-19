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


def _coerce_lat_lng(lat, lng):
    """Return a validated Point for the project's PointField values.

    NOTE: this codebase has stored points as Point(lat, lng) everywhere
    (serializers, fixtures, migrations, tests). Technically PostGIS expects
    Point(x=lng, y=lat) in srid=4326 — so the stored coordinates are
    mirrored globally, but self-consistent: every query references the
    same convention, so nearest-neighbour results remain correct for
    regional data. We preserve that convention here rather than flipping
    it in one place and silently breaking every distance calculation.
    TODO(post-demo): fix the convention across the whole project, add a
    data migration that swaps existing Point coordinates.
    """
    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except (TypeError, ValueError):
        return None
    if not (-90.0 <= lat_f <= 90.0) or not (-180.0 <= lng_f <= 180.0):
        return None
    return Point(lat_f, lng_f, srid=4326)


def _parse_lat_lng(raw: str):
    """Parse 'lat,lng' query-string form into a Point, or return None."""
    if not raw or "," not in raw:
        return None
    parts = raw.split(",", 1)
    if len(parts) != 2:
        return None
    return _coerce_lat_lng(parts[0].strip(), parts[1].strip())


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
        raw_coordinates: str = None,
        latitude: float = None,
        longitude: float = None,
        point: Point = None,
    ):
        """Annotate distance from a reference point.

        Accepts either:
          - raw_coordinates: "lat,lng" string (from the ?coordinates= query param)
          - latitude + longitude
          - a Point

        Validates ranges (lat ∈ [-90, 90], lng ∈ [-180, 180]). On any parse
        error returns the queryset unmodified — calling code must be prepared
        for no `distance` annotation rather than a 500.
        """
        reference = None
        if raw_coordinates:
            reference = _parse_lat_lng(raw_coordinates)
        elif latitude is not None and longitude is not None:
            reference = _coerce_lat_lng(latitude, longitude)
        elif point is not None:
            reference = point

        if reference is None:
            return self

        return self.annotate(distance=Distance("location", reference))

    def annotate_owner_status(self, user):

        return self.annotate(
            is_owner=Case(
                When(user=user, then=True),
                output_field=BooleanField(default=False),
                default=False,
            )
        )
