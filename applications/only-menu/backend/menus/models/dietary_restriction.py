from django.db import models

from menus.models.nutritional_info import DietaryRestriction
from utils.models import BaseModel


class MenuItemDietaryRestriction(BaseModel):
    menu_item = models.ForeignKey('MenuItem', related_name='dietary_restrictions', on_delete=models.CASCADE)
    dietary_restriction = models.ForeignKey(DietaryRestriction, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('menu_item', 'dietary_restriction')
