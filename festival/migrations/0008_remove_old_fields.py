# Manual migration to clean up old fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("festival", "0007_populate_category_data"),
    ]

    operations = [
        # Remove old CharField fields
        migrations.RemoveField(
            model_name="festivalregistration",
            name="festival_format_old",
        ),
        migrations.RemoveField(
            model_name="festivalregistration",
            name="festival_topic_old",
        ),
        migrations.RemoveField(
            model_name="festivalregistration",
            name="special_section_old",
        ),
        # Make festival_format and festival_topic required (non-nullable)
        migrations.AlterField(
            model_name="festivalregistration",
            name="festival_format",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registrations",
                to="festival.festivalformat",
                verbose_name="قالب جشنواره",
            ),
        ),
        migrations.AlterField(
            model_name="festivalregistration",
            name="festival_topic",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registrations",
                to="festival.festivaltopic",
                verbose_name="محور جشنواره",
            ),
        ),
        # special_section remains nullable
    ]
