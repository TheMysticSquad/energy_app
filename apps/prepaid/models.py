from django.db import models
from apps.consumers.models import Consumer

class PrepaidAccount(models.Model):
    consumer = models.OneToOneField(Consumer, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    low_balance_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=20)

class RechargeTransaction(models.Model):
    account = models.ForeignKey(PrepaidAccount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    voucher_code = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
