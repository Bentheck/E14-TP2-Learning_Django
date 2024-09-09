import random
from decimal import Decimal
from django.db import models

class Zone(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    money = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)

    def __str__(self):
        return f"Player with money: {self.money}"

class Drug(models.Model):
    name = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def get_price_for_zone(self, zone, price_type):
        try:
            price_entry = DrugPrice.objects.get(drug=self, zone=zone, price_type=price_type)
            return price_entry.price
        except DrugPrice.DoesNotExist:
            # Retourner base_price par défaut si aucun prix spécifique n'est défini
            return self.base_price

class DrugPrice(models.Model):
    PRICE_TYPES = (
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    )

    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    price_type = models.CharField(max_length=4, choices=PRICE_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('drug', 'zone', 'price_type')

class DrugAvailability(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField()

    class Meta:
        unique_together = ('drug', 'zone')

    def __str__(self):
        return f"{self.drug.name} in {self.zone.name}"

