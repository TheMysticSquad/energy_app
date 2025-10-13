import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv
from prepaid_module_v2 import Consumer, TariffPlan
import urllib.parse as urlparse

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()
DB_URL = os.getenv("DB")  # Example: mysql://user:pass@host:port/db?ssl-mode=REQUIRED


class DatabaseManager:
    """
    MySQL database access layer with connection pooling and internal query management.
    """

    def __init__(self):
        self.db_config = self._parse_db_url()
        self.pool = self._create_connection_pool()

    # -----------------------------
    # Parse MySQL URL
    # -----------------------------
    def _parse_db_url(self):
        if not DB_URL:
            raise ValueError("Database URL not found in environment variables")

        # Parse the URL properly
        url = urlparse.urlparse(DB_URL)

        db_config = {
            "user": url.username,
            "password": url.password,
            "host": url.hostname,
            "port": url.port,
            "database": url.path.lstrip("/"),
            "ssl_mode": "REQUIRED",
        }

        # Extract ssl-mode from query if provided
        query_params = dict(urlparse.parse_qsl(url.query))
        if "ssl-mode" in query_params:
            db_config["ssl_mode"] = query_params["ssl-mode"]

        print("🔗 Parsed DB Config:")
        print(f"Host: {db_config['host']}")
        print(f"Port: {db_config['port']}")
        print(f"User: {db_config['user']}")
        print(f"Database: {db_config['database']}")
        print(f"SSL Mode: {db_config['ssl_mode']}")

        return db_config

    # -----------------------------
    # Create MySQL Connection Pool
    # -----------------------------
    def _create_connection_pool(self):
        try:
            print(f"🌐 Connecting to MySQL @ {self.db_config['host']}:{self.db_config['port']} "
                  f"(DB: {self.db_config['database']})")

            pool = pooling.MySQLConnectionPool(
                pool_name="prepaid_pool",
                pool_size=5,
                host=self.db_config["host"],
                user=self.db_config["user"],
                password=self.db_config["password"],
                database=self.db_config["database"],
                port=self.db_config["port"],
            )

            print("✅ Connection pool created successfully.")
            return pool

        except Exception as e:
            raise Exception(f"Error creating MySQL connection pool: {e}")

    # -----------------------------
    # Utility: Run Query Safely
    # -----------------------------
    def _run_query(self, query, params=(), fetch=False, fetchone=False):
        conn = None
        cursor = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetchone:
                result = cursor.fetchone()
            elif fetch:
                result = cursor.fetchall()
            else:
                result = None

            conn.commit()
            return result
        except Exception as e:
            print(f"⚠️ DB Error: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # -----------------------------
    # Consumers
    # -----------------------------
    def get_all_consumers(self):
        query = "SELECT consumer_id, name, address, phone, balance, status FROM consumers"
        rows = self._run_query(query, fetch=True)
        consumers = []
        if rows:
            for row in rows:
                consumer = Consumer(
                    consumer_id=row[0],
                    name=row[1],
                    address=row[2],
                    phone=row[3],
                    balance=row[4],
                )
                consumer.status = row[5]
                consumers.append(consumer)
        return consumers

    def get_consumer_by_id(self, consumer_id):
        query = "SELECT consumer_id, name, address, phone, balance, status FROM consumers WHERE consumer_id = %s"
        row = self._run_query(query, (consumer_id,), fetchone=True)
        if row:
            consumer = Consumer(
                consumer_id=row[0],
                name=row[1],
                address=row[2],
                phone=row[3],
                balance=row[4],
            )
            consumer.status = row[5]
            return consumer
        return None

    def update_consumer_balance(self, consumer_id, new_balance):
        query = "UPDATE consumers SET balance = %s WHERE consumer_id = %s"
        self._run_query(query, (new_balance, consumer_id))

    def update_consumer_details(self, consumer_id, name, address, phone):
        query = "UPDATE consumers SET name = %s, address = %s, phone = %s WHERE consumer_id = %s"
        self._run_query(query, (name, address, phone, consumer_id))

    # -----------------------------
    # Tariff
    # -----------------------------
    def get_tariff_plan(self, plan_id="A1"):
        query = """SELECT plan_id, rate_per_kwh, fixed_charge_daily, low_balance_threshold, subsidy_units, subsidy_rate 
                   FROM tariff_plan WHERE plan_id = %s"""
        row = self._run_query(query, (plan_id,), fetchone=True)
        if row:
            return TariffPlan(
                plan_id=row[0],
                rate_per_kwh=row[1],
                fixed_charge_daily=row[2],
                low_balance_threshold=row[3],
                subsidy_units=row[4],
                subsidy_rate=row[5]
            )
        return None

    # -----------------------------
    # Consumption Records
    # -----------------------------
    def insert_consumption_record(self, record):
        query = """
        INSERT INTO consumption_records 
        (consumer_id, timestamp, kwh_used, subsidy_units, energy_charge, fixed_charge, total_deduction, balance_before, balance_after) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self._run_query(query, (
            record.consumer_id,
            record.timestamp,
            record.kwh_consumed,
            record.subsidy_units,
            record.energy_charge,
            record.fixed_charge,
            record.total_deduction,
            record.balance_before,
            record.balance_after
        ))

    def get_consumption_history(self, consumer_id):
        query = """
        SELECT timestamp, kwh_consumed, subsidy_units, energy_charge, fixed_charge, total_deduction, balance_before, balance_after
        FROM consumption_records WHERE consumer_id = %s
        ORDER BY timestamp DESC
        """
        return self._run_query(query, (consumer_id,), fetch=True)
