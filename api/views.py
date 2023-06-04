from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from . import serializers
from .models import Mailing, Client, Tag


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """
    • добавления нового клиента в справочник со всеми его атрибутами
    • обновления данных атрибутов клиента
    • удаления клиента из справочника
    """
    queryset = Client.objects.all()
    serializer_class = serializers.ClientSerializer


class MailingViewSet(viewsets.ModelViewSet):
    """
    • добавления новой рассылки со всеми её атрибутами
    • обновления атрибутов рассылки
    • удаления рассылки
    """
    queryset = Mailing.objects.all()
    serializer_class = serializers.MailingSerializer

    @action(detail=False, url_path='stats')
    def general_stats(self, request):
        mailings = Mailing.objects.all()
        serializer = serializers.MailingGeneralStatistics(mailings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_path='stats')
    def detail_stats(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        serializer = serializers.MailingDetailStatSerializer(mailing)
        return Response(serializer.data, status=status.HTTP_200_OK)
