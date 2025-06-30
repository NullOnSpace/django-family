from django import template

from ..models import BabyDate


register = template.Library()

@register.filter
def get_gestational_age_weeks(baby_date: BabyDate, ultrasound_fixed: bool = False) -> str:
    """
    获取孕周的周数
    (fixme) 晚于出生的日期不是期待的显示结果
    :param baby_date: BabyDate 实例
    :param date: 计算孕周的日期，默认为当前日期
    :param ultrasound_fixed: 是否使用超声定位反推的孕周初始日期
    :return: 孕周周数
    """
    days = baby_date.get_gestational_age_days(date=None, ultrasound_fixed=ultrasound_fixed)
    return f"{days // 7}周{days % 7}天" if days >= 0 else f"尚未开始计算孕周"