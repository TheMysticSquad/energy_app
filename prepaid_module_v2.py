# prepaid_module_v2.py - Prepaid Module Logic

from datetime import datetime
from typing import List

# -----------------------------
# Data Models
# -----------------------------
class ConsumptionRecord:
    def __init__(self, timestamp, kwh_consumed, subsidy_units=0, energy_charge=0, fixed_charge=0, total_deduction=0, balance_before=0, balance_after=0):
        self.timestamp = timestamp
        self.kwh_consumed = kwh_consumed
        self.subsidy_units = subsidy_units
        self.energy_charge = energy_charge
        self.fixed_charge = fixed_charge
        self.total_deduction = total_deduction
        self.balance_before = balance_before
        self.balance_after = balance_after

class RechargeTransaction:
    def __init__(self, amount, timestamp=None, voucher_code=None, status="SUCCESS"):
        self.amount = amount
        self.timestamp = timestamp or datetime.now()
        self.voucher_code = voucher_code
        self.status = status

class Alert:
    def __init__(self, timestamp, alert_type, message):
        self.timestamp = timestamp
        self.alert_type = alert_type
        self.message = message

# -----------------------------
# Tariff Plan
# -----------------------------
class TariffPlan:
    def __init__(self, plan_id, rate_per_kwh, fixed_charge_daily=0.0, low_balance_threshold=50.0, subsidy_units=0, subsidy_rate=0.0):
        self.plan_id = plan_id
        self.rate_per_kwh = rate_per_kwh
        self.fixed_charge_daily = fixed_charge_daily
        self.low_balance_threshold = low_balance_threshold
        self.subsidy_units = subsidy_units
        self.subsidy_rate = subsidy_rate

# -----------------------------
# Billing Logic Class
# -----------------------------
class BillingLogic:
    """
    Handles all billing calculations: consumption, subsidy, fixed charge, total deduction.
    """
    def __init__(self, consumer):
        self.consumer = consumer

    def process_consumption(self, kwh_used, tariff: TariffPlan, timestamp=None):
        """
        Process a consumption record for a consumer.
        If timestamp is provided, use it; otherwise, use current time.
        """
        if timestamp is None:
            timestamp = datetime.now()
        balance_before = self.consumer.balance

        # Subsidy / free units calculation
        subsidy_units = min(kwh_used, tariff.subsidy_units)
        non_subsidy_units = kwh_used - subsidy_units
        energy_charge_subsidy = subsidy_units * tariff.rate_per_kwh * (1 - tariff.subsidy_rate)
        energy_charge_normal = non_subsidy_units * tariff.rate_per_kwh
        energy_charge_total = energy_charge_subsidy + energy_charge_normal

        fixed_charge = tariff.fixed_charge_daily
        total_deduction = energy_charge_total + fixed_charge
        balance_after = balance_before - total_deduction
        self.consumer.balance = balance_after

        # Record consumption
        self.consumer.consumption_records.append(
            ConsumptionRecord(
                timestamp, kwh_used, subsidy_units, energy_charge_total,
                fixed_charge, total_deduction, balance_before, balance_after
            )
        )

        # Low balance alert
        if self.consumer.balance <= tariff.low_balance_threshold:
            self.consumer.alerts.append(Alert(timestamp, "LOW_BALANCE", f"Low balance! ₹{self.consumer.balance:.2f}"))

        # Disconnection
        if self.consumer.balance <= 0 and self.consumer.status != "DISCONNECTED":
            self.consumer.status = "DISCONNECTED"
            print(f"[{timestamp}] Consumer {self.consumer.consumer_id} DISCONNECTED due to zero balance.")

    def recharge(self, amount, voucher_code=None):
        timestamp = datetime.now()
        self.consumer.balance += amount
        self.consumer.recharges.append(RechargeTransaction(amount, timestamp, voucher_code))
        if self.consumer.status == "DISCONNECTED" and self.consumer.balance > 0:
            self.consumer.status = "ACTIVE"
            print(f"[{timestamp}] Consumer {self.consumer.consumer_id} RECONNECTED after recharge.")

# -----------------------------
# Consumer Class
# -----------------------------
class Consumer:
    """
    Represents a consumer. Holds details and allows attribute updates.
    """
    def __init__(self, consumer_id, name, address, phone, balance=0.0, status="ACTIVE"):
        self.consumer_id = consumer_id
        self.name = name
        self.address = address
        self.phone = phone
        self.balance = balance
        self.status = status
        self.consumption_records: List[ConsumptionRecord] = []
        self.recharges: List[RechargeTransaction] = []
        self.alerts: List[Alert] = []
        self.billing = BillingLogic(self)  # Link billing logic

    def update_attribute(self, attr, value):
        if hasattr(self, attr):
            setattr(self, attr, value)
            print(f"Consumer {self.consumer_id} attribute '{attr}' updated to {value}")
        else:
            print(f"Attribute '{attr}' not found for Consumer {self.consumer_id}")

    def send_alerts(self):
        for alert in self.alerts:
            print(f"[ALERT] {alert.timestamp} - {alert.message}")
        self.alerts.clear()

    def generate_daily_billing_sheet(self):
        print(f"\n=== Daily Billing Sheet for Consumer {self.consumer_id} - {self.name} ===")
        print(f"{'Date':<12}{'KWh Used':<10}{'Subsidy Units':<15}{'Energy Charge':<15}{'Fixed Charge':<15}{'Total Deduction':<18}{'Balance Before':<15}{'Balance After':<15}{'Status':<12}")
        for rec in self.consumption_records:
            print(f"{rec.timestamp.strftime('%Y-%m-%d'):<12}{rec.kwh_consumed:<10}{rec.subsidy_units:<15}{rec.energy_charge:<15.2f}{rec.fixed_charge:<15.2f}{rec.total_deduction:<18.2f}{rec.balance_before:<15.2f}{rec.balance_after:<15.2f}{self.status:<12}")
