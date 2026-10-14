from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_ac=Shop.Status.PUBLISHED)

class Shop(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField('Модель', max_length=255)
    slug = models.SlugField('URL-модели', max_length=255, unique=True, db_index=True)
    content = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField('Кол-во на складе', default=0)
    photo = models.ImageField('Изображение', upload_to='photos/%Y/%m/%d/')
    time_create = models.DateTimeField('Создано', auto_now_add=True)
    time_update = models.DateTimeField('Обновлено', auto_now=True)
    is_ac = models.BooleanField('Статус', choices=Status.choices, default=Status.PUBLISHED)
    cat = models.ForeignKey(
        'Category',
        on_delete=models.PROTECT,
        verbose_name='Комплектующее',
    )
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        related_name='posts',
        verbose_name='Модель',
    )
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Автор',
    )

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Комплектующее"
        verbose_name_plural = "Комплектующие"
        ordering = ['-time_create']
    unique_together = ('cat', 'slug')

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})

class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug =  models.SlugField(max_length=255, unique=True, db_index=True)

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категории комплектующих"
        verbose_name_plural = "Категории комплектующих"
        ordering = ['id']

class Tag(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, db_index=True)
    cat = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='tags')

    def get_absolute_url(self):
        return reverse('tag', kwargs={
            'cat_slug': self.cat.slug,
            'tag_slug': self.slug,
        })

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Модели комплектующих"
        verbose_name_plural = "Модели комплектующих"
        unique_together = ('cat', 'name')
        ordering = ['id']


class UploadFiles(models.Model):
    file = models.FileField(upload_to='uploads_model')

class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    address = models.CharField('Адрес доставки', max_length=255, blank=True)
    content = models.TextField('О себе', blank=True)
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/%Y/%m/%d/',
        blank=True,
        null=True,
        default='avatars/default.png',
    )

    def __str__(self):
        return f'Профиль {self.user.username}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)
