# Generated by Django 5.1.1 on 2024-12-12 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("podcasts", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name="podcast",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="podcast_images/"),
        ),
        migrations.AddField(
            model_name="podcast",
            name="categories",
            field=models.ManyToManyField(
                related_name="podcasts", to="podcasts.category"
            ),
        ),
    ]