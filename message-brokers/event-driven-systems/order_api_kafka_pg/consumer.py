
import logging
from dotenv import load_dotenv
from kafka_io import make_consumer

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
log = logging.getLogger("orders_consumer")

def main():
    consumer = make_consumer()
    log.info("Consuming from topic...")
    for msg in consumer:
        log.info("topic=%s partition=%s offset=%s key=%s value=%s",
                 msg.topic, msg.partition, msg.offset, msg.key, msg.value)

if __name__ == "__main__":
    main()
