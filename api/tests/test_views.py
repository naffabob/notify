from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from api.models import Client, Tag, Mailing


class TagsAPITests(APITestCase):
    def setUp(self) -> None:
        self.tag1_data = {'name': 'tag1'}
        self.tag2_data = {'name': ''}
        self.tag3 = Tag.objects.create(name='tag3')

    def test_create_tag_with_apiclient(self):
        tag = APIClient()
        url = reverse('tag-list')
        response = tag.post(url, self.tag1_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 2)
        self.assertTrue(Tag.objects.filter(name='tag1').exists())

        response = tag.post(url, self.tag2_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Tag.objects.count(), 2)

    def test_get_tags_list(self):
        tag = APIClient()
        url = reverse('tag-list')
        response = tag.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class ClientAPITests(APITestCase):
    def setUp(self):
        self.CLIENT1_PHONE = '79100000001'
        self.CLIENT2_PHONE = '79100000002'
        self.TIMEZONE = 'UTC'

        self.tag1 = Tag.objects.create(name='tag1')

        self.client1 = Client.objects.create(phone=self.CLIENT1_PHONE, timezone=self.TIMEZONE)
        self.client2_data = {'phone': self.CLIENT2_PHONE, 'timezone': self.TIMEZONE, 'tags': [self.tag1.id]}
        self.wrong_client_data = [{'phone': '1234567890', 'timezone': 'UTC'}, {'phone': '79100000003', 'timezone': ''}]

    def test_create_client(self):
        url = reverse('client-list')
        response = self.client.post(url, self.client2_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], self.client2_data['phone'][1:4])
        self.assertTrue(Client.objects.filter(phone=self.CLIENT2_PHONE).exists())

        for data in self.wrong_client_data:
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Client.objects.count(), 2)

    def test_get_client_list(self):
        url = reverse('client-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_client_detail(self):
        url = reverse('client-detail', args=[self.client1.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone'], self.CLIENT1_PHONE)
        self.assertEqual(response.data['timezone'], self.TIMEZONE)
        self.assertEqual(len(response.data['tags']), 0)

    def test_update_client(self):
        url = reverse('client-detail', args=[self.client1.id])
        response = self.client.put(url, self.client2_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client1.refresh_from_db()
        self.assertEqual(self.client1.phone, self.CLIENT2_PHONE)

    def test_delete_client(self):
        url = reverse('client-detail', args=[self.client1.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Client.objects.filter(phone=self.CLIENT1_PHONE).exists())


class MailingAPITestCase(APITestCase):
    def setUp(self):
        day_ago = timezone.now() - timezone.timedelta(days=1)
        day_after = timezone.now() + timezone.timedelta(days=1)

        self.tag1 = Tag.objects.create(name='tag1')
        self.tag2 = Tag.objects.create(name='tag2')
        self.mailing1 = Mailing.objects.create(
            operator_code='123',
            start_at=day_ago,
            end_at=day_after,
            message_text='Test message 1'
        )
        self.mailing1.tags.add(self.tag1)

        self.mailing2_data = {
            'operator_code': '789',
            'start_at': day_ago,
            'end_at': day_after,
            'message_text': 'Test message 2',
            'tags': [self.tag1.id, self.tag2.id]
        }

    def test_create_mailing(self):
        url = reverse('mailing-list')
        response = self.client.post(url, self.mailing2_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Mailing.objects.count(), 2)
        mailing = Mailing.objects.get(id=response.data['id'])
        self.assertEqual(mailing.operator_code, '789')
        self.assertEqual(mailing.start_at, self.mailing2_data['start_at'])
        self.assertEqual(list(mailing.tags.all()), [self.tag1, self.tag2])

    def test_get_mailing_list(self):
        url = reverse('mailing-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_mailing(self):
        url = reverse('mailing-detail', args=[self.mailing1.id])
        response = self.client.put(url, self.mailing2_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mailing1.refresh_from_db()
        self.assertEqual(self.mailing1.operator_code, self.mailing2_data['operator_code'])
        self.assertEqual(self.mailing1.start_at, self.mailing2_data['start_at'])
        self.assertEqual(self.mailing1.tags.count(), 2)

    def test_delete_mailing(self):
        mailing = Mailing.objects.first()
        url = reverse('mailing-detail', args=[mailing.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Mailing.objects.count(), 0)
