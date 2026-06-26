import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'signature.db'

def get_db_connection():
    return sqlite3.connect(DB_PATH)

# ==========================================================
# 1. INFORMATION TOOLS (Requirement: Retrieves grounded facts)
# ==========================================================

def get_business_rules():
    """Retrieves the official company policies for shoots and safety."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT rule_name, description FROM business_rules")
    rules = cursor.fetchall()
    conn.close()
    return "\n".join([f"{r[0]}: {r[1]}" for r in rules])

def get_vehicle_status(model_name: str):
    """Checks a car's detailing status and last finish date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, model, detailing_status, last_finish_date FROM vehicles WHERE model LIKE ?", (f"%{model_name}%",))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "model": row[1], "status": row[2], "finished": row[3]}
    return "Vehicle not found."

def list_all_vehicles():
    """Returns a list of all vehicles currently in the shop database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT model, detailing_status FROM vehicles")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return "The shop is currently empty."
    return "\n".join([f"- {r[0]}: {r[1]}" for r in rows])

# ==========================================================
# 2. ANALYSIS TOOL (Requirement: Validates inputs/calculates logic)
# ==========================================================

def analyze_shoot_request(model_name: str, location_name: str, is_wide_angle: str = "false"):
    """
    Analyzes if a request is safe. Checks weather, 48h polish rule, and space.
    is_wide_angle should be 'true' or 'false'.
    """
    # FIX: Convert input to boolean safely to avoid the 400 error
    wide_angle_bool = str(is_wide_angle).lower() == "true"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get Data
    cursor.execute("SELECT last_finish_date FROM vehicles WHERE model LIKE ?", (f"%{model_name}%",))
    v_data = cursor.fetchone()
    cursor.execute("SELECT location_type, sq_meters, id FROM locations WHERE name = ?", (location_name,))
    l_data = cursor.fetchone()
    cursor.execute("SELECT condition FROM weather_forecast LIMIT 1") 
    w_data = cursor.fetchone()
    conn.close()

    if not (v_data and l_data and w_data):
        return "Error: Could not find car, location, or weather data to analyze."

    # Logic Calculations
    last_finish = datetime.strptime(v_data[0], '%Y-%m-%d %H:%M:%S')
    hours_passed = (datetime.now() - last_finish).total_seconds() / 3600
    
    loc_type, space, loc_id = l_data
    weather = w_data[0]
    
    decisions = []
    is_safe = True

    # Check 48h Rule
    if loc_type == 'Outdoor' and hours_passed < 48:
        decisions.append(f"BLOCK: Only {int(hours_passed)}h since polish. Needs 48h for outdoor.")
        is_safe = False
    
    # Check Weather
    if loc_type == 'Outdoor' and weather in ['Rainy', 'High-Wind']:
        decisions.append(f"BLOCK: Weather is {weather}. No outdoor shoots.")
        is_safe = False

    # Check Space (Feature #2)
    if wide_angle_bool and space < 200:
        decisions.append(f"WARNING: {location_name} is only {space}m2. Wide angles need 200m2.")

    status = "REJECTED" if not is_safe else "APPROVED"
    return {"status": status, "reason": " | ".join(decisions) if decisions else "All checks passed.", "loc_id": loc_id, "v_id": v_data}

# ==========================================================
# 3. ACTION TOOL (Requirement: Updates an authorized record)
# ==========================================================

def confirm_booking(vehicle_id: int, location_id: int, scheduled_time: str):
    """Finalizes the booking in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO media_projects (vehicle_id, location_id, scheduled_at, status) VALUES (?, ?, ?, 'Confirmed')",
            (vehicle_id, location_id, scheduled_time)
        )
        conn.commit()
        return f"SUCCESS: Project scheduled for Car {vehicle_id} at Location {location_id}."
    except Exception as e:
        return f"DATABASE ERROR: {str(e)}"
    finally:
        conn.close()

# ==========================================================
# 4. REPORTING TOOL (Requirement: Produces structured summary)
# ==========================================================

def create_daily_production_report():
    """Generates a summary of all shoots and saves it to the reports table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT v.model, l.name, m.scheduled_at 
        FROM media_projects m
        JOIN vehicles v ON m.vehicle_id = v.id
        JOIN locations l ON m.location_id = l.id
        WHERE m.status = 'Confirmed'
    """)
    rows = cursor.fetchall()
    
    if not rows:
        return "No projects confirmed to report."

    report_text = "--- DAILY PRODUCTION CALL SHEET ---\n"
    for r in rows:
        report_text += f"• {r[0]} @ {r[1]} scheduled for {r[2]}\n"
    
    cursor.execute("INSERT INTO reports (report_content) VALUES (?)", (report_text,))
    conn.commit()
    conn.close()
    
    return report_text

# ==========================================================
# EXTRA: AUDIT LOGGING (Requirement: 15% Observability)
# ==========================================================

def log_agent_thought(query: str, thought: str, tool_used: str, output: str):
    """Logs the AI's internal reasoning for the professor to evaluate."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO agent_audit_logs (user_query, ai_thought_process, tool_used, tool_output) VALUES (?, ?, ?, ?)",
        (query, thought, tool_used, str(output))
    )
    conn.commit()
    conn.close()