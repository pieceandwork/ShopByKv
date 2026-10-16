from django.contrib.auth.views import LogoutView
from django.urls import path
from shop import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.ShopHome.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('additem/', views.AddItem.as_view(), name='additem'),
    path('contact/', views.contact, name='contact'),
    path('post/<slug:post_slug>/', views.ShowPost.as_view(), name='post'),
    path('category/<slug:cat_slug>/', views.ShopCategory.as_view(), name='category'),
    path('category/<slug:cat_slug>/model/<slug:tag_slug>/', views.ShopTag.as_view(), name='tag'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('profile/', views.ProfileUser.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='shop/password_reset_form.html',
             email_template_name='shop/password_reset_email.html',
             subject_template_name='shop/password_reset_subject.txt',
             success_url='/password-reset/done/',
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='shop/password_reset_done.html',
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='shop/password_reset_confirm.html',
             success_url='/reset/done/',
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='shop/password_reset_complete.html',
         ),
         name='password_reset_complete'),
    path('post/<slug:post_slug>/edit/', views.ShopUpdateView.as_view(), name='post_edit'),
    path('post/<slug:post_slug>/delete/', views.ShopDeleteView.as_view(), name='post_delete'),
    path('post/<slug:post_slug>/archive/', views.ShopArchiveView.as_view(), name='post_archive'),
    path('basket/', views.BasketView.as_view(), name='basket'),
    path('cart/add/<int:product_id>/', views.CartAddView.as_view(), name='cart_add'),
    path('cart/decrease/<int:product_id>/', views.CartDecreaseView.as_view(), name='cart_decrease'),
    path('cart/remove/<int:product_id>/', views.CartRemoveView.as_view(), name='cart_remove'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('cart/set/<int:product_id>/', views.CartSetView.as_view(), name='cart_set'),
]
