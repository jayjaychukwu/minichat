from django.contrib import admin

from .models import Conversation, Message


class MessageAdmin(admin.ModelAdmin):
    pass


class ConversationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Message, MessageAdmin)
admin.site.register(Conversation, ConversationAdmin)
