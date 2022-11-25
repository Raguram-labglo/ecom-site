from rest_framework import serializers
from api.models import (Product, 
                        Cart, 
                        Order, 
                        Wish,
                        User,
                        )

class RegisterSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create_superuser(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()
        return user


class Loginserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class Productserializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title', 'image', 'name', 'brand', 'price', 'in_stocks']

    
class Cartserializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'price', 'quantity', 'status', 'is_active']
        read_only_fields = ('user', 'price','is_active')


class Orderserializer(serializers.ModelSerializer):
    #order_items = Cartserializer()
    class Meta:
        model = Order
        fields = ['user', 'order_items', 'order_status', 'order_price', 'tax_price', 'order_time']

class Wishlistserializer(serializers.ModelSerializer):
    class Meta:
        model = Wish
        fields = ['user', 'favourite']
        read_only_fields = ('user',)