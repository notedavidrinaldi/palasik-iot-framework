# main_mqtt.py

from palasik.core.agent import PalasikAgent
from plugins.logger.plugin import LoggerPlugin
from palasik.adapters.mqtt.adapter import MQTTAdapter
import time

def main():
    agent = PalasikAgent(
    config_file="config.yaml"
)

    agent.load_plugins()
    agent.start()

    broker_host = agent.config.get("palasik", "broker", "host", default="localhost")
    broker_port = agent.config.get("palasik", "broker", "port", default=1883)
    topic = agent.config.get("palasik", "broker", "topic", default="palasik/#")

    mqtt_adapter = MQTTAdapter(
    agent=agent,
    broker=broker_host,
    port=broker_port,
    topic=topic
)

    mqtt_adapter.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[MAIN] Stopping PALASIK...")
    finally:
        mqtt_adapter.stop()
        agent.stop()

if __name__ == "__main__":
    main()
