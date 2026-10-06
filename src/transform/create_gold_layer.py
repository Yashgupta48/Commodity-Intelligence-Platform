import os
import sys

# --- Windows PySpark Error Fix ---
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
os.environ['HADOOP_HOME'] = 'D:\\hadoop'
os.environ['PATH'] = os.environ['HADOOP_HOME'] + '\\bin;' + os.environ.get('PATH', '')
# ---------------------------------

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def create_gold_layer():
    print("🚀 Spark इंजन चालू हो रहा है (Gold Layer के लिए)...")
    spark = SparkSession.builder \
        .appName("GoldLayer_Integration") \
        .getOrCreate()
        
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))
    
    # Silver (इनपुट) और Gold (आउटपुट) के रास्ते
    processed_path = os.path.join(project_root, "data", "processed")
    gold_path = os.path.join(project_root, "data", "gold")
    
    # Gold फोल्डर बनाना
    os.makedirs(gold_path, exist_ok=True)
    
    # कमोडिटी और उनके मुख्य उत्पादक शहरों की मैपिंग (Mapping)
    mapping = {
        "WHEAT": "ludhiana",
        "COTTON": "nagpur",
        "CORN": "indore"
    }
    
    for commodity, city in mapping.items():
        print(f"\n🔄 मिला रहे हैं: {commodity} को {city.upper()} के मौसम के साथ...")
        
        try:
            # 1. Silver Layer से दोनों फाइलों को रीड करना
            comm_df = spark.read.parquet(os.path.join(processed_path, f"{commodity.lower()}_silver"))
            weather_df = spark.read.parquet(os.path.join(processed_path, f"weather_{city}_silver"))
            
            # 2. दोनों को Date के आधार पर Join करना
            gold_df = comm_df.join(
                weather_df,
                comm_df.price_date == weather_df.weather_date,
                "inner"
            ).select(
                col("price_date").alias("date"),
                col("commodity_name"),
                col("price_usd"),
                col("city_name"),
                col("temperature_c"),
                col("humidity_pct"),
                col("weather_condition")
            )
                             
            # 3. Gold Layer (Parquet) में सेव करना
            output_dir = os.path.join(gold_path, f"{commodity.lower()}_weather_gold")
            gold_df.write.mode("overwrite").parquet(output_dir)
            
            print(f"✅ {commodity} का Gold Data तैयार हो गया!")
            
        except Exception as e:
            print(f"⚠️ {commodity} का डेटा जोड़ने में दिक्कत आई: {e}")

    spark.stop()
    print("\n🏆 Gold Layer का काम पूरा हुआ! आपका डेटा अब Power BI/Dashboards के लिए 100% तैयार है।")

if __name__ == "__main__":
    create_gold_layer()