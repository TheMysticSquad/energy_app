from django.db import models
from apps.consumers.models import Consumer
from apps.vendors.models import Vendor

class Meter(models.Model):
    meter_id = models.CharField(max_length=100, primary_key=True)
    consumer = models.ForeignKey(Consumer, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, default="INSTALLED")
    installed_on = models.DateTimeField(null=True, blank=True)

class MeterReading(models.Model):
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    kwh = models.DecimalField(max_digits=12, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)
