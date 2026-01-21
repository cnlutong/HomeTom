"""验证 Bypass Condition 功能的测试脚本"""

import sys
import asyncio
sys.path.insert(0, '/Users/tong/Desktop/code/HomeTom')

from src.domain.Scene.value_objects.condition import Condition
from src.domain.Execution.services.condition_evaluator import ConditionEvaluator, IConditionEvaluator
from src.domain.Scene.services.scene_validator_impl import SceneValidator


def test_condition_create_bypass():
    """测试 Condition.create_bypass() 工厂方法"""
    print("=" * 50)
    print("测试 1: Condition.create_bypass() 工厂方法")
    print("=" * 50)
    
    bypass = Condition.create_bypass()
    
    assert bypass.entity_id == "$system.bypass", f"Expected $system.bypass, got {bypass.entity_id}"
    assert bypass.attribute == "bypass", f"Expected bypass, got {bypass.attribute}"
    assert bypass.operator == "==", f"Expected ==, got {bypass.operator}"
    assert bypass.value == True, f"Expected True, got {bypass.value}"
    
    print(f"✅ create_bypass() 返回正确的 Condition 对象:")
    print(f"   entity_id: {bypass.entity_id}")
    print(f"   attribute: {bypass.attribute}")
    print(f"   operator: {bypass.operator}")
    print(f"   value: {bypass.value}")
    print()


async def test_condition_evaluator_bypass():
    """测试 ConditionEvaluator 对 bypass 条件的评估"""
    print("=" * 50)
    print("测试 2: ConditionEvaluator 评估 bypass 条件")
    print("=" * 50)
    
    # 创建一个 mock device manager
    class MockDeviceManager:
        async def get_device_state(self, entity_id):
            return None
        async def get_device_attributes(self, entity_id):
            return {}
        async def execute_command(self, entity_id, command, params=None):
            pass
    
    evaluator = ConditionEvaluator(MockDeviceManager())
    bypass_condition = Condition.create_bypass()
    
    result = await evaluator.evaluate_single(bypass_condition)
    
    assert result == True, f"Expected True, got {result}"
    print(f"✅ evaluate_single(bypass_condition) 返回 True")
    print()


async def test_validator_accepts_bypass():
    """测试 SceneValidator 接受 bypass 条件"""
    print("=" * 50)
    print("测试 3: SceneValidator 接受 bypass 条件")
    print("=" * 50)
    
    validator = SceneValidator()
    bypass_condition = Condition.create_bypass()
    
    errors = await validator._validate_condition(bypass_condition, 0)
    
    assert len(errors) == 0, f"Expected no errors, got {errors}"
    print(f"✅ _validate_condition(bypass) 未返回任何错误")
    print()


def run_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  Bypass Condition 功能验证")
    print("=" * 60 + "\n")
    
    try:
        # 同步测试
        test_condition_create_bypass()
        
        # 异步测试
        asyncio.run(test_condition_evaluator_bypass())
        asyncio.run(test_validator_accepts_bypass())
        
        print("=" * 60)
        print("  ✅ 所有测试通过！")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(run_tests())
