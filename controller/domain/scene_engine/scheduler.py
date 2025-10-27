"""
场景调度器
使用 APScheduler 管理定时触发
"""
from typing import Callable, Dict
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore

from domain.entities.scene import Scene


class SceneScheduler:
    """场景调度器"""
    
    def __init__(self):
        # 初始化调度器（仅内存存储）
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            timezone='Asia/Shanghai'
        )
        self._job_map: Dict[str, str] = {}  # scene_id -> job_id
    
    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("✓ 场景调度器已启动")
    
    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("✓ 场景调度器已关闭")
    
    def register_scene(self, scene: Scene, callback: Callable):
        """
        注册场景的定时触发器
        
        Args:
            scene: 场景实体
            callback: 触发时的回调函数
        """
        # 移除旧的任务（如果存在）
        self.unregister_scene(scene.id)
        
        # 遍历场景的触发器
        for trigger in scene.definition.triggers:
            if trigger.get("type") == "time":
                cron_expr = trigger.get("cron")
                if cron_expr:
                    self._add_cron_job(scene.id, cron_expr, callback, scene)
    
    def _add_cron_job(
        self,
        scene_id: str,
        cron_expr: str,
        callback: Callable,
        scene: Scene
    ):
        """添加 cron 定时任务"""
        try:
            # 解析 cron 表达式
            parts = cron_expr.split()
            if len(parts) != 5:
                print(f"⚠ 无效的 cron 表达式: {cron_expr}")
                return
            
            minute, hour, day, month, day_of_week = parts
            
            # 创建触发器
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
                timezone='Asia/Shanghai'
            )
            
            # 添加任务
            job = self.scheduler.add_job(
                callback,
                trigger=trigger,
                args=[scene],
                id=f"scene_{scene_id}",
                replace_existing=True
            )
            
            self._job_map[scene_id] = job.id
            print(f"✓ 已注册场景定时任务: {scene.name} ({cron_expr})")
            
        except Exception as e:
            print(f"⚠ 注册场景定时任务失败: {scene.name}, 错误: {e}")
    
    def unregister_scene(self, scene_id: str):
        """取消注册场景"""
        job_id = self._job_map.get(scene_id)
        if job_id:
            try:
                self.scheduler.remove_job(job_id)
                del self._job_map[scene_id]
                print(f"✓ 已取消注册场景: {scene_id}")
            except Exception as e:
                print(f"⚠ 取消注册场景失败: {scene_id}, 错误: {e}")
    
    def get_scheduled_scenes(self) -> list:
        """获取所有已调度的场景"""
        return list(self._job_map.keys())

