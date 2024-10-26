from rest_framework import serializers

from .models import User, Employee, Request


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'agreement', 'phone', 'address')


class EmployeeSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Employee
        fields = ('id', 'email', 'password', 'is_admin')


class RequestSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Request
        fields = ('id', 'user_id', 'request', 'ready')