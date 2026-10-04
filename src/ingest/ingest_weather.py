import os
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load API keys from the .env file.
load_dotenv()

def fetch_weather_data(city_name):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    # OpenWeather API URL (units=metric will give the temperature in Celsius)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    
    # Create a dynamic path (so the file always goes to the correct folder).
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))
    raw_data_path = os.path.join(project_root, "data", "raw")
    os.makedirs(raw_data_path, exist_ok=True)
    
    print(f"Fetching weather data for: {city_name}...")
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # Create the file name with today’s date.
        today = datetime.now().strftime('%Y%m%d')
        file_name = f"WEATHER_{city_name.upper()}_{today}.json"
        full_file_path = os.path.join(raw_data_path, file_name)
        
        # Save the JSON file.
        with open(full_file_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"✅ Weather Data saved: {file_name}")
    else:
        print(f"❌ Failed to fetch {city_name}. Error Code: {response.status_code}")

if __name__ == "__main__":
    # Fetch data for major agro hubs in India.
    cities = ["Indore", "Nagpur", "Ludhiana"]
    
    for city in cities:
        fetch_weather_data(city)
        # API secure, so 2 second gap.
        time.sleep(2)