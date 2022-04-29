from django.db import models

class Backtest(models.Model):
    symbol = models.CharField(max_length=255)
    strategy = models.CharField(max_length=255)
    bin_size = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    result = models.FloatField(null=True)
