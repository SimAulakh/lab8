import connexion
import json
import os.path
import requests
import logger
import yaml
import logging.config
import datetime
from pykafka import KafkaClient

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


def get_immediate_requests(index):
    """ Get an immediate request in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logging.info("Retrieving immediate request at index %d" % index)
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            i = 0
            if msg['type'] == 'ImmediateHotelReservation':
                if i == index:
                    return msg, 200
                i += 1
            logging.info("Immediate hotels at index %d" % index)


    except:
        logging.error("No more messages found")

    logging.error("Could not find Immediate hotels at index %d" % index)
    return {"message": "Not Found"}, 404


def get_scheduled_requests(index):
    """ Get a scheduled request in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logging.info("Retrieving scheduled request at index %d" % index)
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            i = 0
            if msg['type'] == 'ScheduledHotelReservation':
                if i == index:
                    return msg, 200
                i += 1
            logging.info("Scheduled hotels at index %d" % index)
    except:
        logging.error("No more messages found")

    logging.error("Could not find scheduled hotels at index %d" % index)
    return {"message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8010, use_reloader=False)
