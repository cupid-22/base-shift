from django.db import models
from utils.models import BaseModel


class Restaurant(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    contact_info = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    opening_hours = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name
