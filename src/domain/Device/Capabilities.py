from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Set, TYPE_CHECKING
from .value_objects.device_capability import DeviceCapability

class SwitchableMixin:
    """可开关能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, '_capabilities'):
            self._capabilities._capabilities["turn_on"] = DeviceCapability("turn_on")
            self._capabilities._capabilities["turn_off"] = DeviceCapability("turn_off")
            self._capabilities._capabilities["toggle"] = DeviceCapability("toggle")
        self.attributes.setdefault("state", "off")

    def turn_on(self):
        self._state = "on"
        self.attributes["state"] = "on"
        # 实际执行逻辑应由具体驱动或服务处理
        print(f"Device {self.get_entity_id()} turned ON")

    def turn_off(self):
        self._state = "off"
        self.attributes["state"] = "off"
        # 实际执行逻辑应由具体驱动或服务处理
        print(f"Device {self.get_entity_id()} turned OFF")

    def toggle(self):
        if self._state == "on":
            self.turn_off()
        else:
            self.turn_on()

class DimmableMixin:
    """可调光能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, '_capabilities'):
            self._capabilities._capabilities["set_brightness"] = DeviceCapability(
                "set_brightness", 
                parameters={"min": 0, "max": 100}
            )
        self.attributes.setdefault("brightness", 0)

    def set_brightness(self, level: int):
        level = max(0, min(100, level))
        self.attributes["brightness"] = level
        print(f"Device {self.get_entity_id()} brightness set to {level}")

class TemperatureMixin:
    """温度感应能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, '_capabilities'):
            self._capabilities._capabilities["temperature_report"] = DeviceCapability("temperature_report")
        self.attributes.setdefault("temperature", None)

    def get_temperature(self):
        return self.attributes.get("temperature")

class SensorMixin:
    """通用传感器能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 传感器通常不提供命令，只提供属性
        self.attributes.setdefault("value", None)
        self.attributes.setdefault("unit", None)

    def set_value(self, value: Any, unit: Optional[str] = None):
        self.attributes["value"] = value
        if unit:
            self.attributes["unit"] = unit
        self._state = str(value)

class BinaryStateMixin:
    """二元状态能力特征 (门窗、运动等)"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, '_capabilities'):
            # 虽然是只读传感器，但有时我们希望它能模拟触发
            self._capabilities._capabilities["trigger_test"] = DeviceCapability("trigger_test")
        self.attributes.setdefault("binary_state", False)

    def set_binary_state(self, state: bool):
        self.attributes["binary_state"] = state
        self._state = "on" if state else "off"

class ClimateMixin:
    """温控能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, '_capabilities'):
            self._capabilities._capabilities["set_temperature"] = DeviceCapability("set_temperature")
            self._capabilities._capabilities["set_mode"] = DeviceCapability("set_mode")
        self.attributes.setdefault("temperature", 20.0)
        self.attributes.setdefault("current_temperature", 20.0)
        self.attributes.setdefault("mode", "auto")

    def set_temperature(self, temperature: float):
        self.attributes["temperature"] = temperature
        print(f"Device {self.get_entity_id()} target temperature set to {temperature}")

    def set_mode(self, mode: str):
        self.attributes["mode"] = mode
        print(f"Device {self.get_entity_id()} mode set to {mode}")

class CoverMixin:
    """窗帘/遮蔽能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, '_capabilities'):
            self._capabilities._capabilities["set_position"] = DeviceCapability(
                "set_position",
                parameters={"min": 0, "max": 100}
            )
            self._capabilities._capabilities["open_cover"] = DeviceCapability("open_cover")
            self._capabilities._capabilities["close_cover"] = DeviceCapability("close_cover")
        self.attributes.setdefault("position", 0)

    def set_position(self, position: int):
        self.attributes["position"] = position
        print(f"Device {self.get_entity_id()} position set to {position}")

    def open_cover(self):
        self.set_position(100)
        print(f"Device {self.get_entity_id()} opening")

    def close_cover(self):
        self.set_position(0)
        print(f"Device {self.get_entity_id()} closing")

class FanMixin:
    """风扇能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, '_capabilities'):
            self._capabilities._capabilities["set_speed"] = DeviceCapability(
                "set_speed",
                parameters={"min": 0, "max": 100}
            )
            self._capabilities._capabilities["set_oscillating"] = DeviceCapability("set_oscillating")
        self.attributes.setdefault("speed", 0)
        self.attributes.setdefault("oscillating", False)

    def set_speed(self, speed: int):
        self.attributes["speed"] = speed
        print(f"Device {self.get_entity_id()} speed set to {speed}")

    def set_oscillating(self, oscillating: bool):
        self.attributes["oscillating"] = oscillating
        print(f"Device {self.get_entity_id()} oscillating set to {oscillating}")

