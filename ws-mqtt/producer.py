from models.demosensor import TemperatureSensor
from models.message_descriptor import MessageDescriptor
from models.device_descriptor import DeviceDescriptor
import paho.mqtt.client as mqtt
import time
import uuid

"""----------------------------------------------------------------------------------------- PARAMETERS -------------"""
client_id = "clientId0001-Producer"
broker_ip = "155.185.4.4"
broker_port = 7883
sensor_topic = "sensor/temperature"
device_base_topic = "device"
message_limit = 1000
username = "260428@studenti.unimore.it"
password = "pbuebzmjflytqjsp"
account_topic_prefix = "/iot/user/260428@studenti.unimore.it"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


# info data published on account_topic_prefix/device_base_topic/device_ID/info
def publish_device_info():
    target_topic = "{0}/{1}/{2}/info".format(account_topic_prefix, device_base_topic, device_descriptor.deviceId)
    device_payload_string = device_descriptor.to_json()
    mqtt_client.publish(target_topic, device_payload_string, 0, True)
    print(f"Device Info Published: Topic: {target_topic} Payload: {device_payload_string}")


"""---------------------------------------------------------------------------------------- MQTT CLIENT SETUP -------"""
mqtt_client = mqtt.Client(client_id)
mqtt_client.on_connect = on_connect


# Set Account Username & Password
mqtt_client.username_pw_set(username, password)


print("Connecting to "+ broker_ip + " port: " + str(broker_port))
mqtt_client.connect(broker_ip, broker_port)

mqtt_client.loop_start()

# Create Demo Temperature Sensor & Device Descriptor
temperature_sensor = TemperatureSensor()
#device_descriptor = DeviceDescriptor(str(uuid.uuid1()), "PYTHON-ACME_CORPORATION", "0.1-beta")
device_descriptor = DeviceDescriptor('mqtt-sensor-1', "PYTHON-ACME_CORPORATION", "0.1-beta")

publish_device_info()

for message_id in range(message_limit):
    # sensor data published on account_topic_prefix/device_base_topic/device_ID/sensor_topic
    temperature_sensor.measure_temperature()
    payload_string = MessageDescriptor(int(time.time()),
                                       "TEMPERATURE_SENSOR",
                                       temperature_sensor.temperature_value).to_json()

    data_topic = "{0}/{1}/{2}/{3}".format(account_topic_prefix,
                                          device_base_topic,
                                          device_descriptor.deviceId,
                                          sensor_topic)

    infot = mqtt_client.publish(data_topic, payload_string)
    infot.wait_for_publish()
    print(f"Message Sent: {message_id} Topic: {data_topic} Payload: {payload_string}")
    time.sleep(1)

mqtt_client.loop_stop()