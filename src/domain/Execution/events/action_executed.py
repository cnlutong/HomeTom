"""动作执行事件

每个动作执行完成（成功或失败）时发布此事件。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class ActionExecuted:
    """动作执行完成领域事件
    
    每个场景动作（如灯开、灯关、设置温度等）执行完成时发布。
    """
    execution_id: str  # 所属执行ID
    scene_id: str  # 场景ID
    step_number: int  # 步骤序号
    entity_id: str  # 目标设备
    command: str  # 执行的命令（如 turn_on, set_brightness）
    success: bool  # 是否成功
    elapsed_ms: float  # 执行耗时（毫秒）
    parameters: Optional[Dict[str, Any]] = None  # 命令参数
    error_message: Optional[str] = None  # 失败时的错误信息
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.execution_id:
            raise ValueError("执行ID不能为空")
        if not self.entity_id:
            raise ValueError("设备ID不能为空")
        if not self.command:
            raise ValueError("命令不能为空")
    
    @property
    def action_description(self) -> str:
        """获取动作描述（如 "light.living_room.turn_on"）"""
        return f"{self.entity_id}.{self.command}"
