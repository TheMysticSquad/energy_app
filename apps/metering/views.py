from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Meter, MeterReading
from rest_framework import serializers

# Minimal serializers for the view to run without errors
class MeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = '__all__'

class MeterReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeterReading
        fields = ('timestamp', 'kwh') # Exclude meter field since it's passed in save()

class MeterViewSet(viewsets.ModelViewSet):
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer

    @action(detail=True, methods=["post"])
    def push_reading(self, request, pk=None):
        meter = self.get_object()
        serializer = MeterReadingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(meter=meter)
        return Response({"status":"ok"}, status=status.HTTP_201_CREATED)
