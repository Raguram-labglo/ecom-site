from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
routers = DefaultRouter()
routers.register('product', Productlist),
routers.register('cart', Usercart),
routers.register('user', Customer_detail),
routers.register('wish', AddtoWishListView),
routers.register('order', Orders_detail)

urlpatterns = [path('login/', LoginView.as_view(), name = 'login'),
               path('Register/', Register.as_view()),
               path('checkout/', Checkout.as_view()),
               path('Webhook/', Webhook.as_view())
               ]+routers.urls
