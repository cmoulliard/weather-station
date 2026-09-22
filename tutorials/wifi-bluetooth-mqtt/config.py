# Shared configuration
SSID = "MonReseauPi"
PASSWORD = "MonMotDePasse123"

# IP address of the Pi 3B+ running the MQTT Broker and HotSpot
MQTT_BROKER = "10.42.0.1"
TOPIC = "esp32c3/test"
CLIENT_ID = "ESP32C3_Client"

# Static IP config — set to None for DHCP (ESP32-C3 L2 link only works with DHCP)
STATIC_IP = None