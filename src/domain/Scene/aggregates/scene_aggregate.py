"""场景聚合根"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from ..value_objects.scene_definition import SceneDefinition
from ..events.scene_published import ScenePublished
from ..events.scene_disabled import SceneDisabled


class SceneStatus(Enum):
    """场景状态枚举"""
    DRAFT = "draft"  # 草稿
    PUBLISHED = "published"  # 已发布
    DISABLED = "disabled"  # 已禁用


class SceneAggregate:
    """场景聚合根
    
    封装场景的核心业务逻辑，维护场景的一致性边界
    """
    
    def __init__(
        self,
        scene_id: str,
        name: str,
        description: Optional[str] = None,
        status: SceneStatus = SceneStatus.DRAFT,
        definition: Optional[SceneDefinition] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """初始化场景聚合根
        
        Args:
            scene_id: 场景唯一标识
            name: 场景名称
            description: 场景描述
            status: 场景状态
            definition: 场景定义（MVP阶段直接存储在聚合根中）
            created_at: 创建时间
            updated_at: 更新时间
        """
        if not scene_id:
            raise ValueError("场景ID不能为空")
        if not name:
            raise ValueError("场景名称不能为空")
        
        self._scene_id = scene_id
        self._name = name
        self._description = description
        self._status = status
        self._definition = definition
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        
        # 领域事件列表
        self._domain_events: List[object] = []
    
    @property
    def scene_id(self) -> str:
        """获取场景ID"""
        return self._scene_id
    
    @property
    def name(self) -> str:
        """获取场景名称"""
        return self._name
    
    @property
    def description(self) -> Optional[str]:
        """获取场景描述"""
        return self._description
    
    @property
    def status(self) -> SceneStatus:
        """获取场景状态"""
        return self._status
    
    @property
    def definition(self) -> Optional[SceneDefinition]:
        """获取场景定义"""
        return self._definition
    
    @property
    def created_at(self) -> datetime:
        """获取创建时间"""
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        """获取更新时间"""
        return self._updated_at
    
    def update_name(self, name: str) -> None:
        """更新场景名称"""
        if not name:
            raise ValueError("场景名称不能为空")
        self._name = name
        self._updated_at = datetime.utcnow()
    
    def update_description(self, description: Optional[str]) -> None:
        """更新场景描述"""
        self._description = description
        self._updated_at = datetime.utcnow()
    
    def update_definition(self, definition: SceneDefinition) -> None:
        """更新场景定义
        
        Args:
            definition: 新的场景定义
        """
        if not definition:
            raise ValueError("场景定义不能为空")
        
        self._definition = definition
        self._updated_at = datetime.utcnow()
    
    def publish(self) -> None:
        """发布场景
        
        将场景状态从草稿迁移到已发布
        """
        if self._status == SceneStatus.PUBLISHED:
            return  # 已经是发布状态，无需操作
        
        if self._status == SceneStatus.DISABLED:
            raise ValueError("已禁用的场景不能直接发布，需要先启用")
        
        if not self._definition:
            raise ValueError("场景必须有定义才能发布")
        
        self._status = SceneStatus.PUBLISHED
        self._updated_at = datetime.utcnow()
        
        # 发布领域事件
        event = ScenePublished(
            scene_id=self._scene_id,
            version_number=1,  # MVP阶段始终为版本1
            definition=self._definition,
            occurred_at=datetime.utcnow()
        )
        self._add_domain_event(event)
    
    def disable(self) -> None:
        """禁用场景"""
        if self._status == SceneStatus.DISABLED:
            return  # 已经是禁用状态，无需操作
        
        self._status = SceneStatus.DISABLED
        self._updated_at = datetime.utcnow()
        
        # 发布领域事件
        event = SceneDisabled(
            scene_id=self._scene_id,
            occurred_at=datetime.utcnow()
        )
        self._add_domain_event(event)
    
    def get_domain_events(self) -> List[object]:
        """获取领域事件列表"""
        return list(self._domain_events)
    
    def clear_domain_events(self) -> None:
        """清除领域事件列表"""
        self._domain_events.clear()
    
    def _add_domain_event(self, event: object) -> None:
        """添加领域事件"""
        self._domain_events.append(event)
    
    @classmethod
    def create(
        cls,
        scene_id: str,
        name: str,
        description: Optional[str] = None
    ) -> "SceneAggregate":
        """工厂方法：创建新场景
        
        新场景默认状态为草稿
        """
        return cls(
            scene_id=scene_id,
            name=name,
            description=description,
            status=SceneStatus.DRAFT
        )
    
    def __eq__(self, other) -> bool:
        """相等性比较"""
        if not isinstance(other, SceneAggregate):
            return False
        return self._scene_id == other._scene_id
    
    def __hash__(self) -> int:
        """哈希值"""
        return hash(self._scene_id)

