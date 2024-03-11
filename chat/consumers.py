import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Conversation, Message
from .serializers import MessageSerializer


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # check if the conversation exists
        self.conversation = get_object_or_404(Conversation, id=self.room_name)

        # join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

    def receive(self, text_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        print(f"Received message: {message}")

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
            },
        )

    def chat_message(self, event):
        data = event
        print(event)
        print(data)

        self.send(
            text_data=json.dumps(
                {
                    "message": data["message"],
                }
            )
        )
