# Generated by Django 5.1.1 on 2024-12-12 21:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interactions", "0004_view"),
        ("podcasts", "0009_alter_episode_podcast"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comment",
            name="episode",
        ),
        migrations.AddField(
            model_name="comment",
            name="podcast",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="podcasts.podcast",
            ),
        ),
    ]
