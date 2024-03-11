from rest_framework import serializers

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "text",
            "created_at",
        ]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "participants",
            "messages",
        ]


class UpdateReadReceiptSerializer(serializers.Serializer):
    message_id = serializers.IntegerField()


class SendMessageSerializer(serializers.Serializer):
    recipient_id = serializers.IntegerField()
    message = serializers.CharField()