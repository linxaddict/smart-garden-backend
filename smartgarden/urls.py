from django.urls import path, include
from rest_framework import routers

from . import views
from .views import ControlledCircuit

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'circuits', views.CircuitViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/circuits/mine', ControlledCircuit.as_view(), name='mine-circuit'),
    path('', views.index, name='index'),
]
