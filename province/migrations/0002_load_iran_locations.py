import json
from pathlib import Path

from django.db import migrations

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def load_locations(apps, schema_editor):
    Province = apps.get_model("province", "Province")
    City = apps.get_model("province", "City")
    if Province.objects.exists() or City.objects.exists():
        return  # داده‌ی موجود را دست نمی‌زنیم

    provinces = json.loads((FIXTURES / "province.json").read_text(encoding="utf-8"))
    Province.objects.bulk_create(
        Province(pk=p["pk"], **p["fields"]) for p in provinces
    )
    cities = json.loads((FIXTURES / "city.json").read_text(encoding="utf-8"))
    City.objects.bulk_create(City(pk=c["pk"], **c["fields"]) for c in cities)

    # sequence پستگرس بعد از درج با pk صریح باید هماهنگ شود
    if schema_editor.connection.vendor == "postgresql":
        with schema_editor.connection.cursor() as cursor:
            for model in (Province, City):
                table = model._meta.db_table
                cursor.execute(
                    "SELECT setval(pg_get_serial_sequence(%s, 'id'), "
                    f"COALESCE((SELECT MAX(id) FROM {table}), 1))",
                    [table],
                )


class Migration(migrations.Migration):
    dependencies = [("province", "0001_initial")]
    operations = [migrations.RunPython(load_locations, migrations.RunPython.noop)]
