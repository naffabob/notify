import uuid

from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Client(models.Model):
    tags = models.ManyToManyField('Tag', blank=True)
    phone = models.CharField(max_length=11, unique=True)
    timezone = models.CharField(max_length=50)
    log_id = models.UUIDField(max_length=50, default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.phone


class Mailing(models.Model):
    operator_code = models.CharField(max_length=3, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    message_text = models.TextField()
    log_id = models.UUIDField(max_length=50, default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.message_text


class Message(models.Model):
    STATUS_NEW = 'new'
    STATUS_FAILED = 'failed'
    STATUS_SENT = 'sent'

    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_SENT, 'Sent'),
    ]

    created_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, default=None, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, default='new')
    mailing = models.ForeignKey('Mailing', on_delete=models.CASCADE, related_name='messages')
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='messages')
    log_id = models.UUIDField(max_length=50, default=uuid.uuid4, editable=False, unique=True)
