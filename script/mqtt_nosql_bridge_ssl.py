#!/usr/bin/env python
# MIT License
# Copyright (c) 2024 Sergey B <dkc.sergey.dema@gmail.com>


import time
import paho.mqtt.client as mqtt
import ssl
import os
import logging
import boto3
import json
from systemd.daemon import notify
import signal

logger = logging.getLogger("ESP")
table = None
global run


def signals_handler(signum, frame):
    logger.info("signal is sent")
    global run
    run = False

#define callbacks
def on_connect(client, userdata, flags, rc):
    logger.info("connect, reason_code: " + str(rc))
    client.subscribe("/topic/qos1")

def on_message(client, userdata, msg):
    logger.info("new message " + str(msg.payload))
    try:
        # parse json
        parsedData = json.loads(msg.payload)
        table.put_item(
            Item={
                'ts': parsedData["ts"],
                'jsonValue': msg.payload.decode('utf-8')
            }
        )
    except json.decoder.JSONDecodeError:
        logger.error("couldn't parse: " + str(msg.payload) + ", skip")

def on_subscribe(mqttc, obj, mid, reason_code_list, properties):
    logger.info("Subscribed: " + str(mid) + " " + str(reason_code_list))


# def on_log(mqttc, obj, level, string):
    # logger.info(string)

if __name__ == "__main__":
    global run
    run = True
    signal.signal(signal.SIGINT, signals_handler)
    signal.signal(signal.SIGTERM, signals_handler)

    logging.basicConfig(level=logging.INFO)

    client=mqtt.Client(client_id="mqtt_nosql_bridge_ssl")
    client.enable_logger(logger)
    client.on_message=on_message
    # client.on_log=on_log
    client.on_connect=on_connect
    logger.info("connecting to mqqt broker")
    client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    client_context.minimum_version = ssl.TLSVersion.TLSv1_3
    client_context.maximum_version = ssl.TLSVersion.TLSv1_3
    client_context.load_verify_locations(os.environ['CA_CRT'])
    client_context.load_cert_chain(os.environ['CLIENT_CRT'], os.environ['CLIENT_KEY'])
    client.tls_set_context(client_context)
    client.tls_insecure_set(True)
    client.connect(os.environ['MQTT_URI'], 8883, 60)

    logger.info("connecting to dynamodb")
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('EspData')

    # systemd notification
    notify("READY=1")

    while run:
        rc = client.loop(timeout=1.0)
        if rc != 0:
            run = False
            logger.error("connecting to dynamodb")

    client.loop_stop()
    notify("STOPPING=1")
    logger.info("app is stopped")

