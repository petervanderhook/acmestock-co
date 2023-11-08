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

with open('creds.yml', 'r') as f:
    creds = yaml.safe_load(f.read())

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


creds = creds['datastore']
DB_ENGINE = create_engine(f"mysql+pymysql://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['database']}")
logger.info(F"Connecting to DB at host: {creds['host']} with user: {creds['user']} on port: {creds['port']}.")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

# Endpoints
def get_sell_order(timestamp):
    with DB_SESSION.begin() as session:
        timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        readings = session.query(SellOrder).filter(SellOrder.sale_date >= timestamp_datetime)
        results_list = []
        for reading in readings:
            results_list.append(reading.to_dict())
    
    logger.info(f"Query for sale orders after {timestamp} returns {len(results_list)} results.")
    return results_list, 200

def get_available_stocks(timestamp):
    with DB_SESSION.begin() as session:
        timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        readings = session.query(Stock).filter(Stock.listing_date >= timestamp_datetime)
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

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yml', strict_validation=True, validate_responses=True)

def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
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

if __name__ == "__main__":
    make_db()
    make_tables()
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)