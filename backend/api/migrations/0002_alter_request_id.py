# Generated by Django 5.1.2 on 2024-10-26 10:50

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='id',
            field=models.UUIDField(default=uuid.UUID('ea168a8c-78b0-4758-9618-33c59c89f784'), editable=False, primary_key=True, serialize=False),
        ),
    ]
