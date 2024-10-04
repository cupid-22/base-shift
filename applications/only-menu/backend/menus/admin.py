from django.contrib import admin

from menus.models import (
    Menu, MenuItem, MenuItemDietaryRestriction, DietaryRestriction, MenuItemCategoryRelation, NutritionalInfo, Category,
    MenuItemRelation
)

admin.site.register(Menu)
admin.site.register(MenuItem)
admin.site.register(MenuItemDietaryRestriction)
admin.site.register(DietaryRestriction)
admin.site.register(MenuItemCategoryRelation)
admin.site.register(MenuItemRelation)
admin.site.register(NutritionalInfo)
admin.site.register(Category)
