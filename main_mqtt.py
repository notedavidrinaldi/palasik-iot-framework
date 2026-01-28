# main_mqtt.py

from palasik.core.agent import PalasikAgent
from plugins.logger.plugin import LoggerPlugin
from palasik.adapters.mqtt.adapter import MQTTAdapter
import time

def main():
    agent = PalasikAgent()
    agent.load_plugins()

    agent.start()

    mqtt_adapter = MQTTAdapter(
        agent=agent,
        broker="localhost",
        topic="palasik/sensor/#"
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
