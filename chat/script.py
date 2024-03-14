from django.contrib.auth import get_user_model
from django.db.models import Count

users_with_sent_message_count = get_user_model().objects.annotate(sent_message_count=Count("sent_messages"))
print(users_with_sent_message_count)
user1 = get_user_model().objects.get(username="admin1")

print(users_with_sent_message_count.first().sent_message_count)
