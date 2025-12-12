
import time
import MySQLdb
from MySQLdb import OperationalError

while True:
    try:
        print("🔍 Trying to connect to the database...")
        conn = MySQLdb.connect(
            host="db",
            user="root",
            passwd="faizan123@A1",
            database="hospital_db"
        )
        conn.close()
        print("✅ Database is ready! Starting Django...")
        break
    except OperationalError:
        print("⏳ Database not ready yet. Waiting 2 seconds...")
        time.sleep(2)

