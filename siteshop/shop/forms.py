from django import forms
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


from .models import Category, Tag, Shop, Profile


# class AddPostForm(forms.Form):
#     title = forms.CharField(max_length=255, label="Название", widget=forms.TextInput(attrs={'class': 'form-input'}))
#     slug = forms.SlugField(max_length=255, label="URL")
#     content = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'rows': 5}), label="Описание")
#     is_ac = forms.BooleanField(label="Статус")
#     cat = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Не выбрано", label="Комплектующее")


class AddPostForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        label="Модель",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'NVIDIA GeForce RTX 5080',
        })
    )
    content = forms.CharField(
        label="Описание",
        widget=forms.Textarea(attrs={
            'cols': 50,
            'rows': 5,
            'placeholder': 'Флагманская видеокарта нового поколения…',
        })
    )
    price = forms.DecimalField(
        label='Цена (₽)',
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'step': '0.01',
            'placeholder': '189990',
        }),
    )
    stock = forms.IntegerField(
        label='Кол-во на складе',
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '10',
        }),
    )
    photo = forms.ImageField(
        label="Изображение",
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-input'}),
    )
    is_ac = forms.BooleanField(
        label="Статус",
        required=False,
    )
    cat = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Не выбрано",
        label="Комплектующее",
    )
    model_name = forms.CharField(
        label="URL модели",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'RTX-5080',
        })
    )

    def clean(self):
        cleaned = super().clean()
        cat = cleaned.get('cat')
        model_name = (cleaned.get('model_name') or '').strip()

        if cat and model_name:
            if Tag.objects.filter(cat=cat, name__iexact=model_name).exists():
                self.add_error(
                    'model_name',
                    f'Модель «{model_name}» уже есть в категории «{cat.name}». '
                    f'Введите другую.'
                )
        return cleaned

class RegisterUserForm(UserCreationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={'class': 'form-input'}),
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-input'}),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
    )
    password2 = forms.CharField(
        label="Повтор пароля",
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
    )

    first_name = forms.CharField(
        label="Имя",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Необязательно',
        }),
    )
    last_name = forms.CharField(
        label="Фамилия",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Необязательно',
        }),
    )
    address = forms.CharField(
        label="Адрес доставки",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Необязательно',
        }),
    )
    avatar = forms.ImageField(
        label="Аватар",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-input'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            user.first_name = self.cleaned_data.get('first_name', '')
            user.last_name = self.cleaned_data.get('last_name', '')
            user.email = self.cleaned_data.get('email', '')
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.address = self.cleaned_data.get('address', '')
            if self.cleaned_data.get('avatar'):
                profile.avatar = self.cleaned_data['avatar']
            profile.save()

        return user

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={'class': 'form-input'}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
    )

class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Имя', max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        label='Фамилия', max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )

    address = forms.CharField(
        label='Адрес доставки', max_length=255, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    content = forms.CharField(
        label='О себе', required=False,
        widget=forms.Textarea(attrs={'cols': 50, 'rows': 5})
    )
    avatar = forms.ImageField(
        label="Аватар",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-input'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name']   # это поля User

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)

        if self.profile:
            self.fields['address'].initial = self.profile.address
            self.fields['content'].initial = self.profile.content

    def save(self, commit=True):
        user = super().save(commit=commit)
        if self.profile:
            self.profile.address = self.cleaned_data.get('address', '')
            self.profile.content = self.cleaned_data.get('content', '')

            if self.cleaned_data.get('avatar'):
                self.profile.avatar = self.cleaned_data['avatar']

            self.profile.save()
        return user

class ShopEditForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['title', 'content', 'price', 'stock', 'is_ac', 'cat', 'photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['cat'].empty_label = 'Не выбрано'

        self.fields['title'].widget.attrs.update({'class': 'form-input'})
        self.fields['content'].widget.attrs.update({'class': 'form-input'})
        self.fields['price'].widget.attrs.update({'class': 'form-input', 'step': '0.01'})
        self.fields['stock'].widget.attrs.update({'class': 'form-input'})
        self.fields['photo'].widget.attrs.update({'class': 'form-input'})
