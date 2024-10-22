import paho.mqtt.client as mqtt

MQTT_BROKER = "192.168.102.12" # MQTT Broker in dev post
# MQTT_BROKER = "localhost"


# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.publish("test/topic", "Hello, MQTT!")

client = mqtt.Client()
client.on_connect = on_connect

client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()