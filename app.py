import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
import uuid
import datetime
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from flask_cors import CORS, cross_origin
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

def get_health():
    return 200

def get_device_event(index):
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving device event at index %d" % index)
    try:
        event_list = []
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == "device":
                event_list.append(msg)
        response_payload = event_list[index]['payload']
        return response_payload, 200
    except:
        logger.error("No more messages found")
    logger.error("Could not find device event at index %d" % index)
    return {"message": "Not Found"}, 404


def get_network_event(index):
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving network event at index %d" % index)
    try:
        event_list = []
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == "network":
                event_list.append(msg)
        response_payload = event_list[index]['payload']
        return response_payload, 200
    except:
        logger.error("No more messages found")
    logger.error("Could not find network event at index %d" % index)
    return {"message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')

app.add_api("openapi.yml",
            base_path="/audit_log",
            strict_validation=True,
            validate_responses=True)

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    # app.debug = True
    app.run(port=8110)

