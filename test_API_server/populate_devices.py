
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
            # 50% chance to exist for some combinations, but ensure main always exists
            if typ != "main" and random.random() < 0.3:
                continue
                
            name = f"{loc}_{typ}"
            friendly_name = f"{loc.replace('_', ' ').title()} {typ.title()}"
            
            save_device("light", name, random.choice(["on", "off"]), {
                "friendly_name": friendly_name,
                "brightness": random.randint(0, 255),
                "color_temp": random.randint(153, 500),
                "rgb_color": [random.randint(0, 255) for _ in range(3)],
                "supported_features": 63
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
            "current_consumption": random.uniform(0, 100) if random.choice([True, False]) else 0
        })

def generate_sensors():
    # Environmental sensors for each room
    rooms = ["living_room", "bedroom_master", "kitchen", "study"]
    
    for room in rooms:
        # Temperature
        save_device("sensor", f"{room}_temperature", f"{random.uniform(18, 28):.1f}", {
            "friendly_name": f"{room.replace('_', ' ').title()} Temperature",
            "unit_of_measurement": "°C",
            "device_class": "temperature"
        })
        # Humidity
        save_device("sensor", f"{room}_humidity", f"{random.randint(30, 70)}", {
            "friendly_name": f"{room.replace('_', ' ').title()} Humidity",
            "unit_of_measurement": "%",
            "device_class": "humidity"
        })
        
    # Other sensors
    save_device("sensor", "power_usage_total", f"{random.uniform(200, 3500):.1f}", {
        "friendly_name": "Total Power Usage",
        "unit_of_measurement": "W",
        "device_class": "power"
    })
    
    save_device("sensor", "outdoor_pm25", f"{random.randint(10, 150)}", {
        "friendly_name": "Outdoor PM2.5",
        "unit_of_measurement": "µg/m³",
        "device_class": "pm25"
    })

def generate_binary_sensors():
    rooms = ["front_door", "back_door", "kitchen_window", "bedroom_window", "garage_door"]
    
    for item in rooms:
        # Open/Close
        save_device("binary_sensor", f"{item}_contact", random.choice(["on", "off"]), {
            "friendly_name": f"{item.replace('_', ' ').title()} Contact",
            "device_class": "door" if "door" in item else "window"
        })
    
    # Motion sensors
    motion_rooms = ["hallway", "living_room", "kitchen", "driveway"]
    for room in motion_rooms:
        save_device("binary_sensor", f"{room}_motion", random.choice(["on", "off"]), {
            "friendly_name": f"{room.replace('_', ' ').title()} Motion",
            "device_class": "motion"
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
            "device_class": device_class
        })

def generate_climate():
    acs = ["living_room", "bedroom_master", "study"]
    
    for room in acs:
        save_device("climate", f"{room}_ac", random.choice(["cool", "off", "heat"]), {
            "friendly_name": f"{room.replace('_', ' ').title()} AC",
            "temperature": 24,
            "current_temperature": random.uniform(22, 26),
            "hvac_modes": ["off", "cool", "heat", "fan_only"],
            "fan_mode": "auto"
        })

def generate_vacuum():
    save_device("vacuum", "roborock_s7", random.choice(["docked", "cleaning", "paused"]), {
        "friendly_name": "Roborock S7",
        "battery_level": random.randint(0, 100),
        "fan_speed": "standard"
    })

def generate_media():
    save_device("media_player", "living_room_tv", random.choice(["on", "off", "playing", "paused"]), {
        "friendly_name": "Living Room TV",
        "volume_level": 0.3,
        "source": "Netflix",
        "device_class": "tv"
    })
    
    save_device("media_player", "kitchen_speaker", "idle", {
        "friendly_name": "Kitchen Speaker",
        "volume_level": 0.5,
        "device_class": "speaker"
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
    logger.info("Done! Devices generated in ./devices/")

if __name__ == "__main__":
    main()
