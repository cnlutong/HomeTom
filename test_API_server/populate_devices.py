
import json
import logging
from datetime import datetime, timezone
import random
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("populate_devices")

DEVICES_DIR = Path(__file__).parent / "devices"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def save_device(domain, name, state, attributes=None):
    if attributes is None:
        attributes = {}
    
    entity_id = f"{domain}.{name}"
    
    # Ensure domain directory exists
    domain_dir = DEVICES_DIR / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    
    data = {
        "entity_id": entity_id,
        "state": state,
        "attributes": attributes,
        "last_changed": now_iso(),
        "last_updated": now_iso(),
    }
    
    file_path = domain_dir / f"{name}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.debug(f"Created {entity_id}")



def generate_lights():
    locations = ["living_room", "kitchen", "bedroom_master", "bedroom_guest", "hallway", "dining_room", "bathroom", "balcony", "study", "garage"]
    types = ["main", "strip", "spot", "lamp"]
    
    for loc in locations:
        for typ in types:
            if typ != "main" and random.random() < 0.3:
                continue
                
            name = f"{loc}_{typ}"
            friendly_name = f"{loc.replace('_', ' ').title()} {typ.title()}"
            
            save_device("light", name, random.choice(["on", "off"]), {
                "friendly_name": friendly_name,
                "brightness": random.randint(0, 255),
                "color_temp": random.randint(153, 500),
                "rgb_color": [random.randint(0, 255) for _ in range(3)],
                "supported_features": 63,
                "capabilities": [
                    {"name": "turn_on", "value_type": "void"},
                    {"name": "turn_off", "value_type": "void"},
                    {"name": "toggle", "value_type": "void"},
                    {"name": "set_brightness", "value_type": "int", "constraints": {"min": 0, "max": 255}},
                    {"name": "set_color_temp", "value_type": "int", "constraints": {"min": 153, "max": 500}},
                    {"name": "set_rgb_color", "value_type": "int_array", "constraints": {"length": 3, "min_val": 0, "max_val": 255}}
                ]
            })

def generate_switches():
    devices = [
        ("coffee_maker", "Coffee Maker"),
        ("dehumidifier", "Dehumidifier"),
        ("air_purifier_switch", "Air Purifier Power"),
        ("projector_power", "Projector"),
        ("garden_fountain", "Garden Fountain"),
        ("router_restart", "Router Restart"),
        ("water_heater", "Water Heater"),
        ("bed_warmer", "Bed Warmer"),
    ]
    
    # Add some generic plugs
    for i in range(1, 6):
        devices.append((f"smart_plug_{i}", f"Smart Plug {i}"))
        
    for name, friendly in devices:
        save_device("switch", name, random.choice(["on", "off"]), {
            "friendly_name": friendly,
            "device_class": "outlet",
            "current_consumption": random.uniform(0, 100) if random.choice([True, False]) else 0,
            "capabilities": [
                {"name": "turn_on", "value_type": "void"},
                {"name": "turn_off", "value_type": "void"},
                {"name": "toggle", "value_type": "void"}
            ]
        })

def generate_sensors():
    # Environmental sensors for each room
    rooms = ["living_room", "bedroom_master", "kitchen", "study"]
    
    for room in rooms:
        # Temperature
        save_device("sensor", f"{room}_temperature", f"{random.uniform(18, 28):.1f}", {
            "friendly_name": f"{room.replace('_', ' ').title()} Temperature",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "capabilities": [
                {"name": "value", "value_type": "float", "constraints": {"min": -20.0, "max": 50.0, "step": 0.1}}
            ]
        })
        # Humidity
        save_device("sensor", f"{room}_humidity", f"{random.randint(30, 70)}", {
            "friendly_name": f"{room.replace('_', ' ').title()} Humidity",
            "unit_of_measurement": "%",
            "device_class": "humidity",
            "capabilities": [
                {"name": "value", "value_type": "int", "constraints": {"min": 0, "max": 100}}
            ]
        })
        
    # Other sensors
    save_device("sensor", "power_usage_total", f"{random.uniform(200, 3500):.1f}", {
        "friendly_name": "Total Power Usage",
        "unit_of_measurement": "W",
        "device_class": "power",
        "capabilities": [
            {"name": "value", "value_type": "float", "constraints": {"min": 0.0}}
        ]
    })
    
    save_device("sensor", "outdoor_pm25", f"{random.randint(10, 150)}", {
        "friendly_name": "Outdoor PM2.5",
        "unit_of_measurement": "µg/m³",
        "device_class": "pm25",
        "capabilities": [
            {"name": "value", "value_type": "int", "constraints": {"min": 0}}
        ]
    })

