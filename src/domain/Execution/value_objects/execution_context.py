"""执行上下文值对象"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass(frozen=True)
class ExecutionContext:
    """执行上下文值对象
    
    封装场景执行的上下文信息，包括输入参数、调用链等
    """
    scene_id: str
    trigger_source: str  # 触发来源（manual, timer, device_event）
    input_parameters: Optional[Dict[str, Any]] = None  # 输入参数
    call_chain: Optional[List[str]] = None  # 调用链（父场景ID列表）
    
    def __post_init__(self):
        """验证执行上下文数据"""
        if not self.scene_id:
            raise ValueError("场景ID不能为空")
        if not self.trigger_source:
            raise ValueError("触发来源不能为空")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "scene_id": self.scene_id,
            "trigger_source": self.trigger_source
        }
        if self.input_parameters:
            result["input_parameters"] = self.input_parameters
        if self.call_chain:
            result["call_chain"] = self.call_chain
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionContext":
        """从字典创建"""
        return cls(
            scene_id=data["scene_id"],
            trigger_source=data["trigger_source"],
            input_parameters=data.get("input_parameters"),
            call_chain=data.get("call_chain")
        )
    
    def add_to_call_chain(self, scene_id: str) -> "ExecutionContext":
        """添加到调用链（创建新实例）"""
        new_chain = list(self.call_chain) if self.call_chain else []
        new_chain.append(scene_id)
        return ExecutionContext(
            scene_id=self.scene_id,
            trigger_source=self.trigger_source,
            input_parameters=self.input_parameters,
            call_chain=new_chain
        )

