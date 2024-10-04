from rest_framework import serializers
from .models import MenuItem, Menu, Category
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'MenuItem without Menu or Categories',
            summary='Create a MenuItem without optional fields',
            value={
                "name": "Burger",
                "description": "A delicious beef burger",
                "price": "9.99"
            },
            request_only=True  # Show in request examples
        ),
        OpenApiExample(
            'MenuItem with Menu and Categories',
            summary='Create a MenuItem with a Menu and Categories',
            value={
                "name": "Pizza",
                "description": "A large pepperoni pizza",
                "price": "12.99",
                "menu": 1,
                "categories": ["Fast Food", "Italian"]
            },
            request_only=True
        )
    ]
)
class MenuItemSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True
    )
    menu = serializers.PrimaryKeyRelatedField(
        queryset=Menu.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'menu', 'categories']

    def create(self, validated_data):
        categories_data = validated_data.pop('categories', None)
        menu_item = MenuItem.objects.create(**validated_data)

        if categories_data:
            categories = []
            for category_name in categories_data:
                category, created = Category.objects.get_or_create(name=category_name)
                categories.append(category)
            menu_item.categories.set(categories)

        return menu_item

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', None)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.menu = validated_data.get('menu', instance.menu)
        instance.save()

        if categories_data:
            categories = []
            for category_name in categories_data:
                category, created = Category.objects.get_or_create(name=category_name)
                categories.append(category)
            instance.categories.set(categories)

        return instance
