from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category, Shop, Tag

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('title', 'cat', 'author', 'is_ac')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='admin').exists() or request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name='admin').exists() or request.user.is_superuser:
            return True
        if obj is not None:
            return obj.author == request.user
        return super().has_change_permission(request, obj)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'cat')
    list_filter = ('cat',)
    prepopulated_fields = {'slug': ('name',)}
