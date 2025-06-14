import json
import os
import random
import time
from datetime import datetime, timedelta

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, PendingRollbackError

# --- Configuration ---
DATABASE_URL = "mysql+pymysql://avnadmin:AVNS_skZtmn9k8mHNYHMTSxf@mysql-26219722-abhinandanroy165-e599.l.aivencloud.com:20585/defaultdb?"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

BATCH_SIZE = 30
DAILY_SECTION_LIMIT = 10 # Number of sections to process each day

# --- Helper Functions ---

def get_current_month_year():
    """Returns the current month (e.g., 'Jun') and year (e.g., 2025)."""
    today = datetime.today()
    return today.strftime('%b'), today.year

def chunked(iterable, size):
    """Yields successive 'size'-sized chunks from iterable."""
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]

def execute_batch(connection, query, data, table_name):
    """Executes a batch insert with retry logic."""
    if not data:
        print(f"[{table_name}] No data to insert.")
        return

    for i, batch in enumerate(chunked(data, BATCH_SIZE)):
        retry_attempted = False
        while True:
            try:
                connection.execute(text(query), batch)
                connection.commit()
                print(f"[{table_name}] Inserted batch {i*BATCH_SIZE} to {(i+1)*BATCH_SIZE - 1} of {len(data)}.")
                break
            except (OperationalError, PendingRollbackError) as e:
                print(f"Error inserting into {table_name}: {e}")
                print("Rolling back and waiting to retry...")
                try:
                    connection.rollback()
                except:
                    pass # Rollback might fail if connection is already bad
                if not retry_attempted:
                    retry_attempted = True
                    time.sleep(12) # Wait longer on first retry
                else:
                    # If second retry fails, re-raise the exception
                    print("Second retry failed. Aborting batch.")
                    raise e
            except Exception as e:
                print(f"Non-retryable error inserting into {table_name}: {e}")
                connection.rollback()
                raise e # Re-raise for other exceptions

