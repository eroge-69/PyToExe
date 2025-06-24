import mysql.connector
import socket
import uuid

# Generate device token + get PC hostname
device_token = str(uuid.uuid4())
hostname = socket.gethostname()

# Prompt the user
school_id = input("Enter School ID: ")
school_name = input("Enter School Name: ")

# Connect to HostGator MySQL
try:
    conn = mysql.connector.connect(
        host="gator3154.hostgator.com",
        user="igorotec_timetracking2",
        password="25Timetr@ck!ng",
        database="igorotec_time_tracking"
    )
    cursor = conn.cursor()

    query = """
    INSERT INTO registered_devices (school_id, school_name, device_token, hostname)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (school_id, school_name, device_token, hostname))
    conn.commit()

    print("✅ Device registered successfully!")
    print("Device Token:", device_token)

    cursor.close()
    conn.close()

except Exception as e:
    print("❌ Error connecting or inserting:", e)
