from django.contrib import admin

from .models import BabyDate, Feeding, BreastBumping, BodyTemperature, GrowthData


admin.site.register(BabyDate)
admin.site.register(Feeding)
admin.site.register(BreastBumping)
admin.site.register(BodyTemperature)


@admin.register(GrowthData)
class GrowthDataAdmin(admin.ModelAdmin):
    fields = ('baby_date', 'date', 'weight', 'height', 'head_circumference', 'notes')
