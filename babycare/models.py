import datetime

from django.db import models
from django.utils import timezone
from django.conf import settings

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
    nickname = models.CharField(max_length=20, null=True, unique=True)
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

    def __str__(self):
        return self.nickname
    
    def can_be_edited_by(self, user) -> bool:
        return BabyRelation.objects.filter(
            baby_date=self.pk,
            status__in=BabyRelation.editable_status(),
            request_by=user,
        ).exists()


class BabyRelation(models.Model):
    REQUEST_STATUS = (
        (0, "申请中"),
        (1, "已拒绝"),
        (2, "监护人"),
        (3, "亲人"),
        (4, "关心的人"),
    )
    baby_date = models.ForeignKey(
        BabyDate, on_delete=models.CASCADE, related_name='relations')
    request_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="baby_relations")
    request_at = models.DateTimeField(auto_now_add=True)
    approve_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="baby_approveds",
        null=True,
        blank=True
    )
    approve_at = models.DateTimeField(null=True, blank=True)
    status = models.PositiveIntegerField(choices=REQUEST_STATUS, default=0)

    def __str__(self):
        return f"{self.request_by} - {self.baby_date} - {self.get_status_display()}" # type: ignore
    
    def can_be_approved_by(self, user) -> bool:
        """用户是否可以审批该申请
        即当前baby_date的关系中存在一个该用户为grantable_status的关系
        """
        return BabyRelation.objects.filter(
            baby_date=self.baby_date,
            status__in=BabyRelation.grantable_status(),
            request_by=user,
        ).exists()
    
    def status_css_class(self):
        STATUS_CSS_CLASSES ={
            0: 'person-fill-add',
            1: 'person-fill-x',
            2: 'person-gear',
            3: 'person-hearts',
            4: 'person-heart',
        }
        return STATUS_CSS_CLASSES.get(self.status, 'person-fill-slash')
    
    @staticmethod
    def accessible_status():
        """可以访问baby相关的状态"""
        return (2, 3, 4)

    @staticmethod
    def editable_status():
        """可以编辑baby相关的状态"""
        return (2, 3, 4)
    
    @staticmethod
    def pending_status():
        """待处理的状态"""
        return (0, )

    @staticmethod
    def grantable_status():
        """有授权权限的状态"""
        return (2, )
    
    @staticmethod
    def granted_status():
        """处理后的状态,包括拒绝"""
        return (1, 2, 3, 4)
    
    @staticmethod
    def reject_status():
        """拒绝的状态"""
        return (1, )


class Feeding(models.Model):
    baby_date = models.ForeignKey(
        BabyDate, on_delete=models.CASCADE, related_name='feedings')
    feed_at = models.DateTimeField(default=timezone.now)
    amount = models.FloatField()  # 喂养量，单位为毫升
    note = models.TextField(blank=True, null=True)
    class Meta:
        get_latest_by = 'feed_at'

    def __str__(self):
        feed_at_local = timezone.localtime(self.feed_at)
        return f"Feeding on {feed_at_local} - {self.amount}ml"
    
    def can_be_edited_by(self, user):
        return self.baby_date.can_be_edited_by(user)

    @classmethod
    def get_recent_feedings(cls, baby_date_id, limit=9):
        """
        获取最近的喂养记录
        :param limit: 返回的记录数量，默认为9
        :return: 最近的喂养记录列表
        """
        return cls.objects.filter(baby_date=baby_date_id).order_by('-feed_at')[:limit]


class BreastBumping(models.Model):
    baby_date = models.ForeignKey(
        BabyDate, on_delete=models.CASCADE, related_name='breast_bumpings')
    date = models.DateTimeField(default=timezone.now)
    amount = models.FloatField()  # 挤奶量，单位为毫升
    notes = models.TextField(blank=True, null=True)  # 备注

    def __str__(self):
        return f"Breast Bumping on {self.date} - {self.amount}ml"


