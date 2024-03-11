from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "text",
            "read",
            "created_at",
        ]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    participants = UserSerializer(many=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "participants",
            "messages",
        ]


class ConversationCreateSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        many=True,
        required=True,
    )

    class Meta:
        model = Conversation
        fields = ["participants"]


class UpdateReadReceiptSerializer(serializers.Serializer):
    message_id = serializers.IntegerField()


class SendMessageSerializer(serializers.Serializer):
    recipient_id = serializers.IntegerField()
    message = serializers.CharField()
