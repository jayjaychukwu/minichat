from django.urls import path

from .views import ConversationAPIView, SendMessageAPIView, UpdateReadReceiptAPIView

urlpatterns = [
    path("conversation/", ConversationAPIView.as_view(), name="conversation"),
    path("send-message/", SendMessageAPIView.as_view(), name="send_message"),
    path("read-receipt/", UpdateReadReceiptAPIView.as_view(), name="update_read_receipt"),
]