class Diaper(models.Model):
    POOH_AMOUNT_CHOICES = [
        ('0', '无'),
        ('1', '少量'),
        ('2', '中等'),
        ('3', '大量'),
    ]

    POOH_COLOR_CHOICES = {
        '金黄色': {'rgb': 'RGB(255, 215, 0)', 'hex': '#FFD700', 'cause': '母乳喂养', 'significance': '正常健康便便', 'need_medical': '无需担心'},
        '黄褐色': {'rgb': 'RGB(210, 180, 140)', 'hex': '#D2B48C', 'cause': '配方奶喂养', 'significance': '正常健康便便', 'need_medical': '无需担心'},
        '浅黄色': {'rgb': 'RGB(255, 255, 150)', 'hex': '#FFFF96', 'cause': '母乳前奶摄入多', 'significance': '正常，可能稍稀', 'need_medical': '观察'},
        '绿色（正常）': {'rgb': 'RGB(100, 180, 80)', 'hex': '#64B450', 'cause': '铁剂、食物氧化、胆汁代谢', 'significance': '通常无害', 'need_medical': '观察'},
        '深绿色（黏液）': {'rgb': 'RGB(50, 100, 50)', 'hex': '#326432', 'cause': '肠道感染、乳糖不耐受', 'significance': '可能腹泻或消化不良', 'need_medical': '伴随症状需就医'},
        '白色颗粒（奶瓣）': {'rgb': 'RGB(240, 240, 240)', 'hex': '#F0F0F0', 'cause': '未完全消化的奶', 'significance': '消化系统未成熟', 'need_medical': '少量无需担心'},
        '粉红色（黏液）': {'rgb': 'RGB(255, 180, 180)', 'hex': '#FFB4B4', 'cause': '牛奶蛋白过敏、轻微肠炎', 'significance': '可能含少量血', 'need_medical': '观察，持续需就医'},
        '橙色': {'rgb': 'RGB(255, 165, 0)', 'hex': '#FFA500', 'cause': '食物色素（如胡萝卜）', 'significance': '通常无害', 'need_medical': '观察'},
        '墨绿色（胎便）': {'rgb': 'RGB(30, 60, 30)', 'hex': '#1E3C1E', 'cause': '新生儿出生后2-3天', 'significance': '正常胎便', 'need_medical': '无需担心'},
        '灰白色/陶土色': {'rgb': 'RGB(200, 200, 180)', 'hex': '#C8C8B4', 'cause': '胆道闭锁、胆汁缺乏', 'significance': '严重肝胆问题', 'need_medical': '立即就医'},
        '黑色（柏油样）': {'rgb': 'RGB(70, 50, 50)', 'hex': '#463232', 'cause': '上消化道出血（如胃溃疡）', 'significance': '可能含血', 'need_medical': '立即就医'},
        '鲜红色（血便）': {'rgb': 'RGB(255, 50, 50)', 'hex': '#FF3232', 'cause': '肛裂、肠炎、过敏', 'significance': '下消化道出血', 'need_medical': '需就医'},
    }

    PEE_AMOUNT_CHOICES = (
        ('0', '无'),
        ('1', '少量'),
        ('2', '正常'),
        ('3', '大量'),
    )

    PEE_COLOR_CHOICES = (
        ('0', '微黄'),
        ('1', '透明'),
        ('2', '深黄'),
    )

    PEE_COLOR_MAPPING = {
        '0': '#FFFF96',
        '1': '#F0F0F0',
        '2': '#FFD700',
    }

    baby_date = models.ForeignKey(
        BabyDate, on_delete=models.CASCADE, related_name='poohs')
    create_at = models.DateTimeField(default=timezone.now)
    pooh_amount = models.CharField(
        max_length=12, choices=POOH_AMOUNT_CHOICES, default='0')
    pooh_color = models.CharField(
        max_length=40,
        choices=zip(POOH_COLOR_CHOICES.keys(), POOH_COLOR_CHOICES.keys()),
        default='金黄色',
        blank=True,
        null=True,
    )
    pee_amount = models.CharField(
        max_length=12, 
        choices=PEE_AMOUNT_CHOICES,
        default='0',
    )
    pee_color = models.CharField(
        max_length=2,
        choices=PEE_COLOR_CHOICES,
        default='0',
        blank=True,
        null=True,
    )
    notes = models.CharField(
        max_length=80,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Change Diaper at {self.create_at}"

    @classmethod
    def get_recent_diapers(cls, baby_date_id, limit=9):
        return cls.objects.filter(baby_date=baby_date_id).order_by('-create_at')[:limit]
    
    def get_pooh_style(self):
        return self.POOH_COLOR_CHOICES.get(self.pooh_color, {'hex': 'inherit'}).get('hex')
    
    def get_pooh_desc(self):
        if self.pooh_amount is None:
            return ''
        elif self.pooh_color in self.POOH_COLOR_CHOICES:
            detail = self.POOH_COLOR_CHOICES.get(self.pooh_color)
            if detail is not None:
                cause = detail.get('cause')
            else:
                cause = ''
            return f'{self.pooh_color} - {cause}'

    def get_pee_style(self):
        return self.PEE_COLOR_MAPPING.get(self.pee_color, 'inherit')



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
    temperature = models.FloatField()
    measurement = models.CharField(
        max_length=10, choices=MEASUREMENT_CHOICES, default='temporal')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        get_latest_by = 'measure_at'

    @classmethod
    def get_recent_temp(cls, baby_date_id, limit=7):
        """
        获取最近的体温记录
        :param limit: 返回的记录数量，默认为7
        :return: 最近的体温记录列表
        """
        return cls.objects.filter(baby_date=baby_date_id).order_by('-measure_at')[:limit]

    def __str__(self):
        return f"Body Temperature on {self.measure_at} - {self.temperature}°C"


class GrowthData(models.Model):
    baby_date = models.ForeignKey(
        BabyDate, on_delete=models.CASCADE, related_name='growth_datas')
    record_at = models.DateTimeField(default=timezone.now)
    weight = models.FloatField(blank=True, null=True)  # 体重，单位为千克
    height = models.FloatField(blank=True, null=True)  # 身高，单位为厘米
    head_circumference = models.FloatField(blank=True, null=True)  # 头围，单位为厘米
    notes = models.TextField(blank=True, null=True)  # 备注

    class Meta:
        get_latest_by = 'record_at'

    @classmethod
    def get_recent_growth_data(cls, baby_date_id, limit=10):
        """
        获取最近的生长数据记录
        :param limit: 返回的记录数量，默认为10
        :return: 最近的生长数据记录列表
        """
        return cls.objects.filter(baby_date=baby_date_id).order_by('-record_at')[:limit]

    def __str__(self):
        return f"Growth Data on {self.record_at} - Weight: {self.weight}kg, Height: {self.height}cm, Head Circumference: {self.head_circumference}cm"