def generate_binary_sensors():
    rooms = ["front_door", "back_door", "kitchen_window", "bedroom_window", "garage_door"]
    
    for item in rooms:
        # Open/Close
        save_device("binary_sensor", f"{item}_contact", random.choice(["on", "off"]), {
            "friendly_name": f"{item.replace('_', ' ').title()} Contact",
            "device_class": "door" if "door" in item else "window",
            "capabilities": [
                {"name": "value", "value_type": "boolean"}
            ]
        })
    
    # Motion sensors
    motion_rooms = ["hallway", "living_room", "kitchen", "driveway"]
    for room in motion_rooms:
        save_device("binary_sensor", f"{room}_motion", random.choice(["on", "off"]), {
            "friendly_name": f"{room.replace('_', ' ').title()} Motion",
            "device_class": "motion",
            "capabilities": [
                {"name": "value", "value_type": "boolean"}
            ]
        })

def generate_covers():
    covers = [
        ("living_room_curtain_main", "Living Room Curtain Main"),
        ("living_room_curtain_sheer", "Living Room Curtain Sheer"),
        ("bedroom_master_blinds", "Master Bedroom Blinds"),
        ("garage_gate", "Garage Gate"),
    ]
    
    for name, friendly in covers:
        pos = random.randint(0, 100)
        state = "open" if pos > 0 else "closed"
        device_class = "garage" if "garage" in name else "curtain"
        if "blinds" in name: device_class = "blind"
        
        save_device("cover", name, state, {
            "friendly_name": friendly,
            "current_position": pos,
            "device_class": device_class,
            "capabilities": [
                {"name": "open_cover", "value_type": "void"},
                {"name": "close_cover", "value_type": "void"},
                {"name": "stop_cover", "value_type": "void"},
                {"name": "set_cover_position", "value_type": "int", "constraints": {"min": 0, "max": 100}}
            ]
        })

def generate_climate():
    acs = ["living_room", "bedroom_master", "study"]
    
    for room in acs:
        save_device("climate", f"{room}_ac", random.choice(["cool", "off", "heat"]), {
            "friendly_name": f"{room.replace('_', ' ').title()} AC",
            "temperature": 24,
            "current_temperature": random.uniform(22, 26),
            "hvac_modes": ["off", "cool", "heat", "fan_only"],
            "fan_mode": "auto",
            "capabilities": [
                {"name": "turn_on", "value_type": "void"},
                {"name": "turn_off", "value_type": "void"},
                {"name": "set_temperature", "value_type": "float", "constraints": {"min": 16.0, "max": 30.0, "step": 0.5}},
                {"name": "set_hvac_mode", "value_type": "enum", "constraints": {"options": ["off", "cool", "heat", "fan_only"]}},
                {"name": "set_fan_mode", "value_type": "enum", "constraints": {"options": ["auto", "low", "medium", "high"]}}
            ]
        })

def generate_vacuum():
    save_device("vacuum", "roborock_s7", random.choice(["docked", "cleaning", "paused"]), {
        "friendly_name": "Roborock S7",
        "battery_level": random.randint(0, 100),
        "fan_speed": "standard",
        "capabilities": [
            {"name": "start", "value_type": "void"},
            {"name": "stop", "value_type": "void"},
            {"name": "pause", "value_type": "void"},
            {"name": "return_to_base", "value_type": "void"},
            {"name": "set_fan_speed", "value_type": "enum", "constraints": {"options": ["silent", "standard", "medium", "turbo"]}}
        ]
    })

