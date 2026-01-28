# palasik/adapters/mqtt/adapter.py

import json
import paho.mqtt.client as mqtt

class MQTTAdapter:
    """
    MQTT Adapter untuk PALASIK.
    Mengubah pesan MQTT menjadi event PALASIK.
    """

    def __init__(
        self,
        agent,
        broker="localhost",
        port=1883,
        topic="palasik/sensor/#"
    ):
        self.agent = agent
        self.broker = broker
        self.port = port
        self.topic = topic

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("[MQTT] Connected with result code", rc)
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            data = json.loads(payload)

            event = {
                "type": "mqtt",
                "topic": msg.topic,
                "value": data.get("value"),
                "raw": data
            }

            self.agent.emit_event(event)

        except Exception as e:
            print("[MQTT] Error processing message:", e)

    def start(self):
        print("[MQTT] Starting adapter...")
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def stop(self):
        print("[MQTT] Stopping adapter...")
        self.client.loop_stop()
        self.client.disconnect()
