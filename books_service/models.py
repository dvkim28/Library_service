import decimal

from django.db import models

COVER_CHOICE = {
    ("H", "Hard"),
    ("S", "Soft"),
}

class Book(models.Model):

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.CharField(
        max_length=100,
        choices=COVER_CHOICE,
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    def __str__(self):
        return self.title
