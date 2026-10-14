from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse, reverse_lazy
from shop.forms import AddPostForm, RegisterUserForm, LoginUserForm, ProfileEditForm, ShopEditForm
from shop.mixins import ModeratorRequiredMixin
from shop.models import Shop, Category, Tag, Profile
from django.views import View
from django.views.generic import ListView, DetailView, FormView, CreateView, UpdateView, DeleteView
from shop.context import menu
from django.contrib import messages
from django.core.mail import send_mail
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_cookie


@method_decorator(cache_page(60 * 5), name='dispatch')
@method_decorator(vary_on_cookie, name='dispatch')
class ShopHome(ListView):
    model = Shop
    template_name = 'shop/index.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (
            user.groups.filter(name__in=['admin', 'moderator']).exists()
            or user.is_superuser
        ):
            return Shop.objects.all().select_related('cat')
        return Shop.published.all().select_related('cat')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'ShopByKv'
        user = self.request.user
        context['is_staff_user'] = (
            user.is_authenticated
            and (
                user.groups.filter(name__in=['admin', 'moderator']).exists()
                or user.is_superuser
            )
        )
        return context


def about(request):
    return render(request, 'shop/about.html', {'title': 'О сайте', 'menu': menu})

class ShowPost(DetailView):
    model = Shop
    template_name = 'shop/post.html'
    context_object_name = 'post'
    slug_url_kwarg = 'post_slug'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['title'] = f'Комплектующее: {self.object.cat.name}'

        context['can_edit'] = (
                user.is_authenticated
                and (
                        user.groups.filter(name__in=['admin', 'moderator']).exists()
                        or user.is_superuser
                        or self.object.author == user
                )
        )

        context['is_staff_user'] = (
                user.is_authenticated
                and (
                        user.groups.filter(name__in=['admin', 'moderator']).exists()
                        or user.is_superuser
                )
        )

        return context

    def get_queryset(self):
        user = self.request.user
        qs = Shop.objects.all()

        if user.is_authenticated and (
            user.groups.filter(name__in=['moderator', 'admin']).exists()
            or user.is_superuser
        ):
            return qs

        return qs.filter(is_ac=Shop.Status.PUBLISHED)

class AddItem(ModeratorRequiredMixin, FormView):
    form_class = AddPostForm
    template_name = 'shop/additem.html'
    extra_context = {
        'menu': menu,
        'title': 'Панель админа',
    }

    def form_valid(self, form):
        data = form.cleaned_data
        cat = data['cat']
        model_name = (data.get('model_name') or '').strip()

        slug = model_name.replace(' ', '-')
        slug = ''.join(c for c in slug if c.isalnum() or c in '-_') or 'item'
        base = slug
        i = 1
        while Shop.objects.filter(slug=slug).exists():
            i += 1
            slug = f'{base}-{i}'

        self.object = Shop.objects.create(
            title=data['title'],
            slug=slug,
            content=data['content'],
            price=data.get('price') or 0,
            stock=data.get('stock') or 0,
            is_ac=data['is_ac'],
            cat=cat,
            photo=data.get('photo'),
            author=self.request.user,
        )

        if model_name:
            tag_slug = slug
            base_tag = tag_slug
            i = 1
            while Tag.objects.filter(cat=cat, slug=tag_slug).exists():
                i += 1
                tag_slug = f'{base_tag}-{i}'
            tag = Tag.objects.create(cat=cat, name=model_name, slug=tag_slug)
            self.object.tags.add(tag)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post', kwargs={'post_slug': self.object.slug})


def contact(request):
    return render(request, 'shop/contact.html', {'title': 'Обратная связь', 'menu': menu})

