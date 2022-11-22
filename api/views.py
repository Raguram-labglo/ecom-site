from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework import viewsets

from api.models import (Product, 
                        Cart, 
                        Order, 
                        Wish,
                        User,
                        )
from api.serializers import (RegisterSerializers,
                            Loginserializer,
                            Productserializer,
                            Cartserializer,
                            Orderserializer)

from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token


class LoginView(generics.GenericAPIView):

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


class LoginView(generics.GenericAPIView):

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


class Productlist(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = Productserializer
    pagination_class = Pagination


class Usercart(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = Cartserializer
    pagination_class = Pagination
    #http_method_names = ['patch', 'put', 'get', 'post']

    def perform_create(self, serializer):
        
        serializer.save(user=self.request.user)

    
class Customer_detail(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = Loginserializer

