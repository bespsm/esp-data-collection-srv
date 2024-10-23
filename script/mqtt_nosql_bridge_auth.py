#!/usr/bin/env python3
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

dbName = 'espData'
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

def on_subscribe(client, userdata, mid, granted_qos):
    logger.info("Subscribed to qos: " + ' '.join(str(e) for e in granted_qos))


# def on_log(mqttc, obj, level, string):
    # logger.info(string)

if __name__ == "__main__":
    global run
    run = True
    signal.signal(signal.SIGINT, signals_handler)
    signal.signal(signal.SIGTERM, signals_handler)

    logging.basicConfig(level=logging.INFO)

    client=mqtt.Client(client_id="mqtt_nosql_bridge")
    client.enable_logger(logger)
    client.on_message=on_message
    # client.on_log=on_log
    client.on_connect=on_connect
    logger.info("connecting to mqqt broker")
    client.username_pw_set(os.environ['USER_ID'], os.environ['USER_PASS'])
    client.connect("localhost", port=1883, keepalive=60)

    logger.info("connecting to dynamodb")
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dbName)

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

