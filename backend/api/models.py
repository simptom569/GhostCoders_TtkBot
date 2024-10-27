from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from uuid import uuid4


class EmployeeManager(BaseUserManager):
    def create_user(self, email, password=None, is_admin=False, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, is_admin=is_admin, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, is_admin=True, **extra_fields)


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    agreement = models.SmallIntegerField(blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    address = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.id)


class Employee(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_admin = models.BooleanField()
    
    objects = EmployeeManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    @property
    def is_staff(self):
        return self.is_admin


class Request(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    request = models.TextField()
    ready = models.BooleanField()


class Intent(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)  # Имя намерения
    answer = models.TextField()  # Ответ, связанный с намерением
    min_confidence = models.FloatField(default=0.12)  # Минимальный коэффициент уверенности для намерения

    def __str__(self):
        return self.name


class Subintent(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)  # Имя поднамерения
    intent = models.ForeignKey(Intent, related_name='subintents', on_delete=models.CASCADE)  # Связь с основным намерением
    answer = models.TextField()  # Ответ, связанный с поднамерением
    min_confidence = models.FloatField(default=0.42)  # Минимальный коэффициент уверенности для поднамерения

    class Meta:
        unique_together = ('name', 'intent')  # Обеспечиваем уникальность имени поднамерения для каждого намерения

    def __str__(self):
        return f"{self.name} (поднамерение для {self.intent.name})"


class Phrase(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField()  # Текст фразы
    intent = models.ForeignKey(Intent, related_name='phrases', on_delete=models.CASCADE, null=True, blank=True)  # Связь с намерением
    subintent = models.ForeignKey(Subintent, related_name='phrases', on_delete=models.CASCADE, null=True, blank=True)  # Связь с поднамерением

    def __str__(self):
        return self.text
    

class EmailRecipient(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email