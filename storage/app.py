import datetime
import json
import connexion
from connexion import NoContent
import swagger_ui_bundle
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from new_stock import Stock
from create_tables_mysql import make_tables
from db_create import make_db
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from sell_order import SellOrder
import yaml
import logging, logging.config
import time
from sqlalchemy import and_

with open('creds.yml', 'r') as f:
    creds = yaml.safe_load(f.read())

import os
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/storage/app_conf.yml"
    log_conf_file = "/config/storage/log_conf.yml"
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
     

creds = creds['datastore']
DB_ENGINE = create_engine(f"mysql+pymysql://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['database']}")
logger.info(F"Connecting to DB at host: {creds['host']} with user: {creds['user']} on port: {creds['port']}.")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

# Endpoints
def get_sell_order(timestamp, end_timestamp):
    with DB_SESSION.begin() as session:
        timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        readings = session.query(SellOrder).filter(and_(SellOrder.sale_date >= timestamp_datetime, SellOrder.sale_date <= end_timestamp))
        results_list = []
        for reading in readings:
            results_list.append(reading.to_dict())
    
    logger.info(f"Query for sale orders after {timestamp} returns {len(results_list)} results.")
    return results_list, 200

def get_available_stocks(timestamp, end_timestamp):
    with DB_SESSION.begin() as session:
        start_timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        readings = session.query(Stock).filter(and_(Stock.listing_date >= start_timestamp_datetime, Stock.listing_date <= end_timestamp))
        results_list = []
        for reading in readings:
            results_list.append(reading.to_dict())
    
    logger.info(f"Query for available stocks listed after {timestamp} returns {len(results_list)} results.")
    return results_list, 200

def push_sell_order(body):
    logger.debug(f"Stored event SELL STOCK request with a trace id of {body['trace_id']}")
    with DB_SESSION.begin() as session:
        sell_order_object = SellOrder(body['seller_id'], body['broker_id'], body['share_price'], body['amount'], body['trace_id'])
        session.add(sell_order_object)

    return NoContent, 201

def push_stock(body):
    logger.debug(f"Stored event NEW STOCK request with a trace id of {body['trace_id']}")
    with DB_SESSION.begin() as session:
        new_stock_object = Stock(body['listing_id'], body['company'], body['share_price'], body['total_shares_available'], body['trace_id'])
        session.add(new_stock_object)

    return NoContent, 201

def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    retries = 0
    logger.debug(f"Attemping to connect to Kafka")
    while retries < 30:
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            logger.debug(f"Connected to Kafka on attempt {retries}")
            break
        except () as e:
            logger.error(f"ERROR connecting to kafka db on attempt {retries}: {e}")
            retries += 1
            time.sleep(5)
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
    reset_offset_on_start=False,
    auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "new_stock":
            push_stock(payload)
        elif msg["type"] == "new_sell_order":
            push_sell_order(payload)
        consumer.commit_offsets()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yml', base_path='/storage', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    make_db()
    make_tables()
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(host='0.0.0.0', port=8090)
