from django.contrib import admin
from django.contrib.admin import site

from .models import User, Employee, Request

# Register your models here.
site.register(User)
site.register(Employee)
site.register(Request)