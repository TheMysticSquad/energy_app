from django.db import models

class Consumer(models.Model):
    consumer_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("DISCONNECTED", "Disconnected"),
        ("POSTPAID", "Postpaid"),
        ("SUSPENDED", "Suspended"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.consumer_id} - {self.name}"
