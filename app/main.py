import os
import json
from datetime import datetime
from quixstreams import Application
import logging

# Load environment variables (useful when working locally)
from dotenv import load_dotenv
# load_dotenv(os.path.dirname(os.path.abspath(__file__))+"/.env")
load_dotenv(".env")

# Logggin env
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

logging.basicConfig(
    level=log_level,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Config
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_INPUT_TOPIC = os.getenv("KAFKA_INPUT_TOPIC", "iot-frames-model")
SAVE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/stream_sensor_data.jsonl"

app = Application(broker_address=KAFKA_BROKER,
                loglevel="INFO",
                auto_offset_reset="earliest",
                state_dir=os.path.dirname(os.path.abspath(__file__))+"/state/",
                consumer_group="stream_kafka_to_file"
      )
input_topic = app.topic(KAFKA_INPUT_TOPIC, value_deserializer="json")

# ✅ เขียน message ลงไฟล์แบบ JSON lines
def handle_message(row):
    try:
        with open(SAVE_PATH, "a") as f:
            f.write(json.dumps(row) + "\n")
        logging.info(f"💾 Saved message at {datetime.now()} {json.dumps(row)}")
    except Exception as e:
        logging.error(f"❌ Error saving message: {e}")

# Stream
sdf = app.dataframe(input_topic)
sdf = sdf.apply(handle_message)

logging.info(f"Connecting to ...{KAFKA_BROKER}")
logging.info(f"🚀 Listening to Kafka topic: {KAFKA_INPUT_TOPIC}")
app.run(sdf)
