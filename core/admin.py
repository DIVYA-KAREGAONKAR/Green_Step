from django.contrib import admin
from .models import Category, CarbonEntry

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # This makes the admin look like a spreadsheet for easy reading
    list_display = ('name', 'unit', 'co2_per_unit', 'icon_code')
    search_fields = ('name',)

@admin.register(CarbonEntry)
class CarbonEntryAdmin(admin.ModelAdmin):
    # This helps you track which user is emitting the most
    list_display = ('user', 'category', 'value', 'co2_total', 'created_at')
    list_filter = ('category', 'created_at', 'user')
    readonly_fields = ('co2_total',) # Since it's auto-calculated, we make it read-only