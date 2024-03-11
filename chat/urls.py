from django.urls import path

from .views import SendMessageAPIView, UpdateReadReceiptAPIView

urlpatterns = [
    path("send-message/", SendMessageAPIView.as_view(), name="send_message"),
    path("read-receipt/", UpdateReadReceiptAPIView.as_view(), name="update_read_receipt"),
]
