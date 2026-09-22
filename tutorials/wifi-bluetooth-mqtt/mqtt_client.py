from umqtt.simple import MQTTClient
import time


def publish_loop(broker, topic, client_id="ESP32C3_Client"):
    """Connect to MQTT broker and publish messages in a loop."""
    print("Connecting to MQTT broker ...")
    client = MQTTClient(client_id=client_id, server=broker)

    try:
        client.connect()
        print("MQTT connected to the local server !")

        counter = 0
        while True:
            message = f"Hello local MQTT ! Message numero {counter}"
            print("Send :", message)
            client.publish(topic, message)
            counter += 1
            time.sleep(5)

    except Exception as e:
        print("MQTT connection error:", e)