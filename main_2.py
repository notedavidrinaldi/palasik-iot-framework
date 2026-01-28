# main.py

from palasik.core.agent import PalasikAgent
from plugins.logger.plugin import LoggerPlugin

agent = PalasikAgent()
agent.load_plugin(LoggerPlugin())

agent.start()

agent.emit_event({
    "type": "sensor",
    "value": 42
})

agent.emit_event({
    "type": "sensor",
    "value": 150
})

agent.stop()
