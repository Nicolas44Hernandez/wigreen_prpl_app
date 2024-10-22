import paho.mqtt.client as mqtt

MQTT_BROKER = "192.168.102.12" # MQTT Broker in dev post
# MQTT_BROKER = "localhost"

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

# Callback when a message is received
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic: {msg.topic}")


client = mqtt.Client()
client.on_message = on_message
client.on_connect = on_connect

client.connect(MQTT_BROKER, 1883, 60)
client.subscribe("test/topic")

client.loop_forever()