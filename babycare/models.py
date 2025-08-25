import datetime

from django.db import models
from django.utils import timezone

from utils.datetime import get_local_date

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
            date = get_local_date(timezone.now())
        if self.last_menstrual_period > date:
            raise EarlierThanLMPError(
                f"The date: {date} is earlier than the last menstrual period{self.last_menstrual_period}.")
        return (date - self.last_menstrual_period).days + 1

    def get_gestational_age_days(self, date:  datetime.date | None = None, ultrasound_fixed: bool = False) -> int:
        """
        计算孕周的天数
        早于出生的日期用于计算孕周
        晚于出生的日期用于计算PMA
        早于末次月经的日期抛出异常 EarlierThanLMPError
        :param date: 计算孕周的日期，默认为当前日期
        :param ultrasound_fixed: 是否使用超声定位的孕周初始日期
        :return: 孕周天数
        """
        if date is None:
            date = get_local_date(timezone.now())
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
            date = get_local_date(timezone.now())
        if self.birthday is None or date < get_local_date(self.birthday):
            raise NotBornError(
                f"The date for PMA: {date} is earlier than the birthday: {self.birthday}.")
        return (date - self.last_menstrual_period).days + 1

    def get_chronological_age_days(self, date: datetime.date | None = None) -> int:
        """
        计算实际年龄天数，即距离出生日期的天数
        早于出生日期的日期抛出异常 NotBornError
        :param date: 计算实际年龄的日期，默认为当前日期
        :return: 实际年龄天数
        """
        if date is None:
            date = get_local_date(timezone.now())
        if not self.is_born(date):
            raise NotBornError(
                f"The date for chronological age: {date} is earlier than the birthday: {self.birthday}.")
        else:
            return (date - get_local_date(self.birthday)).days + 1  # type: ignore

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
            date = get_local_date(timezone.now())
        if self.is_born(date):
            if self.is_preterm():
                return -self.days_to_due(date) + 1
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
            date = get_local_date(timezone.now())
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
            date = get_local_date(timezone.now())
        return self.birthday is not None and get_local_date(self.birthday) < date

    def is_preterm(self) -> bool:
        """
        判断是否为早产
        :return: 如果是早产，返回True，否则返回False
        """
        return self.is_born() and self.get_gestational_age_days(get_local_date(self.birthday)) < 259  # type: ignore


class Feeding(models.Model):
    baby_date = models.ForeignKey(
        BabyDate, on_delete=models.CASCADE, related_name='feedings')
    feed_at = models.DateTimeField(default=timezone.now)
    amount = models.FloatField()  # 喂养量，单位为毫升
    note = models.TextField(blank=True, null=True)  # 备注

    def __str__(self):
        return f"Feeding on {self.feed_at} - {self.amount}ml"
    
    @classmethod
    def get_recent_feedings(cls, limit=9):
        """
        获取最近的喂养记录
        :param limit: 返回的记录数量，默认为9
        :return: 最近的喂养记录列表
        """
        return cls.objects.filter(baby_date__isnull=False).order_by('-feed_at')[:limit]


class BreastBumping(models.Model):
    baby_date = models.ForeignKey(
        BabyDate, on_delete=models.CASCADE, related_name='breast_bumpings')
    date = models.DateTimeField(default=timezone.now)
    amount = models.FloatField()  # 挤奶量，单位为毫升
    notes = models.TextField(blank=True, null=True)  # 备注

    def __str__(self):
        return f"Breast Bumping on {self.date} - {self.amount}ml"


