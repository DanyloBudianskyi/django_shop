from django.urls import path
from . import views

app_name = 'discounts'

urlpatterns = [
    # Знижки на товари
    path('product/<int:product_id>/', views.product_discounts, name='product_discounts'),
    path('add/<int:product_id>/', views.add_discount, name='add_discount'),
    path('edit/<int:discount_id>/', views.edit_discount, name='edit_discount'),
    path('delete/<int:discount_id>/', views.delete_discount, name='delete_discount'),

    # Промокоди
    path('promo/', views.promo_code_list, name='promo_code_list'),
    path('promo/create/', views.create_promo_code, name='create_promo_code'),
    path('promo/apply/', views.apply_promo_code, name='apply_promo_code'),
    path('promo/remove/', views.remove_promo_code, name='remove_promo_code'),
    path('promo/stats/<int:code_id>/', views.promo_code_stats, name='promo_code_stats'),
]