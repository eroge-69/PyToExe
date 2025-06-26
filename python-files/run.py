from copilot_engine.core_logic import CoPilotPlusEngine
from utils.parser import load_rules

rules = load_rules("example_rules.yaml")
engine = CoPilotPlusEngine(rules)
input_data = {"type": "greeting"}
print(engine.process(input_data))
