from django.db import models
from apps.consumers.models import Consumer

class TariffPlan(models.Model):
    plan_id = models.CharField(max_length=20, primary_key=True)
    rate_per_kwh = models.DecimalField(max_digits=10, decimal_places=4)
    fixed_charge_daily = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subsidy_units = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    subsidy_rate = models.DecimalField(max_digits=10, decimal_places=4, default=0)

class ConsumptionRecord(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    kwh_consumed = models.DecimalField(max_digits=12, decimal_places=4)
    energy_charge = models.DecimalField(max_digits=12, decimal_places=2)
    fixed_charge = models.DecimalField(max_digits=12, decimal_places=2)
    total_deduction = models.DecimalField(max_digits=12, decimal_places=2)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
