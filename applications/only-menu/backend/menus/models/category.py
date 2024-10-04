from django.db import models

from utils.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
