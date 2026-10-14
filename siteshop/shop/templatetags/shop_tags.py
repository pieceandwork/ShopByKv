from django import template
import shop.views as views
from shop.models import Category, Tag, Shop
from shop.context import menu
from django.core.cache import cache


register = template.Library()

@register.inclusion_tag('shop/list_categories.html')
def show_categories(cat_selected=0, tag_selected=None):
    cats_data = cache.get('all_categories')

    if cats_data is None:
        cats_data = []
        for cat in Category.objects.all():
            tags = list(cat.tags.filter(
                posts__is_ac=Shop.Status.PUBLISHED
            ).values('id', 'name', 'slug').distinct())

            cats_data.append({
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'tags': tags,
            })

        cache.set('all_categories', cats_data, 600)

    return {
        'cats_data': cats_data,
        'cat_selected': cat_selected,
        'tag_selected': tag_selected,
    }

@register.inclusion_tag('shop/list_tags.html')
def show_all_tags(cat_selected=0):
    if cat_selected:
        tags = Tag.objects.filter(cat_id=cat_selected)
    else:
        tags = Tag.objects.none()
    return {'tags': tags}
