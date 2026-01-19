"""设备聚合模块 - 包含所有设备类的定义"""

from .BaseDevice import BaseDevice

# 控制类设备
from .Actuators.Light import Light
from .Actuators.Switch import Switch
from .Actuators.Cover import Cover
from .Actuators.Climate import Climate
from .Actuators.Fan import Fan
from .Actuators.Lock import Lock
from .Actuators.Vacuum import Vacuum

# 传感类设备
from .Sensors.GenericSensor import GenericSensor
from .Sensors.BinarySensor import BinarySensor
from .Sensors.DeviceTracker import DeviceTracker
from .Sensors.Weather import Weather

# 多媒体与监控类设备
from .MediaSecurity.MediaPlayer import MediaPlayer
from .MediaSecurity.Camera import Camera
from .MediaSecurity.AlarmControlPanel import AlarmControlPanel

__all__ = [
    # 基类
    'BaseDevice',
    # 控制类设备
    'Light',
    'Switch',
    'Cover',
    'Climate',
    'Fan',
    'Lock',
    'Vacuum',
    # 传感类设备
    'GenericSensor',
    'BinarySensor',
    'DeviceTracker',
    'Weather',
    # 多媒体与监控类设备
    'MediaPlayer',
    'Camera',
    'AlarmControlPanel',
]

