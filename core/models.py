from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. PROFILE MODEL: Handles user metadata and enterprise departments
class Profile(models.Model):
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

# 2. CATEGORY MODEL: Stores the conversion factors (e.g., 0.15 kg per hour)
class Category(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, default='units') # e.g., 'km' or 'hours'
    co2_per_unit = models.FloatField(
        default=0.0, 
        help_text="kg of CO2 emitted per 1 unit"
    )
    icon_code = models.CharField(max_length=50, default='bolt')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} ({self.unit})"

# 3. CARBON ENTRY: The logic happens in the save() method automatically
class CarbonEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    value = models.FloatField(verbose_name="Quantity Used") # Users enter '5' here
    co2_total = models.FloatField(editable=False) # Code calculates the result here
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # AUTOMATION: Multiply the quantity by the category's emission factor
        # Example: 2 hours * 0.15 factor = 0.30 kg CO2
        self.co2_total = float(self.value) * float(self.category.co2_per_unit)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.category.name} ({self.co2_total}kg)"

# --- AUTOMATION SIGNALS: Prevents 'User has no profile' errors ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()