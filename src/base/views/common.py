from django.shortcuts import render
from rest_framework import views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from car import models as car_models
from catalog import models as catalog_models


class IndexView(views.APIView):
    """Main page view"""

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return render(request, template_name="index/index.html")


class GeneralInfoView(views.APIView):
    """Bootstrap endpoint used by the Android client on first launch.

    Aggregates three reference lists in a single response:
      * cities       — [{id, name}]
      * car_colors   — [{id, name}]
      * car_makes    — [{id, name, car_models: [{id, mark, model}]}]

    Kept in `base` because it spans multiple apps. Response shape is frozen
    by docs/API_CONTRACT.md — do not change field names or nesting.
    """

    def get(self, request, *args, **kwargs):
        cities = list(
            catalog_models.City.objects.order_by("name").values("id", "name")
        )
        car_colors = list(
            car_models.CarColor.objects.order_by("name").values("id", "name")
        )

        marks = list(car_models.CarMark.objects.order_by("name"))
        # prefetch all Cars in one query grouped by mark_id
        cars_by_mark: dict[int, list[dict]] = {}
        for car in car_models.Car.objects.select_related(
            "mark", "car_model"
        ).order_by("mark__name", "car_model__name"):
            cars_by_mark.setdefault(car.mark_id, []).append(
                {
                    "id": car.id,
                    "mark": {"id": car.mark.id, "name": car.mark.name},
                    "model": {
                        "id": car.car_model.id,
                        "name": car.car_model.name,
                    },
                }
            )
        car_makes = [
            {
                "id": mark.id,
                "name": mark.name,
                "car_models": cars_by_mark.get(mark.id, []),
            }
            for mark in marks
        ]

        return Response(
            {
                "cities": cities,
                "car_colors": car_colors,
                "car_makes": car_makes,
            }
        )
