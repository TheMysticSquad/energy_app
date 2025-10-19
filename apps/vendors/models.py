from django.db import models

class Vendor(models.Model):
    vendor_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=150)
    base_url = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)

class VendorAuditLog(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=255)
    request_payload = models.JSONField(null=True, blank=True)
    response_payload = models.JSONField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
