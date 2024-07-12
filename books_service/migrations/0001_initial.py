# Generated by Django 4.2.13 on 2024-07-02 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
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
                ("title", models.CharField(max_length=100)),
                ("author", models.CharField(max_length=100)),
                (
                    "cover",
                    models.CharField(
                        choices=[("H", "Hard"), ("S", "Soft")], max_length=100
                    ),
                ),
                ("inventory", models.PositiveIntegerField()),
            ],
        ),
    ]
