import sqlite3
import datetime

conn = sqlite3.connect('signature.db')
cursor = conn.cursor()

# 1. Add Future Weather (One sunny day, one storm)
tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
day_after = (datetime.date.today() + datetime.timedelta(days=2)).isoformat()

cursor.execute("INSERT OR IGNORE INTO weather_forecast VALUES (?, 'Sunny')", (tomorrow,))
cursor.execute("INSERT OR IGNORE INTO weather_forecast VALUES (?, 'High-Wind')", (day_after,))

# 2. Add more specialized staff (Drivers vs Media)
cursor.execute("INSERT INTO employees (name, role) VALUES ('Marco', 'Driver'), ('Lucia', 'Media_Team')")

conn.commit()
conn.close()
print("Future planning data added!")