from datetime import datetime, timedelta

from django import template
from django.utils import timezone

from ..models import BabyDate


register = template.Library()

@register.filter
def get_gestational_age_weeks(baby_date: BabyDate, ultrasound_fixed: bool = False) -> str:
    """
    获取孕周的周数
    :param baby_date: BabyDate 实例
    :param ultrasound_fixed: 是否使用超声定位反推的孕周初始日期
    :return: 孕周周数
    """
    days = baby_date.get_gestational_age_days(date=None, ultrasound_fixed=ultrasound_fixed)
    days = days - 1
    return f"{days // 7}周{days % 7}天" if days >= 0 else f"尚未开始计算孕周"

@register.filter
def get_age_months(days: int) -> str:
    """
    获取月龄
    :param days: 天数
    :return: 月龄和天数
    """
    return f"{days // 30}月{days % 30}天" if days >= 0 else f"尚未开始计算月龄"

@register.filter
def zh_timesince(dt: datetime, conference: datetime | None = None):
    if conference is None:
        conference = timezone.now()
    delta = conference - dt
    res = ""
    if delta.days > 0:
        res += f"{delta.days}天"
    if delta.seconds > 0:
        res += f"{delta.seconds // 3600}小时"
        res += f"{delta.seconds % 3600 // 60}分钟"
    return res