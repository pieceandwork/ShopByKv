from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Shop, Category, Tag


@receiver([post_save, post_delete], sender=Shop)
def invalidate_shop_cache(sender, instance, **kwargs):
    cache.delete('all_categories')       # список категорий/тегов
    cache.delete('shop_list')            # список товаров


@receiver([post_save, post_delete], sender=Category)
def invalidate_category_cache(sender, instance, **kwargs):
    cache.delete('all_categories')


@receiver([post_save, post_delete], sender=Tag)
def invalidate_tag_cache(sender, instance, **kwargs):
    cache.delete('all_categories')
