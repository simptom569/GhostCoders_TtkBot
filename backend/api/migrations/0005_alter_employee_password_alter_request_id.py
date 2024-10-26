# Generated by Django 5.1.2 on 2024-10-26 13:52

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_request_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='password',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='request',
            name='id',
            field=models.UUIDField(default=uuid.UUID('b3144074-5f07-49fa-b891-188257ff1ba4'), editable=False, primary_key=True, serialize=False),
        ),
    ]
