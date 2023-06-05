import requests
from django.utils import timezone
from rest_framework import status

from notify.celery import app
from notify.settings import PROBE_SERVER_TOKEN, PROBE_SERVER_URL
from .models import Mailing, Message, Client
import logging

logger = logging.getLogger(__name__)


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

        for message in messages:
            logger.info(f'message created: {message.log_id}')


@app.task
def handle_messages():
    messages = Message.objects.filter(status=Message.STATUS_NEW)

    for message in messages:
        send_message.delay(message.pk)
        logger.info(f'message ready to send: {message.log_id}')
    return len(messages)


@app.task
def send_message(pk: int):
    message = Message.objects.get(pk=pk)

    if message.status in (Message.STATUS_SENT, Message.STATUS_FAILED):
        logger.warning(f'message already handled: {message.log_id}')
        return

    if timezone.now() > message.mailing.end_at:
        message.status = Message.STATUS_FAILED
        message.save()
        logger.warning(f'message sending period expired: {message.log_id}')
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
        logger.warning('remote API server unreachable')
        return

    if response.status_code == status.HTTP_400_BAD_REQUEST:
        logger.warning(f'sending message {message.log_id} end with error: {response.status_code}')
        return

    if not response.ok:
        logger.warning(f'sending message {message.log_id} end with error')
        return

    message.status = Message.STATUS_SENT
    message.sent_at = timezone.now()
    message.save()
    logger.info(f'message sent: {message.log_id}')
