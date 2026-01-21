"""设备聚合根与 ORM 模型的映射器"""

from typing import Optional
from src.domain.Device.aggregates.device_aggregate import DeviceAggregate
from src.domain.Device.value_objects.device_status import DeviceStatus
from src.domain.Device.value_objects.device_capability import (
    DeviceCapabilities,
    DeviceCapability,
)
from ..models.device_model import DeviceModel


class DeviceMapper:
    """设备映射器
    
    负责 DeviceAggregate 与 DeviceModel 之间的双向转换
    保持领域层的纯净性，转换逻辑在此处理
    """
    
    @staticmethod
    def to_model(aggregate: DeviceAggregate) -> DeviceModel:
        """将聚合根转换为 ORM 模型
        
        Args:
            aggregate: 设备聚合根
            
        Returns:
            设备 ORM 模型
        """
        # 将能力集合序列化为 JSON 格式
        capabilities_data = {
            "capabilities": [
                {
                    "name": cap.name,
                    "value_type": cap.value_type,
                    "constraints": cap.constraints,
                    "description": cap.description,
                }
                for cap in aggregate.capabilities.get_all()
            ]
        }
        
        return DeviceModel(
            id=aggregate.device_id,
            entity_id=aggregate.entity_id,
            name=aggregate.name,
            adapter_type=aggregate.adapter_type,
            manufacturer=aggregate.manufacturer,
            capabilities=capabilities_data,
            status=aggregate.status.value,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
    
    @staticmethod
    def to_aggregate(model: DeviceModel) -> DeviceAggregate:
        """将 ORM 模型转换为聚合根
        
        Args:
            model: 设备 ORM 模型
            
        Returns:
            设备聚合根
            
        Note:
            从数据库恢复时，不会触发领域事件
        """
        # 从 JSON 反序列化能力集合
        capabilities_data = model.capabilities.get("capabilities", [])
        capabilities = DeviceCapabilities([
            DeviceCapability(
                name=cap["name"],
                value_type=cap.get("value_type", "void"),
                constraints=cap.get("constraints") or cap.get("parameters"),
                description=cap.get("description"),
            )
            for cap in capabilities_data
        ])
        
        # 直接构造聚合根，绕过工厂方法（不触发创建事件）
        return DeviceAggregate(
            device_id=model.id,
            entity_id=model.entity_id,
            name=model.name,
            adapter_type=model.adapter_type,
            manufacturer=model.manufacturer,
            capabilities=capabilities,
            status=DeviceStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def update_model(model: DeviceModel, aggregate: DeviceAggregate) -> None:
        """用聚合根数据更新 ORM 模型（就地更新）
        
        Args:
            model: 需要更新的 ORM 模型
            aggregate: 聚合根数据源
        """
        capabilities_data = {
            "capabilities": [
                {
                    "name": cap.name,
                    "value_type": cap.value_type,
                    "constraints": cap.constraints,
                    "description": cap.description,
                }
                for cap in aggregate.capabilities.get_all()
            ]
        }
        
        model.entity_id = aggregate.entity_id
        model.name = aggregate.name
        model.adapter_type = aggregate.adapter_type
        model.manufacturer = aggregate.manufacturer
        model.capabilities = capabilities_data
        model.status = aggregate.status.value
        model.updated_at = aggregate.updated_at
