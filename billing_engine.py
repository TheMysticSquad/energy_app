import datetime
from decimal import Decimal
from database_manager import DatabaseManager
from prepaid_module_v2 import ConsumptionRecord  # Assuming you have this dataclass

class BillingEngine:
    def __init__(self):
        self.db = DatabaseManager()

    # ---------------------------------
    # DAILY BILLING PROCESS
    # ---------------------------------
    def run_daily_billing(self, billing_date=None):
        """
        Main job: Run daily deduction for all active consumers.
        """
        if not billing_date:
            billing_date = datetime.date.today()

        print(f"🚀 Starting daily billing job for {billing_date}")

        consumers = self.db.get_all_consumers()
        processed = 0
        failed = 0

        for consumer in consumers:
            try:
                if consumer.status != "Active":
                    continue

                tariff = self.db.get_tariff_plan(consumer.plan_id or "A1")

                # Simulate daily energy consumption from MDM or estimated logic
                kwh_used = self._fetch_daily_usage(consumer.consumer_id)

                if kwh_used == 0:
                    continue

                # --- Billing Logic ---
                record = self._calculate_daily_deduction(consumer, tariff, kwh_used)
                self.db.insert_consumption_record(record)
                self.db.update_consumer_balance(consumer.consumer_id, record.balance_after)

                processed += 1

            except Exception as e:
                print(f"⚠️ Error processing consumer {consumer.consumer_id}: {e}")
                failed += 1

        # Log job summary
        self._log_daily_job(billing_date, len(consumers), processed, failed)

        print(f"✅ Daily Billing Completed: {processed}/{len(consumers)} processed, {failed} failed.")

    # ---------------------------------
    # BILLING CALCULATION
    # ---------------------------------
    def _calculate_daily_deduction(self, consumer, tariff, kwh_used):
        """
        Calculate deduction and create a consumption record object.
        """
        energy_charge = Decimal(kwh_used) * Decimal(tariff.rate_per_kwh)
        fixed_charge = Decimal(tariff.fixed_charge_daily)
        subsidy_units = min(kwh_used, tariff.subsidy_units or 0)
        subsidy_amount = Decimal(subsidy_units) * Decimal(tariff.subsidy_rate)
        total_deduction = (energy_charge + fixed_charge) - subsidy_amount

        balance_before = Decimal(consumer.balance)
        balance_after = balance_before - total_deduction

        # Auto disconnection trigger logic (if balance is negative)
        if balance_after <= 0:
            consumer.status = "Disconnected"
            self.db.update_consumer_balance(consumer.consumer_id, 0.00)

        # Create consumption record
        record = ConsumptionRecord(
            consumer_id=consumer.consumer_id,
            timestamp=datetime.datetime.now(),
            kwh_consumed=kwh_used,
            subsidy_units=subsidy_units,
            energy_charge=energy_charge,
            fixed_charge=fixed_charge,
            total_deduction=total_deduction,
            balance_before=balance_before,
            balance_after=balance_after
        )

        return record

    # ---------------------------------
    # MONTHLY BILLING / INVOICE
    # ---------------------------------
    def run_monthly_invoice(self, month=None):
        """
        Generate monthly invoice summary for each consumer.
        """
        if not month:
            month = datetime.date.today().strftime("%Y-%m")

        print(f"📅 Generating monthly invoices for {month}")
        consumers = self.db.get_all_consumers()

        for consumer in consumers:
            try:
                # Fetch monthly consumption
                history = self.db.get_consumption_history(consumer.consumer_id)
                monthly_records = [r for r in history if r[0].strftime("%Y-%m") == month]

                if not monthly_records:
                    continue

                total_units = sum([float(r[1]) for r in monthly_records])
                total_energy_charge = sum([float(r[3]) for r in monthly_records])
                total_fixed_charge = sum([float(r[4]) for r in monthly_records])
                total_subsidy = sum([float(r[2]) for r in monthly_records])
                total_amount = sum([float(r[5]) for r in monthly_records])
                opening_balance = monthly_records[-1][6]
                closing_balance = monthly_records[0][7]

                # Insert invoice summary
                self.db._run_query("""
                    INSERT INTO invoices (consumer_id, billing_month, total_units, total_energy_charge, 
                        total_fixed_charge, total_subsidy, total_amount, opening_balance, closing_balance)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (consumer.consumer_id, month, total_units, total_energy_charge,
                      total_fixed_charge, total_subsidy, total_amount,
                      opening_balance, closing_balance))

            except Exception as e:
                print(f"⚠️ Error generating invoice for {consumer.consumer_id}: {e}")

        print(f"✅ Monthly invoices generated successfully for {month}")

    # ---------------------------------
    # RMS / MDM SYNC MOCK
    # ---------------------------------
    def sync_invoices_with_rms(self):
        """
        Sync unsynced invoices to RMS/MDM system (mock).
        """
        invoices = self.db._run_query("SELECT invoice_id, consumer_id, total_amount FROM invoices WHERE sync_status='Pending'", fetch=True)
        if not invoices:
            print("No pending invoices to sync.")
            return

        for inv in invoices:
            invoice_id, consumer_id, amount = inv
            try:
                # Here, you would call the external RMS/MDM API
                print(f"🔁 Syncing invoice {invoice_id} for {consumer_id} ...")
                # simulate success
                self.db._run_query("UPDATE invoices SET sync_status='Synced' WHERE invoice_id=%s", (invoice_id,))
            except Exception as e:
                print(f"❌ Sync failed for invoice {invoice_id}: {e}")
                self.db._run_query("UPDATE invoices SET sync_status='Failed' WHERE invoice_id=%s", (invoice_id,))

        print("✅ RMS/MDM sync completed.")

    # ---------------------------------
    # UTILITIES
    # ---------------------------------
    def _fetch_daily_usage(self, consumer_id):
        """
        Fetch or simulate daily kWh consumption (replace with real API later).
        """
        import random
        return round(random.uniform(2.5, 8.0), 3)  # Simulated 2.5 to 8 kWh daily usage

    def _log_daily_job(self, job_date, total, processed, failed):
        self.db._run_query("""
            INSERT INTO daily_billing_job_status (job_date, total_consumers, processed, failed, status, started_at, finished_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """, (job_date, total, processed, failed, 'Completed'))
