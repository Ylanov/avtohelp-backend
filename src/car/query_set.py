from django.contrib.gis.db.models.functions import Distance
from django.db import models


class CarServiceQuerySet(models.QuerySet):
    """QuerySet for model CarService"""

    def annotate_distance(self, position):
        """Annotate service distance from position"""
        return self.annotate(distance=Distance("location", position))

    def annotate_icon_exists(self):
        """Annotate flag that return True if service category icon is exists"""
        return self.annotate(
            icon_exists=models.Case(
                models.When(category__image__isnull=False, then=True),
                output_field=models.BooleanField(default=False),
                default=False,
            )
        )
