from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    # Professional Department Mapping
    DEPARTMENTS = [
        ('ENG', 'Engineering & Dev'),
        ('OPS', 'Cloud Operations'),
        ('SLS', 'Sales & Growth'),
        ('MKT', 'Marketing'),
        ('ADM', 'Administration'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.CharField(
        max_length=3, 
        choices=DEPARTMENTS, 
        default='ENG',
        verbose_name="Organization Department"
    )
    monthly_budget = models.FloatField(
        default=500.0, 
        help_text="Target carbon limit in kg CO2e"
    )

    def __str__(self):
        return f"{self.user.username} | {self.get_department_display()}"

# AUTOMATION: Create a Profile whenever a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
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