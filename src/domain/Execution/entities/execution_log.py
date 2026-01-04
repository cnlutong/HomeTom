"""执行日志实体

记录场景执行过程中每个动作步骤的详细信息。
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class ExecutionLog:
    """执行日志实体
    
    记录场景执行过程中每个动作步骤的执行详情，包括：
    - 步骤序号
    - 目标设备
    - 执行命令
    - 执行结果
    - 耗时等
    """
    
    log_id: str
    execution_id: str
    step_number: int
    action_type: str  # device_control, scene_call
    target: str  # 目标设备 entity_id 或场景 ID
    command: str  # 命令名称
    parameters: Optional[Dict[str, Any]] = None  # 命令参数
    response: Optional[Dict[str, Any]] = None  # 执行响应
    duration_ms: int = 0  # 执行耗时（毫秒）
    success: bool = True  # 是否成功
    error_message: Optional[str] = None  # 错误信息
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """验证日志数据"""
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
    
    @classmethod
    def create(
        cls,
        execution_id: str,
        step_number: int,
        action_type: str,
        target: str,
        command: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> "ExecutionLog":
        """工厂方法：创建新的执行日志
        
        Args:
            execution_id: 执行ID
            step_number: 步骤序号
            action_type: 动作类型
            target: 目标（设备或场景）
            command: 命令名称
            parameters: 命令参数
            
        Returns:
            新的执行日志实例
        """
        return cls(
            log_id=str(uuid.uuid4()),
            execution_id=execution_id,
            step_number=step_number,
            action_type=action_type,
            target=target,
            command=command,
            parameters=parameters,
            created_at=datetime.utcnow()
        )
    
    def complete(
        self,
        success: bool,
        response: Optional[Dict[str, Any]] = None,
        duration_ms: int = 0,
        error_message: Optional[str] = None
    ) -> "ExecutionLog":
        """标记日志完成
        
        由于 dataclass 是不可变的模式下无法直接修改，
        这里返回一个新的实例包含完成信息。
        
        Args:
            success: 是否成功
            response: 执行响应
            duration_ms: 执行耗时
            error_message: 错误信息
            
        Returns:
            更新后的执行日志实例
        """
        return ExecutionLog(
            log_id=self.log_id,
            execution_id=self.execution_id,
            step_number=self.step_number,
            action_type=self.action_type,
            target=self.target,
            command=self.command,
            parameters=self.parameters,
            response=response,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
            created_at=self.created_at
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "log_id": self.log_id,
            "execution_id": self.execution_id,
            "step_number": self.step_number,
            "action_type": self.action_type,
            "target": self.target,
            "command": self.command,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat()
        }
        if self.parameters:
            result["parameters"] = self.parameters
        if self.response:
            result["response"] = self.response
        if self.error_message:
            result["error_message"] = self.error_message
        return result
    
    def __eq__(self, other) -> bool:
        """相等性比较"""
        if not isinstance(other, ExecutionLog):
            return False
        return self.log_id == other.log_id
    
    def __hash__(self) -> int:
        """哈希值"""
        return hash(self.log_id)
