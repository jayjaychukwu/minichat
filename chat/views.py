from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import permissions, serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation, Message
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageSerializer,
    SendMessageSerializer,
    UpdateReadReceiptSerializer,
)


class ConversationAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_classes = {
        "GET": ConversationSerializer,
        "POST": ConversationCreateSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.request.method)

    def get(self, request, *args, **kwargs):
        user = request.user
        conversations = user.conversations.all()
        serializer = self.get_serializer_class()(conversations, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        seriliazer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            participants = request.data.get("participants")
            conversation = Conversation.objects.create()
            conversation.participants.add(*participants)
            serializer = ConversationSerializer(conversation)
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)


class ConversationDetail(GenericAPIView):
    serializer_class = ConversationSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        conversation_id = kwargs.get("id")  # Retrieve conversation ID from URL parameter
        try:
            conversation = Conversation.objects.get(id=conversation_id)  # Retrieve conversation object
        except Conversation.DoesNotExist:
            return Response(
                {"message": "conversation not found"},
                status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(conversation)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class UpdateReadReceiptAPIView(GenericAPIView):
    serializer_class = UpdateReadReceiptSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            message_id = serializer.validated_data.get("message_id")
            message = Message.objects.get(id=message_id)

            if message.read:
                return Response(
                    {
                        "message": "marked as read already",
                    },
                    status.HTTP_200_OK,
                )

            if (user != message.sender) and (user in message.conversation.participants.all()):
                message.mark_as_read()

                return Response(
                    {
                        "message": "read receipt updated",
                    },
                    status.HTTP_200_OK,
                )

            return Response(
                {
                    "message": "not read",
                },
                status.HTTP_200_OK,
            )
        except serializers.ValidationError:
            return Response(
                serializer.errors,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Message.DoesNotExist:
            return Response(
                {
                    "message": "message not found",
                },
                status.HTTP_400_BAD_REQUEST,
            )
        except Exception as err:
            return Response(
                {
                    "message": "something went wrong",
                    "error": str(err),
                },
                status.HTTP_400_BAD_REQUEST,
            )


class SendMessageAPIView(GenericAPIView):
    serializer_class = SendMessageSerializer
    permissions = (permissions.IsAuthenticated,)

    def post(self, request):
        sender = request.user
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as err:
            return Response(
                serializer.errors,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        recipient_id = serializer.validated_data.get("recipient_id")
        message_text = serializer.validated_data.get("message")

        conversation = Conversation.get_or_create_conversation(sender=sender, recipient_id=recipient_id)

        message = Message.objects.create(
            sender=sender,
            conversation=conversation,
            text=message_text,
        )

        serializer = MessageSerializer(message)

        self.send_message_through_websocket(message)

        return Response(
            serializer.data,
            status.HTTP_201_CREATED,
        )

    def send_message_through_websocket(self, message: Message):
        channel_layer = get_channel_layer()
        room_name = f"chat_{message.conversation.id}"
        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                "type": "chat_message",
                "message": message.text,
            },
        )
