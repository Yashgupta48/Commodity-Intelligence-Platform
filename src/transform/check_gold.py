import os
import sys

# --- Windows PySpark Path Fix ---
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
os.environ['HADOOP_HOME'] = 'D:\\hadoop'
os.environ['PATH'] = os.environ['HADOOP_HOME'] + '\\bin;' + os.environ.get('PATH', '')
# ---------------------------------

from pyspark.sql import SparkSession

def view_gold_data():
    # Spark Session स्टार्ट करना (Log level WARN करके फालतू के मैसेज छिपाना)
    spark = SparkSession.builder \
        .appName("ViewGoldData") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    script_dir = os.path.dirname(__file__)
    gold_path = os.path.abspath(os.path.join(script_dir, "../../data/gold"))

    try:
        print("\n🌾 --- WHEAT & LUDHIANA WEATHER (GOLD DATA) ---")
        wheat_df = spark.read.parquet(os.path.join(gold_path, "wheat_weather_gold"))
        wheat_df.show(5, truncate=False)

        print("\n🌽 --- CORN & INDORE WEATHER (GOLD DATA) ---")
        corn_df = spark.read.parquet(os.path.join(gold_path, "corn_weather_gold"))
        corn_df.show(5, truncate=False)
        
    except Exception as e:
        print(f"⚠️ डेटा दिखाने में एरर: {e}")

    spark.stop()

if __name__ == "__main__":
    view_gold_data()