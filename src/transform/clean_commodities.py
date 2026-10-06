import os
import sys

# --- Windows PySpark Error Fix ---
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
os.environ['HADOOP_HOME'] = 'D:\\hadoop'
os.environ['PATH'] = os.environ['HADOOP_HOME'] + '\\bin;' + os.environ.get('PATH', '')
# ---------------------------------

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, to_date, lit

def clean_commodity_data():
    print("🚀 Spark इंजन चालू हो रहा है (इसमें 10-15 सेकंड लग सकते हैं)...")
    
    # .config वाली लाइन Spark को क्रैश होने से बचाएगी
    spark = SparkSession.builder \
        .appName("CommodityCleaning_SilverLayer") \
        .config("spark.sql.ansi.enabled", "false") \
        .getOrCreate()
        
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))
    raw_path = os.path.join(project_root, "data", "raw")
    processed_path = os.path.join(project_root, "data", "processed")
    
    os.makedirs(processed_path, exist_ok=True)
    
    commodities = ["WHEAT", "COTTON", "CORN"]
    
    for commodity in commodities:
        print(f"\n🔄 सफाई शुरू: {commodity}...")
        
        file_pattern = os.path.join(raw_path, f"{commodity}_*.json")
        
        try:
            df_raw = spark.read.option("multiline", "true").json(file_pattern)
            
            # .filter(col("entry.value") != ".") -> यह लाइन '.' वाले कचरे को हटा देगी
            df_clean = df_raw.select(explode(col("data")).alias("entry")) \
                             .filter(col("entry.value") != ".") \
                             .select(
                                 to_date(col("entry.date"), "yyyy-MM-dd").alias("price_date"), 
                                 col("entry.value").cast("float").alias("price_usd")           
                             ) \
                             .withColumn("commodity_name", lit(commodity)) \
                             .filter(col("price_usd").isNotNull()) 
                             
            output_dir = os.path.join(processed_path, f"{commodity.lower()}_silver")
            df_clean.write.mode("overwrite").parquet(output_dir)
            
            print(f"✅ {commodity} का डेटा साफ होकर Silver Layer (Parquet) में सेव हो गया!")
            
        except Exception as e:
            print(f"⚠️ {commodity} का डेटा प्रोसेस करने में दिक्कत आई: {e}")

    spark.stop()
    print("\n✅ सभी कमोडिटीज़ का काम पूरा हुआ!")

if __name__ == "__main__":
    clean_commodity_data()