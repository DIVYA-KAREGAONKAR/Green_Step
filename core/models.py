from django.db import models
from django.contrib.auth.models import User
class Category(models.Model):
    name = models.CharField(max_length=100) # e.g., "Bike", "Car", "AC"
    unit = models.CharField(max_length=20) # e.g., "km", "kWh"
    co2_per_unit = models.FloatField(default=0.0) # The calculation factor
    icon_code = models.CharField(max_length=50, default='bolt')

    def __str__(self):
        return self.name
class CarbonEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    value = models.FloatField()
    co2_total = models.FloatField(editable=False) # Auto-calculated
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # FIX: Ensure we use 'co2_per_unit' here to match the Category model
        self.co2_total = self.value * self.category.co2_per_unit
        super().save(*args, **kwargs)