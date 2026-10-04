import json
import os

def validate_commodity_json(file_path):
    """
    Commodity JSON file ki quality check karta hai.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Check 1: Kya data khali toh nahi hai?
    if not data or "data" not in data:
        return False, "Missing 'data' key or file is empty."
    
    # Check 2: Kya price zero ya negative hai?
    # Alpha Vantage mein data[0] sabse latest price hota hai
    latest_entry = data["data"][0]
    try:
        price = float(latest_entry["value"])
        if price <= 0:
            return False, f"Invalid Price: {price}"
    except (ValueError, KeyError):
        return False, "Price is not a valid number or missing."

    return True, "Success"

def run_quality_check():
    # Root folder tak pahunchna (Dynamic Path)
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))
    raw_path = os.path.join(project_root, "data", "raw")
    
    print("--- Starting Data Quality Check ---")
    
    for file_name in os.listdir(raw_path):
        if file_name.endswith(".json") and not file_name.startswith("WEATHER"):
            file_path = os.path.join(raw_path, file_name)
            is_valid, message = validate_commodity_json(file_path)
            
            if is_valid:
                print(f"✅ {file_name}: Passed")
            else:
                print(f"❌ {file_name}: Failed! Reason: {message}")

if __name__ == "__main__":
    run_quality_check()