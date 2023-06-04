from django.test import TestCase
from django.utils import timezone

from api.models import Mailing, Message, Client, Tag
from api.tasks import create_messages


class CreateMessagesTaskTestCase(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name='tag1')
        self.client1 = Client.objects.create(phone='79901234567', timezone='UTC')
        self.client2 = Client.objects.create(phone='79911234567', timezone='UTC')
        self.client2.tags.add(self.tag1)

        self.mailing_code = Mailing.objects.create(
            start_at=timezone.now() - timezone.timedelta(days=1),
            end_at=timezone.now() + timezone.timedelta(days=1),
            message_text='Message for 990 code',
            operator_code='990',
        )
        self.mailing_tag = Mailing.objects.create(
            start_at=timezone.now() - timezone.timedelta(days=1),
            end_at=timezone.now() + timezone.timedelta(days=1),
            message_text='Message for tag1 clients',
        )
        self.mailing_tag.tags.add(self.tag1)

        self.mailing_all = Mailing.objects.create(
            start_at=timezone.now() - timezone.timedelta(days=1),
            end_at=timezone.now() + timezone.timedelta(days=1),
            message_text='Message for all clients',
        )
        self.mailing_future = Mailing.objects.create(
            start_at=timezone.now() + timezone.timedelta(days=30),
            end_at=timezone.now() + timezone.timedelta(days=31),
            message_text='Message from future',
        )

    def test_create_messages_task(self):
        create_messages()

        expected_messages = [
            {'client': self.client1.id, 'mailing': self.mailing_code.id},
            {'client': self.client2.id, 'mailing': self.mailing_tag.id},
            {'client': self.client1.id, 'mailing': self.mailing_all.id},
            {'client': self.client2.id, 'mailing': self.mailing_all.id},
        ]
        actual_messages = list(Message.objects.all().values('client', 'mailing'))
        self.assertEqual(expected_messages, actual_messages)
        self.assertEqual(Message.objects.count(), 4)
