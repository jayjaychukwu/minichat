from typing import Any

from django.contrib.humanize.templatetags import humanize
from django.db import models
from django.utils.translation import gettext as _


class BaseModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    created_at = models.DateTimeField(_("date created"), auto_now_add=True, blank=True)

    class Meta:
        abstract = True

    def time_updated(self):
        return f"{humanize.naturaltime(self.updated_at)} - {self.updated_at.date()}"

    def time_created(self):
        return f"{humanize.naturaltime(self.created_at)} -  {self.created_at.date()}"
