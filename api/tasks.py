import requests
from django.utils import timezone
from rest_framework import status

from notify.celery import app
from notify.settings import PROBE_SERVER_TOKEN, PROBE_SERVER_URL
from .models import Mailing, Message, Client


@app.task
def create_messages():
    actual_date_mailings = Mailing.objects.filter(start_at__lte=timezone.now(), end_at__gte=timezone.now())

    for mailing in actual_date_mailings:

        # Получаем список ID клиентов, для которых еще не созданы сообщения в рамках данной рассылки
        exists_message_client_ids = Message.objects.filter(
            mailing=mailing
        ).values_list('client__id', flat=True).distinct()

        clients = Client.objects.all().exclude(pk__in=exists_message_client_ids)

        if mailing.operator_code:
            clients = clients.filter(phone__startswith=f'7{mailing.operator_code}')
        if mailing.tags.count():
            clients = clients.filter(tags__in=mailing.tags.all())

        messages = []
        for client in clients:
            message = Message(
                created_at=timezone.now(),
                mailing=mailing,
                client=client,
            )
            messages.append(message)
        Message.objects.bulk_create(messages)


@app.task
def handle_messages():
    messages = Message.objects.filter(status=Message.NEW_STATUS)
    messages_ids = messages.values_list('id', flat=True)

    for message_id in messages_ids:
        send_message.delay(message_id)
    return len(messages_ids)


@app.task
def send_message(pk: int):
    message = Message.objects.get(pk=pk)

    if message.status in (Message.SENT_STATUS, Message.FAILED_STATUS):
        return

    if timezone.now() > message.mailing.end_at:
        message.status = Message.FAILED_STATUS
        message.save()
        return

    json = {
        "id": message.id,
        "phone": message.client.phone,
        "text": message.mailing.message_text,
    }

    try:
        response = requests.post(
            url=f'{PROBE_SERVER_URL}{message.pk}',
            headers={'Authorization': f'Bearer {PROBE_SERVER_TOKEN}'},
            json=json,
        )
    except requests.exceptions.ConnectionError:
        return

    if response.status_code == status.HTTP_400_BAD_REQUEST:
        return

    if not response.ok:
        return

    message.status = Message.SENT_STATUS
    message.sent_at = timezone.now()
    message.save()
