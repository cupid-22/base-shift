from django.db import models

from utils.models import BaseModel
from .menu import Menu


class MenuItem(BaseModel):
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True, null=True)
    sub_description = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    # Many-to-Many relationship with Category
    categories = models.ManyToManyField('Category', through='MenuItemCategoryRelation',
                                        related_name='menu_items', blank=True)

    def __str__(self):
        return self.name


# Intermediate model to represent additional fields in the Many-to-Many relationship
class MenuItemRelation(BaseModel):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text='Price specific to this menu')
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    is_special = models.BooleanField(default=False, help_text="Is this item a special or seasonal offering?")
    stock_quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ('menu', 'menu_item')

    def __str__(self):
        return f"{self.menu_item.name} in {self.menu.name}"


# Intermediate model to add additional data for the Many-to-Many relationship between MenuItem and Category
class MenuItemCategoryRelation(BaseModel):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('menu_item', 'category')

    def __str__(self):
        return f"{self.menu_item.name} in {self.category.name}"

# also with menu-menuitem and menuitem-categiry both of these are optional at creation and should not be enforced and can be added later, can you modify the serializer and modek to do so?
