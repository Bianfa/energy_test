from django.utils import timezone

from django.db import models

class RegistroEnergia(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    voltaje_fase_1 = models.FloatField()
    voltaje_fase_2 = models.FloatField()
    voltaje_fase_3 = models.FloatField()
    corriente_fase_1 = models.FloatField()
    corriente_fase_2 = models.FloatField()
    corriente_fase_3 = models.FloatField()

    def __str__(self):
        return f"Registro {self.timestamp}"