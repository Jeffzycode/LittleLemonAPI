from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.MenuItemsView.as_view()),
    path('categories', views.CategoriesView.as_view()),
    path('cart', views.CartView.as_view()),
    path('order-items', views.OrderItemView.as_view()),
    path('order', views.OrderView.as_view()),
    path('assign', views.AssignView.as_view()),
]