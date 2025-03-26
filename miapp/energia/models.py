from django.db import models

class RegistroEnergia(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)

    voltaje_fase_1 = models.FloatField(null=True, blank=True)
    voltaje_fase_2 = models.FloatField(null=True, blank=True)
    voltaje_fase_3 = models.FloatField(null=True, blank=True)

    corriente_fase_1 = models.FloatField(null=True, blank=True)
    corriente_fase_2 = models.FloatField(null=True, blank=True)
    corriente_fase_3 = models.FloatField(null=True, blank=True)

    potencia_activa = models.FloatField(null=True, blank=True)
    potencia_reactiva = models.FloatField(null=True, blank=True)
    potencia_aparente = models.FloatField(null=True, blank=True)

    energia_activa = models.FloatField(null=True, blank=True)
    energia_reactiva = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Registro {self.timestamp}"
