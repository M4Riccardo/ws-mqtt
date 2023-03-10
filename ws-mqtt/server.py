from models.device_descriptor import DeviceDescriptor
from models.message_descriptor import MessageDescriptor, WebSocketMessageDescriptor
import paho.mqtt.client as mqtt
import json
import asyncio
import websockets
import logging


"""------------------------------------------------------------------------------------------- PARAMETERS -----------"""
# MQTT parameters
client_id = "clientId0001-Consumer"
broker_ip = "155.185.4.4"
broker_port = 7883
username = "260428@studenti.unimore.it"
password = "pbuebzmjflytqjsp"
account_topic_prefix = "/iot/user/260428@studenti.unimore.it/"
device_info_topic = account_topic_prefix + "device/+/info"
data_topic = account_topic_prefix + "device/+/sensor/#"
message_limit = 1000

# websocket parameters
logging.basicConfig(level=logging.INFO)
local_host_port = 8765
websocket_MQTT_message = WebSocketMessageDescriptor('null', 'null', 0, 'MQTT')


"""--------------------------------------------------------------------------------- MQTT CLIENT SETUP --------------"""


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    mqtt_client.subscribe(device_info_topic)
    print("Subscribed to: " + device_info_topic)
    mqtt_client.subscribe(data_topic)
    print("Subscribed to: " + data_topic)


def on_message(client, userdata, message):
    if mqtt.topic_matches_sub(device_info_topic, message.topic):
        message_payload = str(message.payload.decode("utf-8"))
        device_descriptor = DeviceDescriptor(**json.loads(message_payload))
        print(f"Received IoT Message (Retained:{message.retain}): "
              f"Topic: {message.topic} "
              f"DeviceId: {device_descriptor.deviceId} "
              f"Manufacturer: {device_descriptor.producer} "
              f"SoftwareVersion: {device_descriptor.softwareVersion}")
        websocket_MQTT_message.deviceId = device_descriptor.deviceId

    elif mqtt.topic_matches_sub(data_topic, message.topic):
        message_payload = str(message.payload.decode("utf-8"))
        message_descriptor = MessageDescriptor(**json.loads(message_payload))
        print(f"Received IoT Message: Topic: {message.topic} "
              f"Timestamp: {message_descriptor.timestamp} "
              f"Type: {message_descriptor.type} "
              f"Value: {message_descriptor.value}")
        websocket_MQTT_message.type = message_descriptor.type
        websocket_MQTT_message.value = message_descriptor.value
    else:
        print("Unmanaged Topic !")


mqtt_client = mqtt.Client(client_id)

# Attack Paho OnMessage Callback Method
mqtt_client.on_message = on_message
mqtt_client.on_connect = on_connect


# Set Account Username & Password
mqtt_client.username_pw_set(username, password)


# Connect to the target MQTT Broker
mqtt_client.connect(broker_ip, broker_port)


"""------------------------------------------------------------------------------- WEBSOCKET SERVER SETUP -----------"""


async def websocket_handler(websocket, path):
    while True:
        message = await websocket.recv()
        print(message)

        response = f"data: {websocket_MQTT_message.to_json()}"
        await websocket.send(response)


# Webserver Configuration
start_server = websockets.serve(websocket_handler, "localhost", local_host_port)


# Start MQTT loop
mqtt_client.loop_start()

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
