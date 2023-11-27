import json
import connexion
from connexion import NoContent
import swagger_ui_bundle
import requests
import yaml
import logging, logging.config
from uuid import uuid4
from apscheduler.schedulers.background import BackgroundScheduler
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin

import os
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/audit_log/app_conf.yml"
    log_conf_file = "/config/audit_log/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    # External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)
     

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

def health():
    return 200

app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", base_path='/audit', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8110, use_reloader=False)