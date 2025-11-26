"""场景校验器实现"""

from typing import List, Set
from .scene_validator import ISceneValidator
from ..value_objects.scene_definition import SceneDefinition
from ..value_objects.trigger import TriggerType
from ..value_objects.action import ActionType
from ..value_objects.condition import Condition


class SceneValidator(ISceneValidator):
    """场景校验器实现
    
    提供场景定义的校验和循环依赖检测功能
    """
    
    async def validate_definition(self, definition: SceneDefinition) -> List[str]:
        """校验场景定义
        
        Args:
            definition: 场景定义
            
        Returns:
            错误信息列表，如果为空则表示校验通过
        """
        errors = []
        
        # 1. 校验触发器
        if not definition.triggers:
            errors.append("场景必须至少有一个触发器")
        else:
            for idx, trigger in enumerate(definition.triggers):
                trigger_errors = self._validate_trigger(trigger, idx)
                errors.extend(trigger_errors)
        
        # 2. 校验条件
        if definition.conditions:
            for idx, condition in enumerate(definition.conditions):
                condition_errors = self._validate_condition(condition, idx)
                errors.extend(condition_errors)
        
        # 3. 校验动作
        if not definition.actions:
            errors.append("场景必须至少有一个动作")
        else:
            for idx, action in enumerate(definition.actions):
                action_errors = self._validate_action(action, idx)
                errors.extend(action_errors)
        
        return errors
    
    def _validate_trigger(self, trigger, idx: int) -> List[str]:
        """校验单个触发器"""
        errors = []
        prefix = f"触发器[{idx}]"
        
        if trigger.type == TriggerType.TIMER:
            # 校验定时器配置
            if "schedule" not in trigger.config:
                errors.append(f"{prefix}: 定时器触发器必须包含schedule配置")
            elif not trigger.config["schedule"]:
                errors.append(f"{prefix}: schedule配置不能为空")
        
        elif trigger.type == TriggerType.DEVICE_EVENT:
            # 校验设备事件配置
            if "entity_id" not in trigger.config:
                errors.append(f"{prefix}: 设备事件触发器必须包含entity_id配置")
            elif not trigger.config["entity_id"]:
                errors.append(f"{prefix}: entity_id配置不能为空")
            
            if "event_type" not in trigger.config:
                errors.append(f"{prefix}: 设备事件触发器必须包含event_type配置")
            elif not trigger.config["event_type"]:
                errors.append(f"{prefix}: event_type配置不能为空")
        
        elif trigger.type == TriggerType.MANUAL:
            # 手动触发无需额外配置
            pass
        
        return errors
    
    def _validate_condition(self, condition: Condition, idx: int) -> List[str]:
        """校验单个条件"""
        errors = []
        prefix = f"条件[{idx}]"
        
        # 校验实体ID
        if not condition.entity_id:
            errors.append(f"{prefix}: 实体ID不能为空")
        
        # 校验属性名
        if not condition.attribute:
            errors.append(f"{prefix}: 属性名不能为空")
        
        # 校验操作符
        valid_operators = ["==", "!=", ">", "<", ">=", "<=", "in", "not_in"]
        if condition.operator not in valid_operators:
            errors.append(
                f"{prefix}: 操作符'{condition.operator}'无效，"
                f"有效的操作符为: {', '.join(valid_operators)}"
            )
        
        # 校验值
        if condition.value is None:
            errors.append(f"{prefix}: 比较值不能为None")
        
        return errors
    
    def _validate_action(self, action, idx: int) -> List[str]:
        """校验单个动作"""
        errors = []
        prefix = f"动作[{idx}]"
        
        # 校验目标
        if not action.target:
            errors.append(f"{prefix}: 目标不能为空")
        
        # 校验命令
        if not action.command:
            errors.append(f"{prefix}: 命令不能为空")
        
        # 根据动作类型进行额外校验
        if action.type == ActionType.DEVICE_CONTROL:
            # 设备控制动作的命令校验
            valid_commands = [
                "turn_on", "turn_off", "toggle",
                "set_brightness", "set_color", "set_temperature"
            ]
            if action.command not in valid_commands:
                errors.append(
                    f"{prefix}: 设备控制命令'{action.command}'可能无效，"
                    f"常见命令: {', '.join(valid_commands)}"
                )
        
        elif action.type == ActionType.SCENE_CALL:
            # 场景调用动作
            if action.command != "execute":
                errors.append(f"{prefix}: 场景调用命令必须为'execute'")
        
        return errors
    
    async def check_circular_dependency(
        self,
        scene_id: str,
        definition: SceneDefinition,
        existing_scenes: List[str]
    ) -> bool:
        """检查循环依赖
        
        Args:
            scene_id: 当前场景ID
            definition: 场景定义
            existing_scenes: 已存在的场景ID列表（用于检查依赖）
            
        Returns:
            如果存在循环依赖返回True，否则返回False
        """
        # 获取当前场景引用的所有子场景
        referenced_scenes = definition.get_referenced_scenes()
        
        # 检查是否引用了自己（直接循环）
        if scene_id in referenced_scenes:
            return True
        
        # 检查是否存在间接循环依赖
        # 注意: 在MVP阶段，由于没有存储库来查询其他场景的定义，
        # 这里只能进行简单的直接循环检测
        # 完整的循环依赖检测需要递归遍历所有被引用场景的定义
        # 这需要依赖于场景仓储(SceneRepository)来获取其他场景的定义
        
        # TODO: 在后续迭代中，实现完整的循环依赖检测
        # 需要注入SceneRepository并递归检查依赖链
        
        return False
    
    def _check_circular_dependency_recursive(
        self,
        current_scene_id: str,
        target_scene_id: str,
        visited: Set[str],
        scene_definitions: dict
    ) -> bool:
        """递归检查循环依赖（预留方法）
        
        Args:
            current_scene_id: 当前检查的场景ID
            target_scene_id: 原始目标场景ID
            visited: 已访问的场景ID集合
            scene_definitions: 场景ID到定义的映射
            
        Returns:
            如果存在循环依赖返回True
        """
        # 如果当前场景已经访问过，说明存在循环
        if current_scene_id in visited:
            return True
        
        # 如果当前场景不存在，无法继续检查
        if current_scene_id not in scene_definitions:
            return False
        
        # 标记为已访问
        visited.add(current_scene_id)
        
        # 获取当前场景的定义
        definition = scene_definitions[current_scene_id]
        referenced_scenes = definition.get_referenced_scenes()
        
        # 递归检查所有被引用的场景
        for scene_id in referenced_scenes:
            if scene_id == target_scene_id:
                return True  # 找到循环
            if self._check_circular_dependency_recursive(
                scene_id, target_scene_id, visited.copy(), scene_definitions
            ):
                return True
        
        return False
