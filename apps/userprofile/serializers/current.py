from rest_framework import serializers, exceptions
from fcm_django.models import FCMDevice


class FCMDeviceSerializer(serializers.ModelSerializer):
    """FCM Device model serializer"""
    class Meta:
        model = FCMDevice
        fields = ('id', 'name', 'registration_id', 'device_id',
                  'active', 'date_created', 'type')
        read_only_fields = ('id', 'date_created',)
        extra_kwargs = {'active': {'default': True}}

    def validate(self, attrs):
        regid = attrs.get('registration_id')
        dtype = attrs.get('type')
        if regid and dtype and self.Meta.model.objects.filter(
                registration_id=regid).exclude(type=dtype).count():
            raise exceptions.ValidationError(
                {'registration_id': 'This field must be unique.'})
        return attrs

    def __init__(self, *args, **kwargs):
        super(FCMDeviceSerializer, self).__init__(*args, **kwargs)
        self.fields['type'].help_text = (
            'Should be one of ["%s"]' %
            '", "'.join([i for i in self.fields['type'].choices]))

    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_anonymous:
            validated_data['user'] = user
        device = FCMDevice.objects.create(**validated_data)
        return device

    def update(self, instance, validated_data):

        user = self.context['request'].user
        if not user.is_anonymous:
            instance.user = user
            instance.save()
        else:
            instance.user = None
            instance.save()
        return instance