class LockMixin:
    """锁具能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, '_capabilities'):
            self._capabilities._capabilities["lock"] = DeviceCapability("lock")
            self._capabilities._capabilities["unlock"] = DeviceCapability("unlock")
        self.attributes.setdefault("lock_state", "locked")

    def lock(self):
        self.attributes["lock_state"] = "locked"
        self._state = "locked"
        print(f"Device {self.get_entity_id()} locked")

    def unlock(self):
        self.attributes["lock_state"] = "unlocked"
        self._state = "unlocked"
        print(f"Device {self.get_entity_id()} unlocked")

class VacuumMixin:
    """吸尘器能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, '_capabilities'):
            self._capabilities._capabilities["start"] = DeviceCapability("start")
            self._capabilities._capabilities["stop"] = DeviceCapability("stop")
            self._capabilities._capabilities["pause"] = DeviceCapability("pause")
            self._capabilities._capabilities["return_to_base"] = DeviceCapability("return_to_base")
        self.attributes.setdefault("status", "docked")
        self.attributes.setdefault("battery_level", 100)

    def start(self):
        self.attributes["status"] = "cleaning"
        self._state = "cleaning"
        print(f"Device {self.get_entity_id()} started cleaning")

    def stop(self):
        self.attributes["status"] = "docked"
        self._state = "docked"
        print(f"Device {self.get_entity_id()} stopped")

    def pause(self):
        self.attributes["status"] = "paused"
        self._state = "paused"
        print(f"Device {self.get_entity_id()} paused")

    def return_to_base(self):
        self.attributes["status"] = "returning"
        self._state = "returning"
        print(f"Device {self.get_entity_id()} returning to base")

class LocationMixin:
    """定位能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attributes.setdefault("latitude", None)
        self.attributes.setdefault("longitude", None)
        self.attributes.setdefault("is_home", False)

    def set_location(self, latitude: float, longitude: float):
        self.attributes["latitude"] = latitude
        self.attributes["longitude"] = longitude
        print(f"Device {self.get_entity_id()} location updated to {latitude}, {longitude}")

class WeatherMixin:
    """天气能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attributes.setdefault("temperature", None)
        self.attributes.setdefault("humidity", None)
        self.attributes.setdefault("condition", None)

    def set_weather(self, temperature: float, humidity: Optional[float] = None, condition: Optional[str] = None):
        if temperature is not None:
            self.attributes["temperature"] = temperature
        if humidity is not None:
            self.attributes["humidity"] = humidity
        if condition:
            self.attributes["condition"] = condition
            self._state = condition
        print(f"Device {self.get_entity_id()} weather updated")

class MediaPlayerMixin:
    """媒体播放能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, '_capabilities'):
            self._capabilities._capabilities["play"] = DeviceCapability("play")
            self._capabilities._capabilities["pause"] = DeviceCapability("pause")
            self._capabilities._capabilities["stop"] = DeviceCapability("stop")
            self._capabilities._capabilities["set_volume"] = DeviceCapability("set_volume")
        self.attributes.setdefault("volume_level", 0.5)
        self.attributes.setdefault("is_muted", False)

    def play(self):
        self._state = "playing"
        print(f"Device {self.get_entity_id()} playing")

    def pause(self):
        self._state = "paused"
        print(f"Device {self.get_entity_id()} paused")

    def stop(self):
        self._state = "idle"
        print(f"Device {self.get_entity_id()} stopped")

class CameraMixin:
    """摄像头能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, '_capabilities'):
            self._capabilities._capabilities["start_recording"] = DeviceCapability("start_recording")
            self._capabilities._capabilities["stop_recording"] = DeviceCapability("stop_recording")
        self.attributes.setdefault("is_recording", False)
        self.attributes.setdefault("motion_detected", False)

    def start_recording(self):
        self.attributes["is_recording"] = True
        print(f"Device {self.get_entity_id()} recording started")

    def stop_recording(self):
        self.attributes["is_recording"] = False
        print(f"Device {self.get_entity_id()} recording stopped")

class AlarmMixin:
    """安防能力特征"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, '_capabilities'):
            self._capabilities._capabilities["arm_away"] = DeviceCapability("arm_away")
            self._capabilities._capabilities["arm_home"] = DeviceCapability("arm_home")
            self._capabilities._capabilities["disarm"] = DeviceCapability("disarm")
        self.attributes.setdefault("alarm_state", "disarmed")

    def arm_away(self):
        self.attributes["alarm_state"] = "armed_away"
        self._state = "armed_away"
        print(f"Device {self.get_entity_id()} armed away")

    def arm_home(self):
        self.attributes["alarm_state"] = "armed_home"
        self._state = "armed_home"
        print(f"Device {self.get_entity_id()} armed home")

    def disarm(self):
        self.attributes["alarm_state"] = "disarmed"
        self._state = "disarmed"
        print(f"Device {self.get_entity_id()} disarmed")
