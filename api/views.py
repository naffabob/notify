import logging

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import serializers
from .models import Mailing, Client, Tag

logger = logging.getLogger(__name__)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    basename = 'tag'


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = serializers.ClientSerializer
    basename = 'client'


class MailingViewSet(viewsets.ModelViewSet):
    queryset = Mailing.objects.all()
    serializer_class = serializers.MailingSerializer
    basename = 'mailing'

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
