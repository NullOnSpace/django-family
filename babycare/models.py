import datetime

from django.db import models
from django.utils import timezone


class EarlierThanLMPError(Exception):
    """Exception raised when the date is earlier than the last menstrual period."""
    pass


class LaterThanBirthError(Exception):
    """Exception raised when the date is later than the birthday."""
    pass


class NotBornError(Exception):
    """Exception raised when trying to calculate age for a baby that has not been born yet."""
    pass


class BabyDate(models.Model):
    last_menstrual_period = models.DateField()  # 末次月经
    estimated_due_date = models.DateField(null=True, blank=True)  # 推测预产期
    birthday = models.DateTimeField(null=True, blank=True)  # 出生时间
    ultrasound_fixed_days = models.IntegerField(
        default=0)  # 超声定位矫正的天数 正数代表比末次月经晚，负数代表比末次月经早

    def days_to_lmp(self, date: datetime.date | None = None) -> int:
        """
        计算距离末次月经的天数
        :param date: 计算距离末次月经的日期，默认为当前日期
        :return: 距离末次月经的天数
        """
        if date is None:
            date = timezone.now().date()
        if self.last_menstrual_period > date:
            raise EarlierThanLMPError(
                f"The date: {date} is earlier than the last menstrual period{self.last_menstrual_period}.")
        return (date - self.last_menstrual_period).days

    def get_gestational_age_days(self, date:  datetime.date | None = None, ultrasound_fixed: bool = False) -> int:
        """
        计算孕周的天数
        晚于出生的日期抛出异常 LaterThanBirthError
        早于末次月经的日期抛出异常 EarlierThanLMPError
        :param date: 计算孕周的日期，默认为当前日期
        :param ultrasound_fixed: 是否使用超声定位的孕周初始日期
        :return: 孕周天数
        """
        if date is None:
            date = timezone.now().date()
        if self.birthday and date > self.birthday.date():
            raise LaterThanBirthError(
                f"The date for GA: {date} is later than the birthday: {self.birthday}.")
        days = self.days_to_lmp(date)
        if ultrasound_fixed:
            days -= self.ultrasound_fixed_days
        return days

    def get_postmenstrual_age_days(self, date: datetime.date | None = None) -> int:
        """
        计算月经后年龄天数(PMA)，即胎龄加上出生后实际年龄
        早于出生的日期抛出异常 NotBornError
        :param date: 计算月经后年龄的日期，默认为当前日期
        :return: 月经后年龄天数
        """
        if date is None:
            date = timezone.now().date()
        if self.birthday is None or date < self.birthday.date():
            raise NotBornError(
                f"The date for PMA: {date} is earlier than the birthday: {self.birthday}.")
        return (date - self.last_menstrual_period).days

    def get_chronological_age_days(self, date: datetime.date | None = None) -> int:
        """
        计算实际年龄天数，即距离出生日期的天数
        早于出生日期的日期抛出异常 NotBornError
        :param date: 计算实际年龄的日期，默认为当前日期
        :return: 实际年龄天数
        """
        if date is None:
            date = timezone.now().date()
        if not self.is_born(date):
            raise NotBornError(
                f"The date for chronological age: {date} is earlier than the birthday: {self.birthday}.")
        else:
            return (date - self.birthday.date()).days  # type: ignore

    def get_corrected_age_days(self, date: datetime.date | None = None) -> int:
        """
        计算矫正年龄天数
        如果是早产，则使用预产期计算矫正年龄的天数
        如果是足月出生，则返回实际年龄
        如果尚未出生，则抛出异常 NotBornError
        :param date: 计算矫正年龄的日期，默认为当前日期
        :return: 矫正年龄天数
        """
        if date is None:
            date = timezone.now().date()
        if self.is_born(date):
            if self.is_preterm():
                return -self.days_to_due(date)
            else:
                return self.get_chronological_age_days(date)
        else:
            raise NotBornError(
                f"The date for corrected age: {date} is earlier than the birthday: {self.birthday}.")

    def days_to_due(self, date: datetime.date | None = None) -> int:
        """
        计算距离预产期的天数(足月后为负数)
        出生前用于计算距离预产期的天数
        出生后用于计算早产儿的矫正年龄
        早于末次月经的日期抛出异常 EarlierThanLMPError
        :param date: 计算距离预产期的日期，默认为当前日期
        :return: 距离预产期的天数
        """
        if date is None:
            date = timezone.now().date()
        if self.last_menstrual_period > date:
            raise EarlierThanLMPError(
                f"The date: {date} is earlier than the last menstrual period: {self.last_menstrual_period}.")
        return (self.get_due_date() - date).days

    def get_due_date(self) -> datetime.date:
        """
        获取预产期
        如果没有设置预产期，则根据末次月经推算
        :return: 预产期
        """
        if self.estimated_due_date is None:
            # 默认推算280天
            return self.last_menstrual_period + datetime.timedelta(days=280)
        return self.estimated_due_date

    def is_born(self, date: datetime.date | None = None) -> bool:
        """
        判断是否已经出生
        :return: 如果已经出生，返回True，否则返回False
        """
        if date is None:
            date = timezone.now().date()
        return self.birthday is not None and self.birthday.date() < date

    def is_preterm(self) -> bool:
        """
        判断是否为早产
        :return: 如果是早产，返回True，否则返回False
        """
        return self.is_born() and self.get_gestational_age_days(self.birthday.date()) < 259  # type: ignore
