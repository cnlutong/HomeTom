"""场景状态机实现

定义场景状态转换规则，确保状态迁移的合法性。
"""

from typing import List, Dict, Set
from .scene_state_machine import ISceneStateMachine
from ..aggregates.scene_aggregate import SceneStatus


class SceneStateMachine(ISceneStateMachine):
    """场景状态机实现
    
    状态转换规则：
    
    ```
        ┌──────────────────────────────────────┐
        │                                      │
        v                                      │
      DRAFT ───publish()──> PUBLISHED ───disable()──> DISABLED
        ^                       │                         │
        │                       │                         │
        │                       └────────disable()────────┤
        │                                                 │
        └─────────────────enable()────────────────────────┘
    ```
    
    有效的状态转换：
    - DRAFT → PUBLISHED (发布场景)
    - DRAFT → DISABLED (直接禁用草稿)
    - PUBLISHED → DISABLED (禁用已发布的场景)
    - DISABLED → DRAFT (重新编辑，恢复为草稿)
    
    无效的转换：
    - PUBLISHED → DRAFT (已发布不能直接变为草稿)
    - 任何状态 → 相同状态 (无操作，但不报错)
    """
    
    # 状态转换表：from_status -> [allowed_to_statuses]
    _TRANSITIONS: Dict[SceneStatus, Set[SceneStatus]] = {
        SceneStatus.DRAFT: {SceneStatus.PUBLISHED, SceneStatus.DISABLED},
        SceneStatus.PUBLISHED: {SceneStatus.DISABLED},
        SceneStatus.DISABLED: {SceneStatus.DRAFT},
    }
    
    def can_transition(self, from_status: SceneStatus, to_status: SceneStatus) -> bool:
        """检查是否可以进行状态迁移
        
        Args:
            from_status: 当前状态
            to_status: 目标状态
            
        Returns:
            是否可以迁移
        """
        # 相同状态，无需迁移
        if from_status == to_status:
            return True
        
        # 检查转换表
        allowed = self._TRANSITIONS.get(from_status, set())
        return to_status in allowed
    
    def get_allowed_transitions(self, current_status: SceneStatus) -> List[SceneStatus]:
        """获取允许的迁移目标状态列表
        
        Args:
            current_status: 当前状态
            
        Returns:
            允许迁移到的状态列表
        """
        allowed = self._TRANSITIONS.get(current_status, set())
        return list(allowed)
    
    def get_transition_action(self, from_status: SceneStatus, to_status: SceneStatus) -> str:
        """获取状态转换对应的动作名称
        
        Args:
            from_status: 当前状态
            to_status: 目标状态
            
        Returns:
            动作名称（如 "publish", "disable", "enable"）
        """
        if from_status == SceneStatus.DRAFT and to_status == SceneStatus.PUBLISHED:
            return "publish"
        elif to_status == SceneStatus.DISABLED:
            return "disable"
        elif from_status == SceneStatus.DISABLED and to_status == SceneStatus.DRAFT:
            return "enable"
        else:
            return "unknown"
    
    def validate_transition(self, from_status: SceneStatus, to_status: SceneStatus) -> None:
        """验证状态转换，如果无效则抛出异常
        
        Args:
            from_status: 当前状态
            to_status: 目标状态
            
        Raises:
            ValueError: 状态转换无效
        """
        if not self.can_transition(from_status, to_status):
            raise ValueError(
                f"无效的状态转换: {from_status.value} -> {to_status.value}。"
                f"允许的目标状态: {[s.value for s in self.get_allowed_transitions(from_status)]}"
            )


# 单例实例，方便直接使用
default_scene_state_machine = SceneStateMachine()
