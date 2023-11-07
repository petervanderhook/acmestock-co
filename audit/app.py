import json
import connexion
from connexion import NoContent
import swagger_ui_bundle
import requests
import yaml
from datetime import datetime
import logging, logging.config
from uuid import uuid4
from apscheduler.schedulers.background import BackgroundScheduler
from pykafka import KafkaClient


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_consumer_index(index, str_type):
    f""" Get {str_type} Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info(f"Retrieving {str_type} at index: {index}")
    try:
        i = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            print(str_type, i, f"target: {index}", msg)
            if msg['type'] == str_type:
                if i == index:
                    return {"event": msg['payload']}, 200
                i += 1
    except Exception as e:
        logger.error(f"No more messages found. EXCEPTION: {e}")
        logger.error(f"Could not find {str_type} at index: {index}")
    return { "message": "Not Found"}, 404

def get_stock_price(index):
    res = get_consumer_index(index, "new_sell_order")
    print("RESPONSE", res)
    return res

def get_stock_quantity(index):
    res =  get_consumer_index(index, "new_stock")
    print("RESPONSE", res)
    return res


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110, use_reloader=False)