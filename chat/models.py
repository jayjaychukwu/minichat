from django.contrib.auth import get_user_model
from django.db import models

from utils.model_helpers import BaseModel


class Conversation(BaseModel):
    participants = models.ManyToManyField(to=get_user_model(), related_name="conversations")

    @classmethod
    def get_or_create_conversation(cls, sender, recipient_id):
        try:
            recipient = get_user_model().objects.get(id=recipient_id)
        except get_user_model().DoesNotExist:
            raise ValueError("this user does not exist")

        # check if a conversation already exists
        conversation = cls.objects.filter(participants=sender).filter(participants=recipient)

        if conversation.exists():
            return conversation.first()
        else:
            new_conversation = cls.objects.create()
            new_conversation.participants.add(sender, recipient)
            return new_conversation


class Message(BaseModel):
    conversation = models.ForeignKey(to=Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.SET_NULL,
        related_name="sent_messages",
        null=True,
    )
    text = models.TextField()
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)

    def mark_as_read(self):
        """
        update a message instance to read.
        """
        self.read = True
        self.save()
