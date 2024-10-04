from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .viewset import MenuViewSet, MenuItemViewSet

router = DefaultRouter()
router.register(r'menus', MenuViewSet)
router.register(r'menu-items', MenuItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
