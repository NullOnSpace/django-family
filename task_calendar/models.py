from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import timezone

# (fixme) 现在输入的是date 记录的是datetime 时间比较时都转化为了localdate比较


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
        return timezone.localtime(self.end_date).date() < timezone.localdate()

    def get_status(self):
        if self.is_completed:
            return '已完成'
        elif self.is_outdated():
            return '已过期'
        elif (timezone.localtime(self.start_date).date()
              <= timezone.localdate()
              <= timezone.localtime(self.end_date).date()):
            return '进行中'
        else:
            return '未开始'

    def get_display_class(self):
        status = self.get_status()
        if status == '已完成':
            return 'task-calendar-completed'
        elif status == '已过期':
            return 'task-calendar-outdated'
        elif status == '进行中':
            return 'task-calendar-active'
        else:
            return 'task-calendar-coming'

    class Meta:
        ordering = ['start_date']
