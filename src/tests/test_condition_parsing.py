import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.api.routers.scene_router import AutomationCondition
from src.domain.Scene.value_objects.condition import Condition

def test_parsing():
    test_cases = [
        # New structured format
        {"type": "deviceState", "deviceId": "sensor.temp", "operator": ">=", "value": 20, "expected_op": ">=", "expected_val": 20},
        # Old string format with spaces
        {"type": "deviceState", "deviceId": "sensor.temp", "state": " >= 20 ", "expected_op": ">=", "expected_val": "20"},
        # Old string format without spaces
        {"type": "deviceState", "deviceId": "sensor.temp", "state": ">=20", "expected_op": ">=", "expected_val": "20"},
        # Equality
        {"type": "deviceState", "deviceId": "sensor.temp", "state": "on", "expected_op": "==", "expected_val": "on"},
        # Time with single value
        {"type": "time", "time": "17:00", "expected_after": "17:00", "expected_before": "17:00"},
        # Time with range
        {"type": "time", "after": "08:00", "before": "22:00", "expected_after": "08:00", "expected_before": "22:00"},
    ]

    for i, tc in enumerate(test_cases):
        c = AutomationCondition(**tc)
        
        # Mimic the logic in scene_router.py
        if c.type == "time":
            parsed = Condition.create_time_range(
                after=c.after or c.time or "00:00",
                before=c.before or c.time or "23:59"
            )
            assert parsed.value["after"] == tc["expected_after"], f"Case {i} failed after"
            assert parsed.value["before"] == tc["expected_before"], f"Case {i} failed before"
        elif c.type == "deviceState":
            if c.operator is not None and c.value is not None:
                operator = c.operator
                value = c.value
            else:
                state_str = str(c.state).strip() if c.state is not None else ""
                operator = "=="
                value = state_str
                ops = [">=", "<=", "!=", ">", "<"]
                for op_symbol in ops:
                    if state_str.startswith(op_symbol):
                        operator = op_symbol
                        value = state_str[len(op_symbol):].strip()
                        break
                    elif f" {op_symbol} " in state_str:
                        operator = op_symbol
                        value = state_str.split(f" {op_symbol} ")[1].strip()
                        break
            
            assert operator == tc["expected_op"], f"Case {i} failed op: {operator} != {tc['expected_op']}"
            assert value == tc["expected_val"], f"Case {i} failed val: {value} != {tc['expected_val']}"
            
    print("All test cases passed!")

if __name__ == "__main__":
    test_parsing()
