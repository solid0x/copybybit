from django.db import models


class Position(models.Model):
    symbol = models.CharField(max_length=255)
    side = models.CharField(max_length=255)
    size = models.DecimalField(decimal_places=15, max_digits=30)
    leverage = models.DecimalField(decimal_places=2, max_digits=5)
