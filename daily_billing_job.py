# daily_billing_job.py
from billing_engine import BillingEngine
from random import uniform

def simulate_daily_consumption(consumer):
    """
    Simulate daily consumption in kWh for testing.
    You can later replace this with smart meter input.
    """
    return round(uniform(1.5, 6.0), 2)  # Example: 1.5–6.0 kWh per day

if __name__ == "__main__":
    billing_engine = BillingEngine()
    billing_engine.process_daily_billing(simulated_consumption_fn=simulate_daily_consumption)

    # Optional: Generate invoices on 1st of month
    from datetime import datetime
    if datetime.now().day == 1:
        billing_engine.generate_monthly_invoices()
