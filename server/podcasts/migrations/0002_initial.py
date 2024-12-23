# Generated by Django 5.1.1 on 2024-12-12 12:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("podcasts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="podcast",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="episode",
            name="podcast",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="podcasts.podcast"
            ),
        ),
    ]
