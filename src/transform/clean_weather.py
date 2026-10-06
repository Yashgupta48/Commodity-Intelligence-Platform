import os
import sys

# --- Windows PySpark Error Fix ---
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
os.environ['HADOOP_HOME'] = 'D:\\hadoop'
os.environ['PATH'] = os.environ['HADOOP_HOME'] + '\\bin;' + os.environ.get('PATH', '')
# ---------------------------------

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, from_unixtime, lit

def clean_weather_data():
    print("🚀 Spark इंजन चालू हो रहा है (Weather Data के लिए)...")
    spark = SparkSession.builder \
        .appName("WeatherCleaning_SilverLayer") \
        .getOrCreate()
        
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))
    raw_path = os.path.join(project_root, "data", "raw")
    processed_path = os.path.join(project_root, "data", "processed")
    
    # हमारे 3 शहर
    cities = ["INDORE", "NAGPUR", "LUDHIANA"]
    
    for city in cities:
        print(f"\n🔄 सफाई शुरू: {city} Weather...")
        
        file_pattern = os.path.join(raw_path, f"WEATHER_{city}_*.json")
        
        try:
            # कच्चा JSON रीड करना
            df_raw = spark.read.option("multiline", "true").json(file_pattern)
            
            # Weather JSON के अंदर से ज़रूरी चीज़ें निकालना
            df_clean = df_raw.select(
                to_date(from_unixtime(col("dt"))).alias("weather_date"),       # टाइमस्टैम्प को डेट बनाना
                col("main.temp").cast("float").alias("temperature_c"),         # तापमान
                col("main.humidity").cast("int").alias("humidity_pct"),        # नमी (Humidity)
                col("weather").getItem(0)["main"].alias("weather_condition")   # मौसम कैसा है (Clear, Rain आदि)
            ).withColumn("city_name", lit(city))
                             
            # Parquet फॉर्मेट (सिल्वर लेयर) में सेव करना
            output_dir = os.path.join(processed_path, f"weather_{city.lower()}_silver")
            df_clean.write.mode("overwrite").parquet(output_dir)
            
            print(f"✅ {city} मौसम का डेटा साफ होकर Silver Layer (Parquet) में सेव हो गया!")
            
        except Exception as e:
            print(f"⚠️ {city} का डेटा प्रोसेस करने में दिक्कत आई: {e}")

    spark.stop()
    print("\n✅ सभी शहरों के मौसम का काम पूरा हुआ!")

if __name__ == "__main__":
    clean_weather_data()