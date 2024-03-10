from django.contrib.auth import get_user_model
from django.db import models

from utils.model_helpers import BaseModel


class Conversation(BaseModel):
    participants = models.ManyToManyField(to=get_user_model(), related_name="conversations")


class Message(BaseModel):
    conversation = models.ForeignKey(to=Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(to=get_user_model(), on_delete=models.SET_NULL, related_name="sent_messages")
    text = models.TextField()
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ("-timestamp",)

    def mark_as_read(self):
        self.read = True
        self.save()
