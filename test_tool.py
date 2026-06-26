from tools import validate_shoot_safety
import datetime

# Test: Porsche (finished yesterday) + Beach (Outdoor) + Today (Rainy weather)
# This SHOULD return safety alerts.
today = datetime.date.today().isoformat()
result = validate_shoot_safety("Porsche", "Beach", today)
print(result)