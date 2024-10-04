from django.db import models

from utils.models import BaseModel


class DietaryRestriction(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class NutritionalInfo(BaseModel):
    menu_item = models.OneToOneField('MenuItem', on_delete=models.CASCADE, related_name='nutritional_info')
    calories = models.PositiveIntegerField()
    protein = models.DecimalField(max_digits=5, decimal_places=2)  # Protein in grams
    fat = models.DecimalField(max_digits=5, decimal_places=2)  # Fat in grams
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=2)  # Carbs in grams
    fiber = models.DecimalField(max_digits=5, decimal_places=2)  # Fiber in grams
    sugar = models.DecimalField(max_digits=5, decimal_places=2)  # Sugar in grams
    sodium = models.DecimalField(max_digits=5, decimal_places=2)  # Sodium in milligrams

    def __str__(self):
        return f'Nutritional Info for {self.menu_item.name}'
