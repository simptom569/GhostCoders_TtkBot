from django.contrib.auth.hashers import make_password

from rest_framework import serializers

from .models import User, Employee, Request, Intent, Subintent, Phrase, EmailRecipient


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'agreement', 'phone', 'address')


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'email', 'password', 'is_admin']  # Include other fields as needed

    def create(self, validated_data):
        # Hash the password
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class RequestSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Request
        fields = ('id', 'user_id', 'request', 'ready')


class IntentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Intent
        fields = ('id', 'name', 'answer')
        

class SubintentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Subintent
        fields = ('id', 'name', 'intent', 'answer')


class PhraseSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Phrase
        fields = ('id', 'name', 'intent', 'subintent')


class EmailRecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailRecipient
        fields = ['id', 'email']