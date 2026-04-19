"""
Seed the database with the minimum reference data an empty RoadHelp demo
needs to look believable: Russian cities, popular car brands/models, and
common colours.

Usage:
    docker compose exec api python src/manage.py seed_demo

Idempotent — running it twice is safe, each entity is get_or_create'd.
"""
from django.core.management.base import BaseCommand

from car.models import Car, CarColor, CarMark, CarModel
from catalog.models import City


CITIES = [
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Нижний Новгород",
    "Челябинск",
    "Самара",
    "Омск",
    "Ростов-на-Дону",
    "Уфа",
    "Краснодар",
    "Воронеж",
    "Пермь",
    "Волгоград",
]

# {mark: [models]}
BRANDS = {
    "Lada":        ["Granta", "Vesta", "Priora", "Niva", "XRAY"],
    "Toyota":      ["Camry", "Corolla", "RAV4", "Land Cruiser", "Prius"],
    "Kia":         ["Rio", "Sportage", "Ceed", "K5", "Sorento"],
    "Hyundai":     ["Solaris", "Tucson", "Creta", "Elantra", "Santa Fe"],
    "Volkswagen":  ["Polo", "Tiguan", "Passat", "Golf", "Touareg"],
    "BMW":         ["3 Series", "5 Series", "X3", "X5", "7 Series"],
    "Mercedes":    ["C-Class", "E-Class", "S-Class", "GLC", "GLE"],
    "Ford":        ["Focus", "Fiesta", "Kuga", "Mondeo", "EcoSport"],
    "Nissan":      ["Qashqai", "X-Trail", "Almera", "Terrano", "Juke"],
    "Skoda":       ["Octavia", "Rapid", "Kodiaq", "Karoq", "Superb"],
    "Renault":     ["Logan", "Duster", "Sandero", "Kaptur", "Arkana"],
    "Mazda":       ["CX-5", "3", "6", "CX-9", "MX-5"],
}

COLOURS = [
    ("Белый",     "#ffffff"),
    ("Чёрный",    "#000000"),
    ("Серый",     "#808080"),
    ("Серебристый", "#c0c0c0"),
    ("Красный",   "#e53935"),
    ("Синий",     "#1e88e5"),
    ("Голубой",   "#4fc3f7"),
    ("Зелёный",   "#43a047"),
    ("Жёлтый",    "#fdd835"),
    ("Оранжевый", "#fb8c00"),
    ("Коричневый", "#6d4c41"),
    ("Бежевый",   "#d7ccc8"),
    ("Золотой",   "#ffb300"),
    ("Бордовый",  "#880e4f"),
    ("Фиолетовый", "#8e24aa"),
]


class Command(BaseCommand):
    help = "Seed demo reference data (cities, car marks/models, colours)."

    def handle(self, *args, **opts):
        self._seed_cities()
        self._seed_colours()
        self._seed_brands_and_cars()
        self.stdout.write(self.style.SUCCESS("Seed complete."))

    def _seed_cities(self):
        created = 0
        for name in CITIES:
            _, was_new = City.objects.get_or_create(name=name)
            created += int(was_new)
        self.stdout.write(f"Cities: {created} new / {len(CITIES)} total")

    def _seed_colours(self):
        created = 0
        for name, hex_code in COLOURS:
            _, was_new = CarColor.objects.get_or_create(
                name=name, defaults={"hex_color": hex_code},
            )
            created += int(was_new)
        self.stdout.write(f"Colours: {created} new / {len(COLOURS)} total")

    def _seed_brands_and_cars(self):
        marks_created = 0
        models_created = 0
        cars_created = 0
        for mark_name, model_names in BRANDS.items():
            mark, mark_new = CarMark.objects.get_or_create(name=mark_name)
            marks_created += int(mark_new)
            for model_name in model_names:
                model, model_new = CarModel.objects.get_or_create(
                    name=model_name, mark=mark,
                )
                models_created += int(model_new)
                _, car_new = Car.objects.get_or_create(
                    mark=mark, car_model=model,
                )
                cars_created += int(car_new)
        total_models = sum(len(v) for v in BRANDS.values())
        self.stdout.write(
            f"Brands: {marks_created} new / {len(BRANDS)} total; "
            f"Models: {models_created} new / {total_models} total; "
            f"Cars: {cars_created} new"
        )
