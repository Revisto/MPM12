# Generated by Django 5.1.1 on 2024-12-12 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("podcasts", "0007_alter_podcast_author"),
    ]

    operations = [
        migrations.AddField(
            model_name="episode",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="episode_images/"),
        ),
    ]