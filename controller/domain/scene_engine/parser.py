"""
场景定义解析器
验证和解析 JSON 场景定义
"""
from typing import Dict, Any
from pydantic import ValidationError

from domain.entities.scene import SceneDefinition
from exceptions import SceneDefinitionError


class SceneParser:
    """场景解析器"""
    
    @staticmethod
    def parse(definition_data: Dict[str, Any]) -> SceneDefinition:
        """
        解析场景定义
        
        Args:
            definition_data: 场景定义字典
            
        Returns:
            SceneDefinition: 验证后的场景定义
            
        Raises:
            SceneDefinitionError: 定义格式错误
        """
        try:
            return SceneDefinition(**definition_data)
        except ValidationError as e:
            raise SceneDefinitionError(f"Invalid scene definition: {e}")
    
    @staticmethod
    def validate_trigger(trigger: Dict[str, Any]) -> bool:
        """验证触发器定义"""
        required_fields = {"type"}
        if not required_fields.issubset(trigger.keys()):
            return False
        
        trigger_type = trigger["type"]
        
        if trigger_type == "device_state":
            return "device_id" in trigger and "condition" in trigger
        elif trigger_type == "time":
            return "cron" in trigger
        elif trigger_type == "manual":
            return True
        
        return False
    
    @staticmethod
    def validate_action(action: Dict[str, Any]) -> bool:
        """验证动作定义"""
        required_fields = {"type"}
        if not required_fields.issubset(action.keys()):
            return False
        
        action_type = action["type"]
        
        if action_type == "device_control":
            return "device_id" in action and "command" in action
        elif action_type == "delay":
            return "seconds" in action
        
        return False

