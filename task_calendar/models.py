from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import timezone


class TaskCalendar(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('one_time', 'One Time'),
    ]
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='one_time',
    )
    is_completed = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)
    create_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    create_at = models.DateTimeField(auto_now_add=True)
    target_ct = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name='target_obj',
        on_delete=models.CASCADE
    )
    target_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_ct', 'target_id')

    def __str__(self):
        return self.description

    def is_outdated(self):
        return self.end_date < timezone.now()
    
    def get_status(self):
        if self.is_completed:
            return '已完成'
        elif self.is_outdated():
            return '已过期'
        elif self.start_date <= timezone.now() <= self.end_date:
            return '进行中'
        else:
            return '未开始'
    
    def get_display_class(self):
        if self.is_completed:
            return 'task-calendar-completed'
        elif self.is_outdated():
            return 'task-calendar-outdated'
        elif self.start_date <= timezone.now() <= self.end_date:
            return 'task-calendar-active'
        else:
            return 'task-calendar-coming'

    class Meta:
        ordering = ['start_date']
