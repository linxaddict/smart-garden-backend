from django.urls import path, include
from rest_framework import routers

from . import views
from .views import ControlledCircuitView, CircuitScheduleView, CircuitOneTimeActivationView, acme_challenge

router = routers.DefaultRouter()
router.register(r'circuits', views.CircuitViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/circuits/mine', ControlledCircuitView.as_view(), name='mine-circuit'),
    path('api/circuits/<int:circuit_id>/schedule', CircuitScheduleView.as_view(), name='circuit-schedule'),
    path('api/circuits/<int:circuit_id>/one-time-activations', CircuitOneTimeActivationView.as_view(),
         name='circuit-one-time-activations'),
    path(".well-known/acme-challenge/AN2gxTItG3P8FliBhGOTJoaftesMcoHGjW3ZLyk3Qq4", acme_challenge),
    path('', views.index, name='index'),
]
