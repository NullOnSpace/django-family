import datetime

from django.db import models
from django.utils import timezone


class BabyDate(models.Model):
    last_menstrual_period = models.DateField()  # 末次月经
    estimated_due_date = models.DateField()  # 推测预产期
    birthday = models.DateTimeField(null=True, blank=True)  # 出生时间
    ultrasound_fixed_days = models.DurationField(
        default=datetime.timedelta())  # 超声定位反推的孕周初始日期 正数代表比末次月经晚，负数代表比末次月经早

    def get_gestational_age_days(self, date:  datetime.date | None = None, ultrasound_fixed: bool = False) -> int:
        """
        计算孕周的天数
        (fixme) 晚于出生的日期或早于末次月经的日期会导致计算错误
        :param date: 计算孕周的日期，默认为当前日期
        :return: 孕周天数
        """
        if date is None:
            date = timezone.now().date()
        date_diff = date - self.last_menstrual_period
        if ultrasound_fixed:
            date_diff -= self.ultrasound_fixed_days
        return date_diff.days
