from config import SSID, PASSWORD, MQTT_BROKER, TOPIC, CLIENT_ID
from wifi import connect
from mqtt_client import publish_loop

connect(SSID, PASSWORD)
publish_loop(MQTT_BROKER, TOPIC, CLIENT_ID)
