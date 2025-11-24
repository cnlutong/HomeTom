"""执行日志实体"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class ExecutionLog:
    """执行日志实体
    
    记录执行过程中的详细步骤
    """
    log_id: str
    execution_id: str
    step_number: int  # 步骤序号
    action_type: str  # 动作类型（device_control, scene_call等）
    target: str  # 目标（设备entity_id或场景ID）
    command: str  # 命令
    parameters: Optional[Dict[str, Any]] = None  # 命令参数
    response: Optional[Dict[str, Any]] = None  # 响应数据
    success: bool = True  # 是否成功
    error_message: Optional[str] = None  # 错误信息
    duration_ms: Optional[float] = None  # 耗时（毫秒）
    created_at: datetime = None
    
    def __post_init__(self):
        """验证执行日志数据"""
        if not self.log_id:
            raise ValueError("日志ID不能为空")
        if not self.execution_id:
            raise ValueError("执行ID不能为空")
        if self.step_number < 1:
            raise ValueError("步骤序号必须大于0")
        if not self.action_type:
            raise ValueError("动作类型不能为空")
        if not self.target:
            raise ValueError("目标不能为空")
        if not self.command:
            raise ValueError("命令不能为空")
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def mark_success(self, response: Optional[Dict[str, Any]] = None, duration_ms: Optional[float] = None) -> None:
        """标记为成功"""
        self.success = True
        self.response = response
        self.duration_ms = duration_ms
        self.error_message = None
    
    def mark_failed(self, error_message: str, duration_ms: Optional[float] = None) -> None:
        """标记为失败"""
        self.success = False
        self.error_message = error_message
        self.duration_ms = duration_ms
        self.response = None

