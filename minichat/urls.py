from django.contrib import admin
from django.urls import include, path

from chat.consumers import ChatConsumer

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("chat/", include("chat.urls")),
]
