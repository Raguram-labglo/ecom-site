from django.shortcuts import HttpResponse, render, redirect
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.views import APIView
import stripe

from api.models import (Product,
                        Cart,
                        Order,
                        Wish,
                        User,
                        Paymets
                        )
from api.serializers import (RegisterSerializers,
                             Loginserializer,
                             Productserializer,
                             Cartserializer,
                             Orderserializer,
                             Wishlistserializer)

from django.contrib.auth import authenticate, login
from django.db.models import Sum
from rest_framework.authtoken.models import Token
from django.conf import settings

endpoint_secret = 'whsec_66e4f8db2c43802cc38b65b57f02618cdbf8e0f5c5421491afd321a9fe66a35b'
stripe.api_key = settings.STRIPE_SECRET_KEY

class LoginView(APIView):

    serializer_class = Loginserializer

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")
        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'})
        user = authenticate(username=username, password=password)

        if not user:
            return Response({'error': 'Invalid Credentials'})
        login(request, user)
        token, li = Token.objects.get_or_create(user=user)

        return Response({'token': token.key})


class Pagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class Register(generics.ListCreateAPIView):

    queryset = User.objects.all()
    serializer_class = RegisterSerializers


class Productlist(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = Productserializer
    pagination_class = Pagination


class Usercart(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = Cartserializer
    pagination_class = Pagination

    def perform_create(self, serializer):
        product = Product.objects.get(id=int(self.request.data['product']))
        serializer.save(user=self.request.user, price=product.price * int(self.request.data['quantity']), is_active=True)
    def list(self, request, *args, **kwargs):
        queryset = Cart.objects.filter(user=request.user.id)
        serializer = Cartserializer(queryset, many=True)
        return Response(serializer.data)


class Customer_detail(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = Loginserializer


class AddtoWishListView(viewsets.ModelViewSet):
    queryset = Wish.objects.all()
    serializer_class = Wishlistserializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class Checkout(APIView):
    def post(self, request):
        cart = Cart.objects.filter(user=self.request.user,is_active=True)
        orders = Order.objects.create(user= self.request.user, order_status=1)
        price = (cart.aggregate(Sum('price'))['price__sum'])
        orders.order_items.add(*cart)
        orders.order_price = int(price)
        orders.tax_price = int(18/100*int(price))+int(price)
        orders.save()
        products = orders.order_items.all()
        prices = []
        for item in products:
            product = stripe.Product.create(
                name=item.product.name)
            price = stripe.Price.create(product=product.id, unit_amount=int(
                item.product.price + int(18/100*item.product.price))*100, currency='inr',)
            prices.append(price)
            print('kjbxcshdbadshlvbfbadhfrvb', price)
        line_items = []
        for item, price in zip(products, prices):
            line_items.append({'price': price, 'quantity': item.quantity})
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            metadata={'order ID': orders.id},
            mode='payment',
            success_url='http://127.0.0.1:8000/',
            cancel_url='http://127.0.0.1:8000/'
        )
        
        Paymets.objects.create(order=orders, transaction_id=session['id'])
        cart.update(is_active=False)
        return Response({'checkout': session.url})


charges = []
order = []
pay_status = []
class Webhook(APIView):
    
    def post(self, request):
        payload = request.body.decode('utf-8')
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

        if event['type'] == 'charge.succeeded':
            session = event['data']['object']['id']
            status = event['data']['object']['outcome']['seller_message']
            charges.append(session)
           # pay_status.append(status)
        
        if event['type'] == 'checkout.session.completed':
            order_id  = event['data']['object']['metadata']['order ID']
            order_status = event['data']['object']['payment_status']
            pay_status.append(order_status)
            order.append(order_id)
            print(order_status)
        if len(pay_status) == 0:
                order_obj = Paymets.objects.last()
                print(order_obj)
                order_obj.payment_satus = 'failed'
                order_obj.save()
        else:
                order_obj = Paymets.objects.last()
                order_obj.payment_satus = 'paid'
                order_obj.save()
        return HttpResponse('True', status = 200)

class Orders_detail(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.all()
    serializer_class = Orderserializer
    pagination_class = Pagination
    def list(self, request, *args, **kwargs):
        queryset = Order.objects.filter(user=request.user.id)
        serializer = Orderserializer(queryset, many=True)
        return Response(serializer.data)