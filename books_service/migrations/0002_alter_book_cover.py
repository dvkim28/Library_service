# Generated by Django 4.2.13 on 2024-07-02 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books_service", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="cover",
            field=models.CharField(
                choices=[("S", "Soft"), ("H", "Hard")], max_length=100
            ),
        ),
    ]
