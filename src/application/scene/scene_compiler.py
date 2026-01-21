"""场景编译器

提供场景定义到可执行流程的编译功能。
此模块抽取自 main.py 和 scene_lifecycle_handler.py 中的重复逻辑。
"""

from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.Scene.aggregates.scene_aggregate import SceneAggregate


def compile_execution_flow(scene: "SceneAggregate") -> Dict[str, Any]:
    """编译场景定义为可执行的执行流程
    
    将场景的触发器、条件和动作转换为调度器可直接使用的字典格式。
    
    Args:
        scene: 场景聚合根
        
    Returns:
        执行流程字典，包含以下键:
        - scene_id: 场景ID
        - scene_name: 场景名称
        - triggers: 触发器列表
        - conditions: 条件列表
        - actions: 动作列表
    """
    if not scene.definition:
        return {
            "scene_id": scene.scene_id,
            "scene_name": scene.name,
            "triggers": [],
            "conditions": [],
            "actions": []
        }
    
    definition = scene.definition
    
    return {
        "scene_id": scene.scene_id,
        "scene_name": scene.name,
        "triggers": [t.to_dict() for t in definition.triggers],
        "conditions": [c.to_dict() for c in definition.conditions] if definition.conditions else [],
        "actions": [a.to_dict() for a in definition.actions]
    }
