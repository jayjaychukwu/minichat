from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import permissions, serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationList(GenericAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        conversations = user.conversations.all()
        serializer = self.get_serializer(conversations, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        participants = request.data.get("participants")
        conversation = Conversation.objects.create()
        conversation.participants.add(*participants)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConversationDetail(GenericAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        conversation = self.get_object()
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)


class StartConversation(GenericAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        participants = request.data.get("participants")
        conversation = Conversation.objects.create()
        conversation.participants.add(*participants)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageList(GenericAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs["conversation_id"]
        return Message.objects.filter(conversation_id=conversation_id)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageDetail(GenericAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        message = self.get_object()
        serializer = self.get_serializer(message)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        message = self.get_object()
        serializer = self.get_serializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        message = self.get_object()
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateReadReceiptAPIView(APIView):
    def post(self, request):
        try:
            message_id = request.data.get("message_id")
            message = Message.objects.get(id=message_id)
            message.read = True
            message.save()
            return Response(
                {
                    "message": "read receipt updated",
                },
                status.HTTP_200_OK,
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


class SendMessageAPIView(APIView):
    permissions = (permissions.IsAuthenticated,)

    def post(self, request):
        sender = request.user
        recipient_id = request.data.get("recipient_id")
        message_text = request.data.get("message")

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

    # def post(self, request):
    #     serializer = MessageSerializer(data=request.data)
    #     try:
    #         serializer.is_valid(raise_exception=True)
    #     except serializers.ValidationError as err:
    #         return Response(
    #             serializer.errors,
    #             status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         )

    #     message = serializer.save()
    #     self.send_message_through_websocket(message)

    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

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
