import sqlite3
import datetime

def init_db():
    conn = sqlite3.connect('signature.db')
    cursor = conn.cursor()

    # Drop old tables if they exist to start fresh
    cursor.executescript('''
        DROP TABLE IF EXISTS vehicles;
        DROP TABLE IF EXISTS employees;
        DROP TABLE IF EXISTS locations;
        DROP TABLE IF EXISTS weather_forecast;
        DROP TABLE IF EXISTS media_projects;
        DROP TABLE IF EXISTS business_rules;
        DROP TABLE IF EXISTS reports;
        DROP TABLE IF EXISTS agent_audit_logs;
    ''')

    # 1. CREATE ALL TABLES (The Full Schema)
    cursor.executescript('''
        CREATE TABLE vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT,
            license_plate TEXT UNIQUE,
            detailing_status TEXT,
            last_finish_date DATETIME
        );

        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            role TEXT,
            is_available BOOLEAN DEFAULT 1
        );

        CREATE TABLE locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            location_type TEXT,
            sq_meters INTEGER
        );

        CREATE TABLE weather_forecast (
            forecast_date DATE PRIMARY KEY,
            condition TEXT
        );

        CREATE TABLE media_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            location_id INTEGER,
            scheduled_at DATETIME,
            status TEXT DEFAULT 'Pending'
        );

        CREATE TABLE business_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT,
            description TEXT
        );

        CREATE TABLE reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            report_content TEXT
        );

        CREATE TABLE agent_audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_query TEXT,
            ai_thought_process TEXT,
            tool_used TEXT,
            tool_output TEXT
        );
    ''')

    # 2. INSERT TEST DATA & BUSINESS RULES
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    five_days_ago = (datetime.datetime.now() - datetime.timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
    today_date = datetime.date.today().isoformat()

    # Vehicles
    cursor.execute("INSERT INTO vehicles (model, license_plate, detailing_status, last_finish_date) VALUES (?, ?, ?, ?)", 
                   ('Porsche 911', 'ABC-123', 'Completed', yesterday))
    cursor.execute("INSERT INTO vehicles (model, license_plate, detailing_status, last_finish_date) VALUES (?, ?, ?, ?)", 
                   ('BMW M3', 'XYZ-789', 'Completed', five_days_ago))
    
    # Employees & Locations
    cursor.execute("INSERT INTO employees (name, role) VALUES ('Ali', 'Driver'), ('Sarah', 'Media_Team')")
    cursor.execute("INSERT INTO locations (name, location_type, sq_meters) VALUES ('Beach', 'Outdoor', 500), ('Showroom', 'Indoor', 150)")
    
    # Weather
    cursor.execute("INSERT INTO weather_forecast (forecast_date, condition) VALUES (?, 'Rainy')", (today_date,))

    # Grounded Business Rules (Project Requirement!)
    cursor.execute("INSERT INTO business_rules (rule_name, description) VALUES (?, ?)", 
                   ('Outdoor Shoot Rule', 'Cars must wait 48 hours after detailing before an outdoor shoot.'))
    cursor.execute("INSERT INTO business_rules (rule_name, description) VALUES (?, ?)", 
                   ('Weather Policy', 'No outdoor shoots allowed if weather is Rainy or High-Wind.'))
    cursor.execute("INSERT INTO business_rules (rule_name, description) VALUES (?, ?)", 
                   ('Wide Angle Rule', 'Shoots requiring wide angles need at least 200 sq meters of space.'))

    conn.commit()
    conn.close()
    print("Full Pro Database created successfully!")

if __name__ == "__main__":
    init_db()