class Pooh(models.Model):
    POOH_AMOUNT_CHOICES = [
        ('1', '少量'),
        ('2', '中等'),
        ('3', '大量'),
    ]

    POOH_COLOR_CHOICES = {
        '金黄色': {'rgb': 'RGB(255, 215, 0)', 'hex': '#FFD700', 'cause': '母乳喂养', 'significance': '正常健康便便', 'need_medical': '无需担心'},
        '黄褐色': {'rgb': 'RGB(210, 180, 140)', 'hex': '#D2B48C', 'cause': '配方奶喂养', 'significance': '正常健康便便', 'need_medical': '无需担心'},
        '浅黄色': {'rgb': 'RGB(255, 255, 150)', 'hex': '#FFFF96', 'cause': '母乳前奶摄入多', 'significance': '正常，可能稍稀', 'need_medical': '观察'},
        '橙色': {'rgb': 'RGB(255, 165, 0)', 'hex': '#FFA500', 'cause': '食物色素（如胡萝卜）', 'significance': '通常无害', 'need_medical': '观察'},
        '绿色（正常）': {'rgb': 'RGB(100, 180, 80)', 'hex': '#64B450', 'cause': '铁剂、食物氧化、胆汁代谢', 'significance': '通常无害', 'need_medical': '观察'},
        '白色颗粒（奶瓣）': {'rgb': 'RGB(240, 240, 240)', 'hex': '#F0F0F0', 'cause': '未完全消化的奶', 'significance': '消化系统未成熟', 'need_medical': '少量无需担心'},
        '深绿色（黏液）': {'rgb': 'RGB(50, 100, 50)', 'hex': '#326432', 'cause': '肠道感染、乳糖不耐受', 'significance': '可能腹泻或消化不良', 'need_medical': '伴随症状需就医'},
        '墨绿色（胎便）': {'rgb': 'RGB(30, 60, 30)', 'hex': '#1E3C1E', 'cause': '新生儿出生后2-3天', 'significance': '正常胎便', 'need_medical': '无需担心'},
        '灰白色/陶土色': {'rgb': 'RGB(200, 200, 180)', 'hex': '#C8C8B4', 'cause': '胆道闭锁、胆汁缺乏', 'significance': '严重肝胆问题', 'need_medical': '立即就医'},
        '黑色（柏油样）': {'rgb': 'RGB(70, 50, 50)', 'hex': '#463232', 'cause': '上消化道出血（如胃溃疡）', 'significance': '可能含血', 'need_medical': '立即就医'},
        '鲜红色（血便）': {'rgb': 'RGB(255, 50, 50)', 'hex': '#FF3232', 'cause': '肛裂、肠炎、过敏', 'significance': '下消化道出血', 'need_medical': '需就医'},
        '粉红色（黏液）': {'rgb': 'RGB(255, 180, 180)', 'hex': '#FFB4B4', 'cause': '牛奶蛋白过敏、轻微肠炎', 'significance': '可能含少量血', 'need_medical': '观察，持续需就医'},
    }

    baby_date = models.ForeignKey(
        BabyDate, on_delete=models.CASCADE, related_name='poohs')
    date = models.DateTimeField(default=timezone.now)
    amount = models.CharField(
        max_length=12, choices=POOH_AMOUNT_CHOICES)  # 大便量
    color = models.CharField(
        max_length=40,
        choices=zip(POOH_COLOR_CHOICES.keys(), POOH_COLOR_CHOICES.keys()),
    )

    def __str__(self):
        return f"Pooh on {self.date} - Color: {self.color}, Amount: {self.amount}"


class BodyTemperature(models.Model):
    MEASUREMENT_CHOICES = [
        ('temporal', '额温'),
        ('tympanic', '耳温'),
        ('axillary', '腋下'),
        ('oral', '口腔'),
        ('rectal', '直肠'),
    ]
    baby_date = models.ForeignKey(
        BabyDate, on_delete=models.CASCADE, related_name='body_temperatures')
    measure_at = models.DateTimeField(default=timezone.now)
    temperature = models.FloatField()  # 体温，单位为摄氏度
    measurement = models.CharField(
        max_length=10, choices=MEASUREMENT_CHOICES, default='temporal')  # 测量方式
    notes = models.TextField(blank=True, null=True)  # 备注

    @classmethod
    def get_recent_body_temperatures(cls, limit=7):
        """
        获取最近的体温记录
        :param limit: 返回的记录数量，默认为7
        :return: 最近的体温记录列表
        """
        return cls.objects.filter(baby_date__isnull=False).order_by('-measure_at')[:limit]

    def __str__(self):
        return f"Body Temperature on {self.measure_at} - {self.temperature}°C"


class GrowthData(models.Model):
    baby_date = models.ForeignKey(
        BabyDate, on_delete=models.CASCADE, related_name='growth_data')
    date = models.DateTimeField(default=timezone.now)
    weight = models.FloatField(blank=True, null=True)  # 体重，单位为千克
    height = models.FloatField(blank=True, null=True)  # 身高，单位为厘米
    head_circumference = models.FloatField(blank=True, null=True)  # 头围，单位为厘米
    notes = models.TextField(blank=True, null=True)  # 备注

    @classmethod
    def get_recent_growth_data(cls, limit=10):
        """
        获取最近的生长数据记录
        :param limit: 返回的记录数量，默认为10
        :return: 最近的生长数据记录列表
        """
        return cls.objects.filter(baby_date__isnull=False).order_by('-date')[:limit]

    def __str__(self):
        return f"Growth Data on {self.date} - Weight: {self.weight}kg, Height: {self.height}cm, Head Circumference: {self.head_circumference}cm"
