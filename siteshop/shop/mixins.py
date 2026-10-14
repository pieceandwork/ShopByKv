from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from shop.context import menu


class ModeratorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and (
                self.request.user.groups.filter(name__in=['moderator', 'admin']).exists()
                or self.request.user.is_superuser
            )
        )

    def handle_no_permission(self):
        return render(self.request, 'shop/no_permission.html', {
            'menu': menu,
            'title': 'Недостаточно прав',
            'cat_selected': 0,
        }, status=200)
