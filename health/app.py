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
    print("In Test Environment ")
    app_conf_file = "/config/health/app_conf.yml"
    log_conf_file = "/config/health/log_conf.yml"
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
    logger.info("Periodic Health Check Started...")
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    status1 = "Stopped."
    status2 = "Stopped."
    status3 = "Stopped."
    status4 = "Stopped."
    # Check file
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            datastore = json.loads(f.read())
    except FileNotFoundError:
        logger.error(f"{app_config['datastore']['filename']} Statistics file not found.")
        with open(app_config['datastore']['filename'], 'w+') as f:
            file_data = {"receiver": "Stopped","processing": "Stopped", "storage": "Stopped", "audit": "Stopped", "last_updated": "2023-10-10T10:52:57.000Z"}
            f.write(json.dumps(file_data))
        return
    # Response 1
    try:
        res1 = requests.get(f"{app_config['eventstore']['url1']}")
        if str(res1.status_code) != '200':
            logger.error(f"Error {res1.status_code} on request for health status.")
        else:
            logger.info(f"{app_config['eventstore']['url1NAME'] } health check response received and service is running.")
            status1 = "Running."
    except TimeoutError:
        logger.error(f"Error, request timed out for {app_config['eventstore']['url1NAME']}")
    # Response 2
    try:
        res2 = requests.get(f"{app_config['eventstore']['url2']}")
        if str(res2.status_code) != '200':
            logger.error(f"Error {res2.status_code} on request for available stocks.")
        else:
            logger.info(f"{app_config['eventstore']['url2NAME'] } health check response received and service is running.")
            status2 = "Running."
    except TimeoutError:
        logger.error(f"Error, request timed out for {app_config['eventstore']['url2NAME']}")
    # Response 3
    try:
        res3 = requests.get(f"{app_config['eventstore']['url3']}")
        if str(res3.status_code) != '200':
            logger.error(f"Error {res3.status_code} on request for available stocks.")
        else:
            logger.info(f"{app_config['eventstore']['url3NAME'] } health check response received and service is running.")
            status3 = "Running."
    except TimeoutError:
        logger.error(f"Error, request timed out for {app_config['eventstore']['url3NAME']}")
    # Response 4
    try:
        res4 = requests.get(f"{app_config['eventstore']['url4']}")
        if str(res4.status_code) != '200':
            logger.error(f"Error {res4.status_code} on request for available stocks.")
        else:
            logger.info(f"{app_config['eventstore']['url4NAME'] } health check response received and service is running.")
            status4 = "Running."
    except TimeoutError:
        logger.error(f"Error, request timed out for {app_config['eventstore']['url4NAME']}")
    # Write to file
    file_data = {app_config['eventstore']['url1']: status1, app_config['eventstore']['url2NAME']: status2, app_config['eventstore']['url3NAME']: status3, app_config['eventstore']['url4NAME']: status4, "last_updated": current_time}
    try:
        with open(app_config['datastore']['filename'], 'w') as f:
            f.write(json.dumps(file_data))
    except:
        logger.error("ERROR: Unable to write health status to file.")
        
    logger.info(f"{file_data}")
    logger.info("Periodic Health Check Complete")

def get_stats():
    # Called every 20 seconds
    # Periodically update stats
    logger.info("Health satus GET request received.")
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            datastore = json.loads(f.read())
    except FileNotFoundError:
        logger.error(f"{app_config['datastore']['filename']} health status file not found.")
        return "Health status does not exist", 404
    logger.debug(f"Health Status: {datastore}")
    logger.info(f"GET request for health status complete.")
    return datastore, 200

app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", base_path='/processing', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(host='0.0.0.0', port=8100, use_reloader=False)
