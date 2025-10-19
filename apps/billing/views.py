from rest_framework import viewsets
from .models import TariffPlan
from rest_framework import serializers

class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TariffPlan
        fields = '__all__'

class BillingViewSet(viewsets.ModelViewSet):
    queryset = TariffPlan.objects.all()
    serializer_class = BillingSerializer
