import json
import time
import os
from uuid import uuid4
from datetime import datetime
import logging, logging.config
import connexion
from connexion import NoContent
import swagger_ui_bundle
import yaml
from pykafka import KafkaClient
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/receiver/app_conf.yml"
    log_conf_file = "/config/receiver/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open(app_conf_file, 'r') as f:
    APP_CONFIG = yaml.safe_load(f.read())
with open(log_conf_file, 'r') as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger('basicLogger')
logger.info(f"App Conf File: {app_conf_file}")
logger.info(f"Log Conf File: {log_conf_file}")

retries = 1
while retries < 31:
    logger.info(f'ATTEMPT {retries}: Connecting to kafka service. {APP_CONFIG["events"]["hostname"]}:{APP_CONFIG["events"]["port"]}')
    try:
        client = KafkaClient(hosts=f'{APP_CONFIG["events"]["hostname"]}:{APP_CONFIG["events"]["port"]}')
        topic = client.topics[str.encode(APP_CONFIG['events']['topic'])]
        logger.info(f'Connected to kafka service after {retries} attempts.')
        producer = topic.get_sync_producer()
        break
    except () as e:
        logger.error(f'ERROR connecting to kafka on attempt {retries}: {e}')
        time.sleep(5)
        retries += 1
        if retries == 31:
            logger.error(f'ERROR Unable to connect to Kafka service. Exiting: {e}')
            raise ConnectionError
        
def process_events(event, endpoint):
    print(endpoint, APP_CONFIG[endpoint])
    endpoint_url = APP_CONFIG[endpoint]['url']
    endpoint_type = APP_CONFIG[endpoint]['type']
    trace_id = str(uuid4())
    logger.info(f"Received {endpoint} event with id: {trace_id}, endpoint_type: {endpoint_type}")
    if endpoint_type == 'post':
        event['trace_id'] = trace_id
        msg = { "type": endpoint_url,
            "datetime" : datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "payload": event }
        msg_str = json.dumps(msg)
        producer.produce(msg_str.encode('utf-8'))
        logger.info(f"Returned event {endpoint} response. (ID: {trace_id} with status code {201})")
        return NoContent, 201
    return NoContent, 404
def health():
    return 200
def add_new_stock(body):
    return process_events(body, 'new_stock')
def sell_order(body):
    return process_events(body, 'new_sell_order')
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", base_path='/receiver', strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)