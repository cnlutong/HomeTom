"""重试策略值对象"""

from dataclasses import dataclass
from typing import Optional
from datetime import timedelta


@dataclass(frozen=True)
class RetryPolicy:
    """重试策略值对象"""
    max_retries: int  # 最大重试次数
    retry_interval: timedelta  # 重试间隔
    backoff_multiplier: float = 1.0  # 退避乘数（用于指数退避）
    
    def __post_init__(self):
        """验证重试策略数据"""
        if self.max_retries < 0:
            raise ValueError("最大重试次数不能为负数")
        if self.retry_interval.total_seconds() < 0:
            raise ValueError("重试间隔不能为负数")
        if self.backoff_multiplier < 1.0:
            raise ValueError("退避乘数不能小于1.0")
    
    def should_retry(self, current_retry_count: int) -> bool:
        """判断是否应该重试"""
        return current_retry_count < self.max_retries
    
    def get_retry_delay(self, current_retry_count: int) -> timedelta:
        """获取重试延迟时间（支持指数退避）"""
        multiplier = self.backoff_multiplier ** current_retry_count
        return timedelta(
            seconds=self.retry_interval.total_seconds() * multiplier
        )
    
    @classmethod
    def default(cls) -> "RetryPolicy":
        """创建默认重试策略（重试3次，间隔1秒）"""
        return cls(
            max_retries=3,
            retry_interval=timedelta(seconds=1),
            backoff_multiplier=1.0
        )
    
    @classmethod
    def no_retry(cls) -> "RetryPolicy":
        """创建不重试策略"""
        return cls(
            max_retries=0,
            retry_interval=timedelta(seconds=0),
            backoff_multiplier=1.0
        )

