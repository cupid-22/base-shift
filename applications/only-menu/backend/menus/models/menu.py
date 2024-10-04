from django.db import models

from restaurants.models import Restaurant
from utils.models import BaseModel


class Menu(BaseModel):
    name = models.CharField(max_length=100)
    restaurant = models.ForeignKey(Restaurant, related_name='menus', on_delete=models.CASCADE)
    total_items = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-Many relationship with MenuItem
    items = models.ManyToManyField('MenuItem', through='MenuItemRelation', related_name='menu', blank=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
