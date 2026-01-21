"""设备能力值对象"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass(frozen=True)
class DeviceCapability:
    """设备能力描述值对象
    
    表示设备支持的操作，如 turn_on, turn_off, set_brightness 等
    """
    name: str  # 能力名称，如 "turn_on", "set_brightness"
    value_type: str = "void"  # 值类型: void, boolean, int, float, string, enum
    constraints: Optional[Dict[str, Any]] = None  # 约束条件: min, max, options 等
    description: Optional[str] = None  # 能力描述
    
    def __post_init__(self):
        """验证能力名称"""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("能力名称不能为空且必须是字符串")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "name": self.name,
            "value_type": self.value_type
        }
        if self.constraints:
            result["constraints"] = self.constraints
        if self.description:
            result["description"] = self.description
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceCapability":
        """从字典创建"""
        # 兼容旧代码，如果没有 value_type 只有 parameters，进行简单转换
        val_type = data.get("value_type", "void")
        constraints = data.get("constraints") or data.get("parameters")
        
        return cls(
            name=data["name"],
            value_type=val_type,
            constraints=constraints,
            description=data.get("description")
        )


class DeviceCapabilities:
    """设备能力集合
    
    封装设备的所有能力，提供便捷的查询方法
    """
    
    def __init__(self, capabilities: List[DeviceCapability]):
        """初始化能力集合"""
        self._capabilities: Dict[str, DeviceCapability] = {
            cap.name: cap for cap in capabilities
        }
    
    def has_capability(self, name: str) -> bool:
        """检查是否支持某个能力"""
        return name in self._capabilities
    
    def get_capability(self, name: str) -> Optional[DeviceCapability]:
        """获取指定能力"""
        return self._capabilities.get(name)
    
    def get_all(self) -> List[DeviceCapability]:
        """获取所有能力"""
        return list(self._capabilities.values())
    
    def to_list(self) -> List[Dict[str, Any]]:
        """转换为列表（用于序列化）"""
        return [cap.to_dict() for cap in self._capabilities.values()]
    
    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "DeviceCapabilities":
        """从列表创建"""
        capabilities = [DeviceCapability.from_dict(item) for item in data]
        return cls(capabilities)
    
    def __len__(self) -> int:
        return len(self._capabilities)
    
    def __iter__(self):
        return iter(self._capabilities.values())

