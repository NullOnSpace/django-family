from django.contrib import admin

from . import models


admin.site.register(models.BabyDate)
admin.site.register(models.BreastBumping)
admin.site.register(models.BodyTemperature)
admin.site.register(models.Diaper)
admin.site.register(models.BabyRelation)
admin.site.register(models.MiscItem)
admin.site.register(models.MiscRecord)


@admin.register(models.GrowthData)
class GrowthDataAdmin(admin.ModelAdmin):
    fields = ('baby_date', 'record_at', 'weight',
              'height', 'head_circumference', 'notes')


@admin.register(models.Feeding)
class FeedingAdmin(admin.ModelAdmin):
    fields = ('baby_date', 'feed_at', 'amount', 'note')