def generate_media():
    save_device("media_player", "living_room_tv", random.choice(["on", "off", "playing", "paused"]), {
        "friendly_name": "Living Room TV",
        "volume_level": 0.3,
        "source": "Netflix",
        "device_class": "tv",
        "capabilities": [
            {"name": "turn_on", "value_type": "void"},
            {"name": "turn_off", "value_type": "void"},
            {"name": "play_media", "value_type": "string"},
            {"name": "media_play", "value_type": "void"},
            {"name": "media_pause", "value_type": "void"},
            {"name": "media_stop", "value_type": "void"},
            {"name": "volume_set", "value_type": "float", "constraints": {"min": 0.0, "max": 1.0}},
            {"name": "volume_mute", "value_type": "boolean"}
        ]
    })
    
    save_device("media_player", "kitchen_speaker", "idle", {
        "friendly_name": "Kitchen Speaker",
        "volume_level": 0.5,
        "device_class": "speaker",
        "capabilities": [
            {"name": "turn_on", "value_type": "void"},
            {"name": "turn_off", "value_type": "void"},
            {"name": "play_media", "value_type": "string"},
            {"name": "media_play", "value_type": "void"},
            {"name": "media_pause", "value_type": "void"},
            {"name": "media_stop", "value_type": "void"},
            {"name": "volume_set", "value_type": "float", "constraints": {"min": 0.0, "max": 1.0}},
            {"name": "volume_mute", "value_type": "boolean"}
        ]
    })

def generate_locks():
    locks = ["front_door", "back_door", "garage_side_door"]
    for lock in locks:
        save_device("lock", lock, random.choice(["locked", "unlocked"]), {
            "friendly_name": f"{lock.replace('_', ' ').title()}",
            "capabilities": [
                {"name": "lock", "value_type": "void"},
                {"name": "unlock", "value_type": "void"}
            ]
        })

def generate_fans():
    fans = ["living_room_fan", "bedroom_fan"]
    for fan in fans:
        save_device("fan", fan, random.choice(["on", "off"]), {
            "friendly_name": f"{fan.replace('_', ' ').title()}",
            "speed": "low",
            "oscillating": False,
            "capabilities": [
                {"name": "turn_on", "value_type": "void"},
                {"name": "turn_off", "value_type": "void"},
                {"name": "set_speed", "value_type": "enum", "constraints": {"options": ["low", "medium", "high"]}},
                {"name": "set_oscillating", "value_type": "boolean"}
            ]
        })

def generate_cameras():
    cams = ["front_porch", "backyard", "garage_interior"]
    for cam in cams:
        save_device("camera", cam, "idle", {
            "friendly_name": f"{cam.replace('_', ' ').title()} Camera",
            "access_token": "mock_token",
            "capabilities": [
                {"name": "turn_on", "value_type": "void"},
                {"name": "turn_off", "value_type": "void"},
                {"name": "start_recording", "value_type": "void"},
                {"name": "stop_recording", "value_type": "void"}
            ]
        })

def generate_alarms():
    save_device("alarm_control_panel", "home_alarm", "disarmed", {
        "friendly_name": "Home Alarm",
        "code_format": "number",
        "capabilities": [
            {"name": "alarm_arm_away", "value_type": "string", "constraints": {"regex": "^\\d{4}$"}},
            {"name": "alarm_arm_home", "value_type": "string", "constraints": {"regex": "^\\d{4}$"}},
            {"name": "alarm_disarm", "value_type": "string", "constraints": {"regex": "^\\d{4}$"}},
            {"name": "alarm_trigger", "value_type": "void"}
        ]
    })

def generate_misc():
    # Weather
    save_device("weather", "home", "sunny", {
        "friendly_name": "Home Weather",
        "temperature": 25,
        "humidity": 60,
        "pressure": 1013,
        "wind_speed": 10,
        "capabilities": []
    })
    
    # Device Tracker
    save_device("device_tracker", "users_phone", "home", {
        "friendly_name": "User's Phone",
        "source_type": "router",
        "ip": "192.168.1.100",
        "capabilities": []
    })

def main():
    logger.info("Cleaning old devices...")
    if DEVICES_DIR.exists():
        import shutil
        shutil.rmtree(DEVICES_DIR)
    DEVICES_DIR.mkdir(parents=True, exist_ok=True)
    
    logger.info("Generating smart home devices...")
    generate_lights()
    generate_switches()
    generate_sensors()
    generate_binary_sensors()
    generate_covers()
    generate_climate()
    generate_vacuum()
    generate_media()
    generate_locks()
    generate_fans()
    generate_cameras()
    generate_alarms()
    generate_misc()
    logger.info("Done! Devices generated in ./devices/")

if __name__ == "__main__":
    main()
