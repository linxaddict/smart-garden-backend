from rest_framework import serializers

from smartgarden.models import User, Circuit, Activation, ScheduledOneTimeActivation, ScheduledActivation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'user_type']


class ActivationSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S')

    class Meta:
        model = Activation
        fields = ['amount', 'timestamp']


class ScheduledOneTimeActivationSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S')

    class Meta:
        model = ScheduledOneTimeActivation
        fields = ['amount', 'timestamp']


class ScheduledActivationSerializer(serializers.ModelSerializer):
    time = serializers.TimeField(format='%H:%M:%S')

    class Meta:
        model = ScheduledActivation
        fields = ['active', 'amount', 'time']


class CircuitSerializer(serializers.ModelSerializer):
    one_time_activation = ScheduledOneTimeActivationSerializer()
    schedule = ScheduledActivationSerializer(many=True)

    class Meta:
        model = Circuit
        fields = ['id', 'name', 'active', 'healthy', 'one_time_activation', 'schedule']
