from fastapi import FastAPI, HTTPException, Query
from urllib.parse import urlparse
import os
import pymysql

app = FastAPI(title="KPI Test API")

# Read from environment
mysql_url = os.getenv("MYSQL_URL")
parsed = urlparse(mysql_url)
user = parsed.username
password = parsed.password
host = parsed.hostname
port = parsed.port or 3306
db = parsed.path.lstrip('/')

def get_connection():
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.get("/test/kpi/")
def get_kpis(
    section_id: int = Query(..., description="Section ID"),
    year: int = Query(..., description="Year"),
    month: int = Query(..., description="Month (1-12)")
):
    data = {}

    try:
        conn = get_connection()
        cur = conn.cursor()

        # service_connections
        cur.execute("""
            SELECT * FROM service_connections 
            WHERE section_id=%s AND year=%s AND month=%s
        """, (section_id, year, month))
        data['service_connections'] = cur.fetchone()

        # metering
        cur.execute("""
            SELECT * FROM metering 
            WHERE section_id=%s AND year=%s AND month=%s
        """, (section_id, year, month))
        data['metering'] = cur.fetchone()

        # billing
        cur.execute("""
            SELECT * FROM billing 
            WHERE section_id=%s AND year=%s AND month=%s
        """, (section_id, year, month))
        data['billing'] = cur.fetchone()

        # collection
        cur.execute("""
            SELECT * FROM collection 
            WHERE section_id=%s AND year=%s AND month=%s
        """, (section_id, year, month))
        data['collection'] = cur.fetchone()

        # disconnection_recovery
        cur.execute("""
            SELECT * FROM disconnection_recovery 
            WHERE section_id=%s AND year=%s AND month=%s
        """, (section_id, year, month))
        data['disconnection_recovery'] = cur.fetchone()

        cur.close()
        conn.close()

        if not any(data.values()):
            raise HTTPException(status_code=404, detail="No KPI data found for given parameters.")

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
