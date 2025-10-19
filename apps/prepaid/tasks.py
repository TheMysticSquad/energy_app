from celery import shared_task
from django.utils import timezone
from apps.billing.models import ConsumptionRecord
from apps.prepaid.models import PrepaidAccount

@shared_task
def run_daily_prepaid_billing(billing_date=None):
    # NOTE: This is a NAIVE implementation stub for demonstration.
    # A real billing engine would be much more complex.
    billing_date = billing_date or timezone.now().date()
    log = []

    for acct in PrepaidAccount.objects.select_related("consumer"):
        # compute today's consumption (simplified)
        recs = ConsumptionRecord.objects.filter(consumer=acct.consumer, timestamp__date=billing_date)
        total_kwh = sum([float(r.kwh_consumed) for r in recs])

        # Simplified deduction logic (e.g., $0.50 per KWH)
        deduction = total_kwh * 0.50 # Replace with real tariff calculation

        acct.balance -= deduction
        acct.save(update_fields=['balance'])

        log.append(f"Consumer {acct.consumer.consumer_id}: Consumed {total_kwh:.2f} kWh, Deducted {deduction:.2f}. New Balance: {acct.balance:.2f}")

    return {"status": "done", "log": log}
