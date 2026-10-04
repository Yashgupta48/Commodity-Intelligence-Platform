import os
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# 1. Securely load API keys from the .env file.
load_dotenv()

def fetch_commodity_data(commodity_name):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f'https://www.alphavantage.co/query?function={commodity_name}&apikey={api_key}'
    
    # 2. Create a dynamic path (so the file always goes to the correct folder).
    script_dir = os.path.dirname(__file__) 
    project_root = os.path.abspath(os.path.join(script_dir, "../../")) 
    raw_data_path = os.path.join(project_root, "data", "raw")
    
    # If the folder does not exist, create it.
    os.makedirs(raw_data_path, exist_ok=True)
    
    print(f"Fetching data for: {commodity_name}...")
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # 3. Handle API Limit (Throttling)
        # If the API limit is exceeded, the API response contains a “Note” or “Information” message.
        if "Note" in data or "Information" in data:
            print(f"⚠️ API Limit Reached! Waiting for 60 seconds...")
            time.sleep(60) # Wait for 60 seconds.
            return fetch_commodity_data(commodity_name) # Try again
            
        # 4. Create the file name with today’s date (Partitioning)
        today = datetime.now().strftime('%Y%m%d')
        file_name = f"{commodity_name}_{today}.json"
        full_file_path = os.path.join(raw_data_path, file_name)
        
        # Save the JSON file (Bronze Layer)
        with open(full_file_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"✅ Success! Data saved to: {full_file_path}")
    else:
        print(f"❌ Failed! Status Code: {response.status_code}")

if __name__ == "__main__":
    # We will fetch data for Soybean, Cotton, and Maize.
    commodities = ["SOYBEAN", "COTTON", "CORN"] #Alpha Vantage refers to Maize as “CORN.”
    
    for item in commodities:
        fetch_commodity_data(item)
        # 15-second gap between each API call to prevent the API from being blocked.
        print("Waiting 15 seconds for the next call to avoid API limits...")
        time.sleep(15)