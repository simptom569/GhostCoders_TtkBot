# Generated by Django 5.1.2 on 2024-10-26 11:41

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_request_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='id',
            field=models.UUIDField(default=uuid.UUID('bdad9c20-167e-44dc-9a09-f3648e24612b'), editable=False, primary_key=True, serialize=False),
        ),
    ]
