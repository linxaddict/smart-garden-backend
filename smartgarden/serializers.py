from rest_framework import serializers

from smartgarden.models import User, Circuit, Activation, ScheduledOneTimeActivation, ScheduledActivation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'user_type']


class ActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activation
        fields = ['amount', 'timestamp']


class ScheduledOneTimeActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledOneTimeActivation
        fields = ['amount', 'timestamp']


class ScheduledActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledActivation
        fields = ['active', 'amount', 'time']


class CircuitSerializer(serializers.ModelSerializer):
    today_one_time_activations = ScheduledOneTimeActivationSerializer(source='one_time_activations', many=True)
    schedule = ScheduledActivationSerializer(many=True)

    class Meta:
        model = Circuit
        fields = ['id', 'name', 'active', 'healthy', 'today_one_time_activations', 'schedule']
