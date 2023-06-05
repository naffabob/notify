# Generated by Django 4.2.1 on 2023-06-04 20:24

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='log_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AddField(
            model_name='mailing',
            name='log_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AddField(
            model_name='message',
            name='log_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
