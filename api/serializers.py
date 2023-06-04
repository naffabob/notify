import re

from rest_framework import serializers

from .models import Client, Mailing, Message, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class ClientSerializer(serializers.ModelSerializer):
    code = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ('id', 'tags', 'phone', 'timezone', 'code')

    def get_code(self, obj):
        return obj.phone[1:4]

    def validate_phone(self, value):
        if not re.match(r"^7\d{10}$", value):
            raise serializers.ValidationError("Phone number should be in format 7XXXXXXXXXX")
        return value


class MailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class MessageStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'created_at', 'sent_at', 'status', 'client_id')


class MailingGeneralStatistics(MailingSerializer):
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Mailing
        fields = ('id', 'stats')

    def get_stats(self, obj):
        stats = {
            "new_messages": Message.objects.filter(mailing=obj.pk, status=Message.NEW_STATUS).count(),
            "failed_messages": Message.objects.filter(mailing=obj.pk, status=Message.FAILED_STATUS).count(),
            "succeed_messages": Message.objects.filter(mailing=obj.pk, status=Message.SENT_STATUS).count()
        }
        return stats


class MailingDetailStatSerializer(serializers.ModelSerializer):
    messages = MessageStatSerializer(many=True)

    class Meta:
        model = Mailing
        fields = ('id', 'messages')