def generate_and_insert_data():
    current_month_str, current_year_int = get_current_month_year()
    
    with engine.connect() as conn:
        print("Fetching hierarchy...")
        all_sections_rows = conn.execute(text("""
            SELECT
                c.CircleName,
                d.DivisionName,
                s.SubdivisionName,
                sec.SectionName
            FROM Sections sec
            LEFT JOIN Subdivisions s ON sec.SubdivisionID = s.SubdivisionID
            JOIN Divisions d ON sec.DivisionID = d.DivisionID
            JOIN Circles c ON d.CircleID = c.CircleID
            WHERE s.SubdivisionName IS NOT NULL
        """)).fetchall()

        all_section_identifiers = [(row[0], row[1], row[2], row[3]) for row in all_sections_rows]

        # --- New: Fetch already processed sections from the DB for the current month/year ---
        # Assuming one of your KPI tables (e.g., billing_efficiency) can serve as a marker
        # for a section being processed for a given month/year.
        # This query gets all unique section identifiers that already have data for the current month/year.
        print(f"Checking existing data in DB for {current_month_str}_{current_year_int}...")
        existing_sections_data = conn.execute(text("""
            SELECT DISTINCT
                circle, division, subdivision, section
            FROM billing_efficiency -- Using billing_efficiency as a representative table
            WHERE month = :month AND year = :year
        """), {"month": current_month_str, "year": current_year_int}).fetchall()

        processed_for_current_period = set([(row[0], row[1], row[2], row[3]) for row in existing_sections_data])
        # --- End of New Section ---

        unprocessed_sections = [
            s_id for s_id in all_section_identifiers
            if s_id not in processed_for_current_period
        ]

        if not unprocessed_sections:
            print(f"All sections already have data for {current_month_str}_{current_year_int}. No new data to insert today.")
            return

        sections_to_process_today = random.sample(unprocessed_sections, min(DAILY_SECTION_LIMIT, len(unprocessed_sections)))

        if not sections_to_process_today:
            print(f"No new sections available to process today for {current_month_str}_{current_year_int}.")
            return

        print(f"Processing {len(sections_to_process_today)} unique sections for {current_month_str}_{current_year_int}...")

        kpi_tables = [
            ("billing_efficiency", "value", lambda: round(random.uniform(85, 99), 2)),
            ("revenue_collection_efficiency", "value", lambda: round(random.uniform(80, 98), 2)),
            ("avg_billing_per_consumer", "value", lambda: round(random.uniform(600, 900), 2)),
            ("collection_rate", "value", lambda: round(random.uniform(85, 100), 2)),
            ("unbilled_consumers", "percent", lambda: round(random.uniform(5, 15), 2)),
            ("arrear_ratio", "percent", lambda: round(random.uniform(10, 25), 2)),
            ("billing_coverage", "value", lambda: round(random.uniform(90, 99), 2)),
        ]

        inserted_any_data = False

        for table, column_name, value_fn in kpi_tables:
            print(f"Inserting into {table} for selected sections...")
            data_to_insert = []
            for circle, division, subdivision, section in sections_to_process_today:
                data_to_insert.append({
                    "month": current_month_str,
                    "year": current_year_int,
                    "circle": circle,
                    "division": division,
                    "subdivision": subdivision,
                    "section": section,
                    column_name: value_fn()
                })
            if data_to_insert:
                execute_batch(conn, f"""
                    INSERT INTO {table}
                    (month, year, circle, division, subdivision, section, {column_name})
                    VALUES (:month, :year, :circle, :division, :subdivision, :section, :{column_name})
                    ON DUPLICATE KEY UPDATE {column_name} = VALUES({column_name})
                """, data_to_insert, table)
                inserted_any_data = True

        print("Inserting billing_rate for selected sections...")
        billing_rate_data_to_insert = []
        for circle, division, subdivision, section in sections_to_process_today:
            billing_rate_data_to_insert.append({
                "circle": circle,
                "division": division,
                "subdivision": subdivision,
                "section": section,
                "rate": round(random.uniform(4.5, 6.5), 2)
            })
        if billing_rate_data_to_insert:
            execute_batch(conn, """
                INSERT INTO billing_rate (circle, division, subdivision, section, rate)
                VALUES (:circle, :division, :subdivision, :section, :rate)
                ON DUPLICATE KEY UPDATE rate = VALUES(rate)
            """, billing_rate_data_to_insert, "billing_rate")
            inserted_any_data = True

        # --- Handle disputed_bills and metering_status (aggregated monthly) ---
        # These will still be inserted only once per month.
        # We need to check if data for the current month/year already exists.

        disputed_exists = conn.execute(text(f"""
            SELECT COUNT(*) FROM disputed_bills
            WHERE month = :month AND year = :year
        """), {"month": current_month_str, "year": current_year_int}).scalar()

        if disputed_exists == 0:
            print("Inserting disputed_bills for current month...")
            disputed_data = {
                "month": current_month_str,
                "year": current_year_int,
                "total": random.randint(9000, 11000),
                "disputed": random.randint(200, 600)
            }
            execute_batch(conn, """
                INSERT INTO disputed_bills (month, year, total, disputed)
                VALUES (:month, :year, :total, :disputed)
            """, [disputed_data], "disputed_bills")
            inserted_any_data = True
        else:
            print(f"Disputed bills data already exists for {current_month_str}_{current_year_int}.")

        metering_exists = conn.execute(text(f"""
            SELECT COUNT(*) FROM metering_status
            WHERE month = :month AND year = :year
        """), {"month": current_month_str, "year": current_year_int}).scalar()

        if metering_exists == 0:
            print("Inserting metering_status for current month...")
            metering_data = {
                "month": current_month_str,
                "year": current_year_int,
                "metered": random.randint(15000, 20000),
                "unmetered": random.randint(1000, 5000)
            }
            execute_batch(conn, """
                INSERT INTO metering_status (month, year, metered, unmetered)
                VALUES (:month, :year, :metered, :unmetered)
            """, [metering_data], "metering_status")
            inserted_any_data = True
        else:
            print(f"Metering status data already exists for {current_month_str}_{current_year_int}.")

        if not inserted_any_data:
            print("No new data inserted in this run.")


if __name__ == "__main__":
    print("Starting KPI data generation for daily sections (DB-centric tracking)...")
    try:
        generate_and_insert_data()
        print("Daily section data processing completed.")
    except Exception as e:
        print(f"Aborted due to error: {e}")
        print("Please check the error details and logs for troubleshooting.")