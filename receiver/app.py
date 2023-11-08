import json
import connexion
from connexion import NoContent
import swagger_ui_bundle
import requests
import yaml
from pykafka import KafkaClient
from datetime import datetime
import logging, logging.config
from uuid import uuid4
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')



def process_events(event, endpoint): 
    print(endpoint, app_config[endpoint])
    endpoint_url = app_config[endpoint]['url']
    endpoint_type = app_config[endpoint]['type']
    trace_id = str(uuid4())
    logger.info(f"Received {endpoint} event with id: {trace_id}")
    if endpoint_type == 'post':
        event['trace_id'] = trace_id
        client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
        topic = client.topics[str.encode(app_config['events']['topic'])]
        producer = topic.get_sync_producer()
        msg = { "type": endpoint_url,
            "datetime" : datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": event }
        msg_str = json.dumps(msg)
        producer.produce(msg_str.encode('utf-8'))
        logger.info(f"Returned event {endpoint} response. (ID: {trace_id} with status code {201})")
        return NoContent, 201

def add_new_stock(body):
    return process_events(body, 'new_stock')

def sell_order(body):
    return process_events(body, 'new_sell_order')

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)