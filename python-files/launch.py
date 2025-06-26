import json
from utils.validate_config import validate_config
from utils.parser import load_rules
from copilot_engine.core_logic import CoPilotPlusEngine

def load_threshold():
    try:
        with open("config/confidence_threshold.json") as f:
            return json.load(f).get("threshold", 0.5)
    except:
        return 0.5

if __name__ == "__main__":
    validate_config()
    rules = load_rules("example_rules.yaml")
    engine = CoPilotPlusEngine(rules)
    input_data = {"type": "greeting"}
    result = engine.process(input_data)
    print(result)
