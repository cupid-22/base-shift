from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .viewset import RestaurantViewSet

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
