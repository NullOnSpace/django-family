from django.contrib import admin

from . import models


admin.site.register(models.BabyDate)
admin.site.register(models.BreastBumping)
admin.site.register(models.BodyTemperature)
admin.site.register(models.BabyRelation)


@admin.register(models.GrowthData)
class GrowthDataAdmin(admin.ModelAdmin):
    fields = ('baby_date', 'date', 'weight', 'height', 'head_circumference', 'notes')

@admin.register(models.Feeding)
class FeedingAdmin(admin.ModelAdmin):
    fields = ('baby_date', 'feed_at', 'amount', 'note')