from django.db import models
from django.utils import timezone


class Event(models.Model):
    CATEGORY_CHOICES = [
        ('activity', '體驗活動'),
        ('aiot', 'AIoT 展示'),
        ('usr', 'USR 成果'),
        ('workshop', '工作坊'),
        ('other', '其他'),
    ]

    title = models.CharField(max_length=100, verbose_name='活動名稱')
    description = models.TextField(verbose_name='活動描述')
    date = models.DateField(verbose_name='活動日期')
    location = models.CharField(max_length=200, default='水井村風雲客棧', verbose_name='活動地點')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='activity', verbose_name='類別')
    image = models.ImageField(upload_to='events/', blank=True, null=True, verbose_name='活動圖片')
    is_featured = models.BooleanField(default=False, verbose_name='首頁精選')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')

    class Meta:
        ordering = ['-date']
        verbose_name = '活動'
        verbose_name_plural = '活動列表'

    def __str__(self):
        return self.title

    def is_upcoming(self):
        return self.date >= timezone.now().date()


class Story(models.Model):
    title = models.CharField(max_length=200, verbose_name='故事標題')
    content = models.TextField(verbose_name='故事內容')
    author = models.CharField(max_length=100, blank=True, verbose_name='作者/來源')
    image = models.ImageField(upload_to='stories/', blank=True, null=True, verbose_name='故事圖片')
    published_date = models.DateField(default=timezone.now, verbose_name='發布日期')
    is_featured = models.BooleanField(default=False, verbose_name='首頁精選')

    class Meta:
        ordering = ['-published_date']
        verbose_name = '在地故事'
        verbose_name_plural = '在地故事列表'

    def __str__(self):
        return self.title


class NewsItem(models.Model):
    title = models.CharField(max_length=300, verbose_name='新聞標題')
    source = models.CharField(max_length=100, verbose_name='來源')
    url = models.URLField(blank=True, verbose_name='新聞連結')
    summary = models.TextField(verbose_name='摘要')
    published_date = models.DateField(verbose_name='發布日期')
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name='新聞圖片')

    class Meta:
        ordering = ['-published_date']
        verbose_name = '相關新聞'
        verbose_name_plural = '新聞列表'

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name='姓名')
    email = models.EmailField(verbose_name='電子郵件')
    phone = models.CharField(max_length=20, blank=True, verbose_name='電話')
    subject = models.CharField(max_length=200, verbose_name='主旨')
    message = models.TextField(verbose_name='訊息內容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    is_read = models.BooleanField(default=False, verbose_name='已讀')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '聯絡訊息'
        verbose_name_plural = '聯絡訊息列表'

    def __str__(self):
        return f'{self.name} - {self.subject}'


class AIoTProject(models.Model):
    title = models.CharField(max_length=200, verbose_name='專案名稱')
    description = models.TextField(verbose_name='專案說明')
    tech_stack = models.CharField(max_length=300, blank=True, verbose_name='技術棧')
    image = models.ImageField(upload_to='aiot/', blank=True, null=True, verbose_name='專案圖片')
    demo_url = models.URLField(blank=True, verbose_name='展示連結')
    order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'AIoT 專案'
        verbose_name_plural = 'AIoT 專案列表'

    def __str__(self):
        return self.title
