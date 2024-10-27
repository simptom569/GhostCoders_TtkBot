from django.contrib import admin
from django.contrib.admin import site

from .models import User, Employee, Request, Intent, Subintent, Phrase, EmailRecipient

# Register your models here.
site.register(User)
site.register(Employee)
site.register(Request)

admin.site.register(Intent)
admin.site.register(Subintent)
admin.site.register(Phrase)
admin.site.register(EmailRecipient)
