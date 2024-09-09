from django.contrib import admin
from .models import Drug, Zone, DrugAvailability

@admin.action(description='Update drug prices for all zones')
def update_drug_prices(modeladmin, request, queryset):
    populate_drug_prices()

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    actions = [update_drug_prices]

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(DrugAvailability)
class DrugAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('drug', 'zone', 'stock')
    search_fields = ('drug__name', 'zone__name')