class ShopCategory(ListView):
    model = Shop
    template_name = 'shop/index.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['cat_slug'])
        user = self.request.user
        if user.is_authenticated and (
            user.groups.filter(name__in=['admin', 'moderator']).exists()
            or user.is_superuser
        ):
            return Shop.objects.filter(cat=self.category).select_related('cat')
        return Shop.published.filter(cat=self.category).select_related('cat')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Комплектующее: {self.category.name}'
        context['cat_selected'] = self.category.pk
        context['cat_slug'] = self.category.slug
        context['cat_name'] = self.category.name
        user = self.request.user
        context['is_staff_user'] = (
            user.is_authenticated
            and (
                user.groups.filter(name__in=['admin', 'moderator']).exists()
                or user.is_superuser
            )
        )
        return context

class ShopTag(ListView):
    model = Shop
    template_name = 'shop/index.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_queryset(self):
        self.tag = get_object_or_404(
            Tag,
            slug=self.kwargs['tag_slug'],
            cat__slug=self.kwargs['cat_slug'],
        )
        user = self.request.user
        if user.is_authenticated and (
            user.groups.filter(name__in=['admin', 'moderator']).exists()
            or user.is_superuser
        ):
            return Shop.objects.filter(tags=self.tag).select_related('cat')
        return Shop.published.filter(tags=self.tag).select_related('cat')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Модель: {self.tag.name}'
        context['cat_selected'] = self.tag.cat.pk
        context['tag_selected'] = self.tag.slug
        context['cat_slug'] = self.tag.cat.slug
        context['cat_name'] = self.tag.cat.name
        user = self.request.user
        context['is_staff_user'] = (
            user.is_authenticated
            and (
                user.groups.filter(name__in=['admin', 'moderator']).exists()
                or user.is_superuser
            )
        )
        return context

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'shop/register.html'
    success_url = reverse_lazy('login')
    extra_context = {
        'menu': menu,
        'title': 'Регистрация',
    }


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'shop/login.html'
    extra_context = {
        'menu': menu,
        'title': 'Вход',
    }

class ProfileUser(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'shop/profile.html'
    context_object_name = 'user_profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    extra_context = {
        'menu': menu,
        'title': 'Ваш профиль',
    }

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_superuser or user.groups.filter(name='admin').exists():
            context['role'] = 'Администратор'
        elif user.groups.filter(name='moderator').exists():
            context['role'] = 'Модератор'
        else:
            context['role'] = 'Пользователь'

        return context

class ProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = ProfileEditForm
    template_name = 'shop/profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        kwargs['profile'] = profile
        return kwargs

    def get_success_url(self):
        return reverse('profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = menu
        context['title'] = 'Редактирование профиля'
        return context

class ShopUpdateView(ModeratorRequiredMixin, UpdateView):
    model = Shop
    form_class = ShopEditForm
    template_name = 'shop/additem.html'

    slug_field = 'slug'
    slug_url_kwarg = 'post_slug'

    def test_func(self):
        if not super().test_func():
            return False
        post = self.get_object()
        if self.request.user.groups.filter(name='admin').exists() or self.request.user.is_superuser:
            return True
        return post.author == self.request.user

    def get_success_url(self):
        return reverse('post', kwargs={'post_slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Панель админа'
        return context

class ShopDeleteView(ModeratorRequiredMixin, DeleteView):
    model = Shop
    template_name = 'shop/delete_confirm.html'
    success_url = reverse_lazy('home')

    slug_field = 'slug'
    slug_url_kwarg = 'post_slug'

    def test_func(self):
        if not super().test_func():
            return False
        post = self.get_object()
        if self.request.user.groups.filter(name='admin').exists() or self.request.user.is_superuser:
            return True
        return post.author == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление товара'
        return context

class ShopArchiveView(ModeratorRequiredMixin, View):
    def get(self, request, post_slug):
        post = get_object_or_404(Shop, slug=post_slug)
        if not (request.user.groups.filter(name='admin').exists() or request.user.is_superuser or post.author == request.user):
            return render(request, 'shop/no_permission.html', status=200)

        post.is_ac = not post.is_ac
        post.save()
        return redirect('post', post_slug=post.slug)

class CartAddView(View):
    def get(self, request, product_id):
        product = get_object_or_404(Shop, id=product_id)

        if product.stock <= 0:
            messages.warning(request, f'Товар «{product.title}» закончился.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        cart = request.session.get('cart', {})
        current = cart.get(str(product.id), 0)

        if current + 1 > product.stock:
            messages.warning(request, f'На складе только {product.stock} шт.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        cart[str(product.id)] = current + 1
        request.session['cart'] = cart
        request.session.modified = True
        return redirect(request.META.get('HTTP_REFERER', 'home'))

class CartDecreaseView(View):
    def get(self, request, product_id):
        cart = request.session.get('cart', {})
        pid = str(product_id)

        if pid in cart:
            cart[pid] -= 1
            if cart[pid] <= 0:
                del cart[pid]
            request.session['cart'] = cart
            request.session.modified = True

        return redirect('basket')

class CartRemoveView(View):
    def get(self, request, product_id):
        cart = request.session.get('cart', {})
        pid = str(product_id)
        if pid in cart:
            del cart[pid]
            request.session['cart'] = cart
            request.session.modified = True
        return redirect('basket')

class BasketView(LoginRequiredMixin, View):
    def get(self, request):
        cart = request.session.get('cart', {})
        cart_items = []
        total_price = 0

        for pid, qty in cart.items():
            try:
                product = Shop.objects.get(id=int(pid))
            except Shop.DoesNotExist:
                continue

            subtotal = product.price * qty
            total_price += subtotal
            cart_items.append({
                'product': product,
                'quantity': qty,
                'subtotal': subtotal,
            })

        user = request.user

        missing = []
        if not user.first_name:
            missing.append('Имя')
        if not user.last_name:
            missing.append('Фамилия')
        if not user.profile.address:
            missing.append('Адрес доставки')

        missing_text = ', '.join(missing)

        user_data_complete = (
                user.is_authenticated
                and user.first_name
                and user.last_name
                and user.profile.address
        )

        return render(request, 'shop/basket.html', {
            'menu': menu,
            'title': 'Корзина',
            'cart_items': cart_items,
            'total_price': total_price,
            'user_data_complete': user_data_complete,
            'missing_text': missing_text,
        })

class CheckoutView(View):
    def get(self, request):
        user = request.user

        if not user.is_authenticated:
            return redirect('login')

        if not (user.first_name and user.last_name and user.profile.address):
            messages.warning(request, 'Заполните Имя, Фамилию и Адрес доставки.')
            return redirect('profile_edit')

        cart = request.session.get('cart', {})

        if not cart:
            messages.warning(request, 'Корзина пуста.')
            return redirect('basket')

        order_lines = []
        total_price = 0

        for pid, qty in cart.items():
            try:
                product = Shop.objects.get(id=int(pid))
            except Shop.DoesNotExist:
                continue

            if product.stock < qty:
                messages.warning(request, f'Товар «{product.title}» закончился. Доступно {product.stock} шт.')
                return redirect('basket')

            product.stock -= qty
            product.save()

            subtotal = product.price * qty
            total_price += subtotal

            order_lines.append(f'{product.title} - {qty} шт.')

        order_text = '\n'.join(order_lines)

        message = f"""Здравствуйте, {user.first_name} {user.last_name}!
Вы успешно оформили заказ на ShopByKv. Благодарим за заказ!

Ваш заказ:
{order_text}

Вся сумма заказа составила: {total_price} ₽

Заказ будет доставлен по адресу: {user.profile.address}


Остались вопросы или есть предложения? Напишите нам на почту: shopbykv@gmail.com

С уважением,
ShopByKv"""

        send_mail(
            subject='Заказ на ShopByKv',
            message=message,
            from_email='shopbykv@gmail.com',
            recipient_list=[user.email],
            fail_silently=False,
        )

        request.session['cart'] = {}
        request.session.modified = True

        return render(request, 'shop/checkout_success.html', {
            'menu': menu,
            'title': 'Заказ оформлен',
            'user': user,
        })

def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Извините, но страница не была найдена! D:</h1>")
