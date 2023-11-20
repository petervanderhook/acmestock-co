import json
import connexion
from connexion import NoContent
import swagger_ui_bundle
import requests
import yaml
from datetime import datetime
import logging, logging.config
from flask_cors import CORS, cross_origin
from uuid import uuid4
from apscheduler.schedulers.background import BackgroundScheduler

import os
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/processing/app_conf.yml"
    log_conf_file = "/config/processing/log_conf.yml"
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
            

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'],
                  max_instances=30)
    sched.start()


def populate_stats():
    # Periodically update stats
    logger.info("Static Periodic Statistic Processing Started...")
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            datastore = json.loads(f.read())
    except FileNotFoundError:
        logger.error(f"{app_config['datastore']['filename']} Statistics file not found.")
        with open(app_config['datastore']['filename'], 'w+') as f:
            file_data = {"num_sell_orders_listed": 0,"num_stocks_listed": 0, "average_stock_price": 0, "total_shares_available": 0, "average_shares_available_per_stock": 0, "last_updated": "2023-10-10T10:52:57.000Z"}
            f.write(json.dumps(file_data))
        return
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    res1 = requests.get(f"{app_config['eventstore']['url1']}?timestamp={datastore['last_updated']}&end_timestamp={current_time}")
    res2 = requests.get(f"{app_config['eventstore']['url2']}?timestamp={datastore['last_updated']}&end_timestamp={current_time}")
    if str(res1.status_code) != '200':
        logger.error(f"Error {res1.status_code} on request for available stocks.")
    if str(res2.status_code) != '200':
        logger.error(f"Error {res2.status_code} on request for sale orders.")
    data_stocks = res1.json()
    data_orders = res2.json()
    print(data_stocks)
    print(data_orders)
    sell_orders = datastore['num_sell_orders_listed']
    data_stock_count = datastore['num_stocks_listed']
    share_prices = data_stock_count * datastore['average_stock_price']
    shares_available = datastore['total_shares_available']
    for dataset in data_stocks:
        data_stock_count += 1
        share_prices += dataset['share_price']
        shares_available += dataset['total_shares_available']
    for dataset in data_orders:
        sell_orders += 1
    
    datastore['num_sell_orders_listed'] = sell_orders
    datastore['num_stocks_listed'] = data_stock_count
    datastore['average_stock_price'] = share_prices / data_stock_count
    datastore['total_shares_available'] = shares_available
    datastore['average_shares_available_per_stock'] = shares_available / data_stock_count
    datastore['last_updated'] = current_time
    logger.info(f"Satic Periodic Statistic Calculation Results. Total_stocks_listed={datastore['num_stocks_listed']} Average_Stock_price={datastore['average_stock_price']} Total_Shares_Available={datastore['total_shares_available']} Average_Shares_Available_per_Stock={datastore['average_shares_available_per_stock']}")
    with open(app_config['datastore']['filename'], "w") as outfile:
        outfile.write(json.dumps(datastore))
    logger.info("Static Periodic Statistic Results Request Complete")
    
    
def get_stats():
    # Periodically update stats
    logger.info("Statistic GET request received.")
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            datastore = json.loads(f.read())
    except FileNotFoundError:
        logger.error(f"{app_config['datastore']['filename']} Statistics file not found.")
        return "Statistics does not exist", 404
    logger.debug(f"Current Statistics loaded. Total_stocks_listed={datastore['num_stocks_listed']} Average_Stock_price={datastore['average_stock_price']} Total_Shares_Available={datastore['total_shares_available']} Average_Shares_Available_per_Stock={datastore['average_shares_available_per_stock']}")
    logger.info(f"GET request for stats complete.")
    return datastore, 200

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(host='0.0.0.0', port=8100, use_reloader=False)
