"""设备数据导出工具

将当前硬编码的设备数据导出为 JSON 文件。
运行后可删除此脚本。

用法：
    python3 -m test_API_server.export_devices
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

# 设备目录
DEVICES_DIR = Path(__file__).parent / "devices"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def export_device(entity_id: str, state: str, attributes: dict):
    """导出单个设备到 JSON 文件"""
    domain = entity_id.split(".")[0]
    device_name = entity_id.split(".")[1]
    
    device_data = {
        "entity_id": entity_id,
        "state": state,
        "attributes": attributes,
        "last_changed": now(),
        "last_updated": now(),
    }
    
    # 确保目录存在
    domain_dir = DEVICES_DIR / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    
    # 写入 JSON 文件
    file_path = domain_dir / f"{device_name}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(device_data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ {entity_id} -> {file_path.relative_to(DEVICES_DIR.parent)}")


def main():
    print("=" * 60)
    print("📦 导出设备数据到 JSON 文件")
    print("=" * 60)
    print()
    
    # ==================== 灯光设备 (Light) ====================
    print("💡 Light (8个)")
    export_device("light.living_room", "on", {
        "friendly_name": "客厅主灯",
        "brightness": 200,
        "color_temp": 300,
        "rgb_color": [255, 255, 255],
        "supported_features": 63,
    })
    export_device("light.bedroom", "off", {
        "friendly_name": "卧室主灯",
        "brightness": 0,
        "color_temp": 350,
        "supported_features": 63,
    })
    export_device("light.kitchen", "on", {
        "friendly_name": "厨房灯",
        "brightness": 255,
        "color_temp": 250,
    })
    export_device("light.bathroom", "off", {
        "friendly_name": "浴室灯",
        "brightness": 0,
    })
    export_device("light.study", "on", {
        "friendly_name": "书房台灯",
        "brightness": 180,
        "color_temp": 400,
    })
    export_device("light.balcony", "off", {
        "friendly_name": "阳台灯",
        "brightness": 0,
    })
    export_device("light.hallway", "on", {
        "friendly_name": "走廊灯",
        "brightness": 100,
    })
    export_device("light.dining_room", "on", {
        "friendly_name": "餐厅吊灯",
        "brightness": 220,
        "color_temp": 320,
        "rgb_color": [255, 240, 220],
    })
    
    # ==================== 开关设备 (Switch) ====================
    print("\n🔌 Switch (6个)")
    export_device("switch.bedroom_fan", "off", {
        "friendly_name": "卧室风扇开关",
        "device_class": "switch",
    })
    export_device("switch.water_heater", "on", {
        "friendly_name": "热水器",
        "device_class": "switch",
        "power_consumption": 2000,
    })
    export_device("switch.air_purifier", "on", {
        "friendly_name": "空气净化器",
        "device_class": "switch",
    })
    export_device("switch.humidifier", "off", {
        "friendly_name": "加湿器",
        "device_class": "switch",
    })
    export_device("switch.floor_heating", "on", {
        "friendly_name": "地暖开关",
        "device_class": "switch",
        "power_consumption": 1500,
    })
    export_device("switch.mosquito_killer", "off", {
        "friendly_name": "灭蚊器",
        "device_class": "switch",
    })
    
    # ==================== 窗帘/覆盖设备 (Cover) ====================
    print("\n🪟 Cover (6个)")
    export_device("cover.living_room_curtain", "open", {
        "friendly_name": "客厅窗帘",
        "position": 100,
        "cover_type": "curtain",
        "supported_features": 15,
    })
    export_device("cover.garage_door", "closed", {
        "friendly_name": "车库门",
        "position": 0,
        "cover_type": "garage_door",
    })
    export_device("cover.bedroom_blind", "open", {
        "friendly_name": "卧室百叶窗",
        "position": 80,
        "cover_type": "blind",
        "tilt_position": 45,
    })
    export_device("cover.kitchen_curtain", "closed", {
        "friendly_name": "厨房窗帘",
        "position": 0,
        "cover_type": "curtain",
    })
    export_device("cover.study_blind", "open", {
        "friendly_name": "书房百叶窗",
        "position": 50,
        "cover_type": "blind",
        "tilt_position": 30,
    })
    export_device("cover.balcony_awning", "closed", {
        "friendly_name": "阳台遮阳棚",
        "position": 0,
        "cover_type": "awning",
    })
    
    # ==================== 空调/温控设备 (Climate) ====================
    print("\n❄️ Climate (5个)")
    export_device("climate.living_room_ac", "heat", {
        "friendly_name": "客厅空调",
        "temperature": 24,
        "current_temperature": 22.5,
        "hvac_modes": ["off", "heat", "cool", "auto", "dry", "fan_only"],
        "fan_mode": "auto",
        "fan_modes": ["auto", "low", "medium", "high"],
        "swing_mode": "off",
        "swing_modes": ["off", "vertical", "horizontal", "both"],
        "min_temp": 16,
        "max_temp": 30,
    })
    export_device("climate.bedroom_ac", "cool", {
        "friendly_name": "卧室空调",
        "temperature": 26,
        "current_temperature": 28,
        "hvac_modes": ["off", "heat", "cool", "auto"],
        "fan_mode": "high",
    })
    export_device("climate.study_ac", "off", {
        "friendly_name": "书房空调",
        "temperature": 25,
        "current_temperature": 24,
        "hvac_modes": ["off", "heat", "cool", "auto"],
        "fan_mode": "auto",
    })
    export_device("climate.floor_heating", "heat", {
        "friendly_name": "地暖温控器",
        "temperature": 22,
        "current_temperature": 20,
        "hvac_modes": ["off", "heat"],
        "min_temp": 16,
        "max_temp": 28,
    })
    export_device("climate.water_heater", "heat", {
        "friendly_name": "热水器温控",
        "temperature": 45,
        "current_temperature": 42,
        "hvac_modes": ["off", "heat"],
        "min_temp": 35,
        "max_temp": 65,
    })
    
    # ==================== 风扇设备 (Fan) ====================
    print("\n🌀 Fan (4个)")
    export_device("fan.living_room_fan", "on", {
        "friendly_name": "客厅吊扇",
        "percentage": 50,
        "speed_count": 3,
        "oscillating": True,
        "direction": "forward",
    })
    export_device("fan.bedroom_fan", "off", {
        "friendly_name": "卧室落地扇",
        "percentage": 0,
        "speed_count": 5,
        "oscillating": False,
    })
    export_device("fan.desk_fan", "on", {
        "friendly_name": "书房USB小风扇",
        "percentage": 30,
        "speed_count": 3,
    })
    export_device("fan.exhaust_fan", "off", {
        "friendly_name": "浴室排气扇",
        "percentage": 0,
        "speed_count": 2,
    })
    
    # ==================== 门锁设备 (Lock) ====================
    print("\n🔒 Lock (4个)")
    export_device("lock.front_door", "locked", {
        "friendly_name": "前门智能锁",
        "is_locked": True,
        "device_class": "lock",
    })
    export_device("lock.back_door", "unlocked", {
        "friendly_name": "后门智能锁",
        "is_locked": False,
    })
    export_device("lock.garage_door", "locked", {
        "friendly_name": "车库门锁",
        "is_locked": True,
    })
    export_device("lock.safe_box", "locked", {
        "friendly_name": "保险箱",
        "is_locked": True,
    })
    
    # ==================== 扫地机器人 (Vacuum) ====================
    print("\n🤖 Vacuum (3个)")
    export_device("vacuum.robot_vacuum", "docked", {
        "friendly_name": "扫地机器人",
        "battery_level": 100,
        "fan_speed": "standard",
        "fan_speed_list": ["quiet", "standard", "turbo", "max"],
        "status": "充电中",
    })
    export_device("vacuum.mop_robot", "cleaning", {
        "friendly_name": "拖地机器人",
        "battery_level": 75,
        "fan_speed": "standard",
        "status": "清扫中",
    })
    export_device("vacuum.window_cleaner", "docked", {
        "friendly_name": "擦窗机器人",
        "battery_level": 100,
        "status": "待机",
    })
    
    # ==================== 传感器 (Sensor) ====================
    print("\n🌡️ Sensor (4个)")
    export_device("sensor.temperature", "23.5", {
        "friendly_name": "室内温度",
        "unit_of_measurement": "°C",
        "device_class": "temperature",
    })
    export_device("sensor.humidity", "65", {
        "friendly_name": "室内湿度",
        "unit_of_measurement": "%",
        "device_class": "humidity",
    })
    export_device("sensor.power_consumption", "1250", {
        "friendly_name": "当前功耗",
        "unit_of_measurement": "W",
        "device_class": "power",
    })
    export_device("sensor.illuminance", "350", {
        "friendly_name": "光照强度",
        "unit_of_measurement": "lx",
        "device_class": "illuminance",
    })
    
    # ==================== 二元传感器 (Binary Sensor) ====================
    print("\n🚪 Binary Sensor (6个)")
    export_device("binary_sensor.motion_living_room", "off", {
        "friendly_name": "客厅人体传感器",
        "device_class": "motion",
        "is_on": False,
    })
    export_device("binary_sensor.motion_bedroom", "on", {
        "friendly_name": "卧室人体传感器",
        "device_class": "motion",
        "is_on": True,
    })
    export_device("binary_sensor.door_front", "off", {
        "friendly_name": "前门传感器",
        "device_class": "door",
        "is_on": False,
    })
    export_device("binary_sensor.window_living_room", "on", {
        "friendly_name": "客厅窗户传感器",
        "device_class": "window",
        "is_on": True,
    })
    export_device("binary_sensor.water_leak", "off", {
        "friendly_name": "漏水传感器",
        "device_class": "moisture",
        "is_on": False,
    })
    export_device("binary_sensor.smoke", "off", {
        "friendly_name": "烟雾报警器",
        "device_class": "smoke",
        "is_on": False,
    })
    
    # ==================== 设备追踪器 (Device Tracker) ====================
    print("\n📍 Device Tracker (2个)")
    export_device("device_tracker.phone_dad", "home", {
        "friendly_name": "爸爸的手机",
        "source_type": "gps",
        "latitude": 31.2304,
        "longitude": 121.4737,
        "gps_accuracy": 10,
        "battery_level": 85,
    })
    export_device("device_tracker.phone_mom", "not_home", {
        "friendly_name": "妈妈的手机",
        "source_type": "gps",
        "latitude": 31.2200,
        "longitude": 121.4600,
    })
    
    # ==================== 天气 (Weather) ====================
    print("\n☀️ Weather (1个)")
    export_device("weather.home", "sunny", {
        "friendly_name": "本地天气",
        "temperature": 25,
        "humidity": 60,
        "pressure": 1013,
        "wind_speed": 5.5,
        "wind_bearing": 180,
        "condition": "sunny",
        "forecast": [
            {"condition": "sunny", "temperature": 26, "templow": 18, "datetime": "2024-01-02"},
            {"condition": "cloudy", "temperature": 24, "templow": 17, "datetime": "2024-01-03"},
            {"condition": "rainy", "temperature": 20, "templow": 15, "datetime": "2024-01-04"},
        ],
    })
    
    # ==================== 媒体播放器 (Media Player) ====================
    print("\n📺 Media Player (2个)")
    export_device("media_player.living_room_tv", "playing", {
        "friendly_name": "客厅电视",
        "volume_level": 0.5,
        "is_volume_muted": False,
        "media_content_type": "video",
        "media_title": "新闻联播",
        "source": "HDMI1",
        "source_list": ["HDMI1", "HDMI2", "TV", "Netflix", "YouTube"],
        "supported_features": 152463,
    })
    export_device("media_player.bedroom_speaker", "idle", {
        "friendly_name": "卧室音箱",
        "volume_level": 0.3,
        "is_volume_muted": False,
        "media_content_type": "music",
    })
    
    # ==================== 摄像头 (Camera) ====================
    print("\n📷 Camera (2个)")
    export_device("camera.front_door", "idle", {
        "friendly_name": "前门摄像头",
        "is_streaming": False,
        "is_recording": True,
        "motion_detection": True,
        "brand": "Hikvision",
        "model": "DS-2CD2143G0-I",
    })
    export_device("camera.backyard", "recording", {
        "friendly_name": "后院摄像头",
        "is_streaming": False,
        "is_recording": True,
        "motion_detection": True,
    })
    
    # ==================== 安防面板 (Alarm Control Panel) ====================
    print("\n🚨 Alarm Control Panel (1个)")
    export_device("alarm_control_panel.home", "disarmed", {
        "friendly_name": "家庭安防系统",
        "code_arm_required": True,
        "code_format": "number",
        "supported_features": 31,
    })
    
    print()
    print("=" * 60)
    print(f"✅ 导出完成！设备文件保存在: {DEVICES_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
