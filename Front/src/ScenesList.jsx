import React, { useState, useEffect } from "react";

// home1 scene data
const getHome1Scene = () => {
  const home1Data = {
    automationId: "auto_home1",
    name: "home1",
    description: "Automation with 2 trigger(s), 2 condition(s), and 1 action(s)",
    isEnabled: true,
    triggers: [
      {
        type: "deviceState",
        deviceId: "sensor_temp_01",
        capability: "temp",
        state: "detected"
      },
      {
        type: "deviceState",
        deviceId: "sensor_motion_01",
        capability: "motion",
        state: "detected"
      }
    ],
    conditions: [
      {
        type: "time",
        time: "17:00"
      },
      {
        type: "deviceState",
        deviceId: "sensor_temp_01",
        capability: "temperature",
        state: ">= 30"
      }
    ],
    actions: [
      {
        type: "deviceCommand",
        deviceId: "device_lamp_01",
        capability: "onOff",
        value: true
      }
    ]
  };

  return {
    id: home1Data.automationId,
    name: "Welcome Home",
    description: "Automation with 2 trigger(s), 2 condition(s), and 1 action(s)",
    icon: "🏠",
    isEnabled: true,
    triggerCount: home1Data.triggers.length,
    conditionCount: home1Data.conditions.length,
    actionCount: home1Data.actions.length,
    nodeCount: 3,
    activeCount: 1,
    createdAt: new Date().toISOString(),
    automationData: home1Data,
  };
};

// Helper function to translate Chinese scene names to English
const translateSceneName = (name) => {
  const translations = {
    "回家模式": "Welcome Home",
    "观影模式": "Movie Night",
    "睡眠模式": "Sleep Mode",
    "早晨模式": "Morning Routine",
    "晚上模式": "Evening Relax",
  };
  
  // Check if name contains Chinese characters
  if (/[\u4e00-\u9fa5]/.test(name)) {
    // Try to find exact match
    if (translations[name]) {
      return translations[name];
    }
    // Try to extract Chinese part and translate
    const chineseMatch = name.match(/[\u4e00-\u9fa5]+/);
    if (chineseMatch && translations[chineseMatch[0]]) {
      return translations[chineseMatch[0]];
    }
    // If name has English in parentheses, use that
    const englishMatch = name.match(/\(([^)]+)\)/);
    if (englishMatch) {
      return englishMatch[1];
    }
  }
  return name;
};

// Load scene data from localStorage
const loadScenesFromStorage = () => {
  try {
    const saved = localStorage.getItem("smart-home-scenes");
    if (saved) {
      const scenes = JSON.parse(saved);
      // Update scene names to English if they contain Chinese
      const updatedScenes = scenes.map(scene => ({
        ...scene,
        name: translateSceneName(scene.name)
      }));
      
      // Save updated scenes back to localStorage
      if (scenes.some((scene, idx) => scene.name !== updatedScenes[idx].name)) {
        localStorage.setItem("smart-home-scenes", JSON.stringify(updatedScenes));
      }
      
      const hasHome1 = updatedScenes.some(scene => scene.id === "auto_home1");
      if (!hasHome1) {
        return [getHome1Scene(), ...updatedScenes];
      }
      return updatedScenes;
    }
  } catch (error) {
    console.error("Failed to load scenes from localStorage:", error);
  }
  return [
    getHome1Scene(),
    {
      id: "scene_002",
      name: "Movie Night",
      description: "Dim lights and close curtains",
      icon: "🎬",
      isEnabled: true,
      triggerCount: 1,
      conditionCount: 1,
      actionCount: 2,
      nodeCount: 2,
      activeCount: 2,
      createdAt: "2024-01-01T18:00:00Z",
    },
  ];
};

const saveScenesToStorage = (scenes) => {
  try {
    localStorage.setItem("smart-home-scenes", JSON.stringify(scenes));
  } catch (error) {
    console.error("Failed to save scenes to localStorage:", error);
  }
};

// API function to fetch device status
const fetchDeviceStatus = async () => {
  try {
    // TODO: Replace with actual API endpoint
    // const response = await fetch('/api/devices/status', {
    //   headers: {
    //     'Authorization': `Bearer ${token}`,
    //     'Content-Type': 'application/json'
    //   }
    // });
    // const result = await response.json();
    // return result.data;
    
    // Mock data for now - replace with actual API call
    return {
      devices: [
        {
          id: "sensor_temp_01",
          type: "sensor",
          capability: "temperature",
          currentState: { temperature: 24.2 }
        },
        {
          id: "sensor_humidity_01",
          type: "sensor",
          capability: "humidity",
          currentState: { humidity: 48 }
        }
      ]
    };
  } catch (error) {
    console.error("Failed to fetch device status:", error);
    return { devices: [] };
  }
};

// Get user's current location
const getCurrentLocation = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocation is not supported by your browser"));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        });
      },
      (error) => {
        reject(error);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  });
};

// Get location name from coordinates (reverse geocoding)
const getLocationName = async (latitude, longitude) => {
  try {
    // Using OpenStreetMap Nominatim API (free, no key required)
    // Add accept-language parameter to get English names
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10&addressdetails=1&accept-language=en`,
      {
        headers: {
          'User-Agent': 'SmartHomeDemo/1.0',
          'Accept-Language': 'en'
        }
      }
    );
    
    if (!response.ok) {
      throw new Error(`Geocoding API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Extract location name in English
    if (data.address) {
      // Try to get city, town, or village name
      // Format: City, State/Country
      const city = data.address.city || data.address.town || data.address.village || data.address.municipality;
      const state = data.address.state || data.address.region;
      const country = data.address.country;
      
      let locationName = '';
      if (city) {
        locationName = city;
        if (state && state !== city) {
          locationName += `, ${state}`;
        } else if (country) {
          locationName += `, ${country}`;
        }
      } else if (state) {
        locationName = state;
        if (country) {
          locationName += `, ${country}`;
        }
      } else if (country) {
        locationName = country;
      } else {
        locationName = `${latitude.toFixed(2)}, ${longitude.toFixed(2)}`;
      }
      
      return locationName;
    }
    
    return `${latitude.toFixed(2)}, ${longitude.toFixed(2)}`;
  } catch (error) {
    console.error("Failed to get location name:", error);
    return "Unknown Location";
  }
};

// API function to fetch weather data from OpenWeatherMap
const fetchWeatherData = async () => {
  try {
    // Get user's location
    const location = await getCurrentLocation();
    
    // Get location name
    const locationName = await getLocationName(location.latitude, location.longitude);
    
    // OpenWeatherMap API (free tier)
    // Note: You need to get a free API key from https://openweathermap.org/api
    // For demo purposes, we'll use a public API that doesn't require a key
    // If you have an API key, replace the URL below
    
    // Option 1: Using OpenWeatherMap (requires API key)
    // const API_KEY = 'YOUR_API_KEY_HERE'; // Replace with your OpenWeatherMap API key
    // const response = await fetch(
    //   `https://api.openweathermap.org/data/2.5/weather?lat=${location.latitude}&lon=${location.longitude}&appid=${API_KEY}&units=metric`
    // );
    
    // Option 2: Using a free public API (no key required)
    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${location.latitude}&longitude=${location.longitude}&current=temperature_2m,relative_humidity_2m,weather_code&timezone=auto`
    );
    
    if (!response.ok) {
      throw new Error(`Weather API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Parse Open-Meteo API response
    if (data.current) {
      const weatherCode = data.current.weather_code;
      const weatherConditions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
      };
      
      return {
        temperature: Math.round(data.current.temperature_2m),
        condition: weatherConditions[weatherCode] || "Unknown",
        humidity: Math.round(data.current.relative_humidity_2m),
        location: locationName
      };
    }
    
    // Fallback for OpenWeatherMap format (if using that API)
    // return {
    //   temperature: Math.round(data.main.temp),
    //   condition: data.weather[0].main,
    //   humidity: data.main.humidity,
    //   location: locationName
    // };
    
    throw new Error("Unexpected API response format");
  } catch (error) {
    console.error("Failed to fetch weather data:", error);
    // Return default values if API fails
    return {
      temperature: 24,
      condition: "Partly Cloudy",
      humidity: 48,
      location: "Unknown Location"
    };
  }
};

function ScenesList({ onSelectScene, onCreateNew }) {
  const [scenes, setScenes] = useState([]);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [environmentData, setEnvironmentData] = useState({
    averageTemp: 24.2,
    humidity: 48,
    weatherTemp: 26,
    weatherCondition: "Partly Cloudy",
    location: "Loading..."
  });
  const [activeDevices, setActiveDevices] = useState({ active: 3, total: 5 });

  useEffect(() => {
    const loadedScenes = loadScenesFromStorage();
    setScenes(loadedScenes);
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch device status and weather data
  useEffect(() => {
    const loadData = async () => {
      const [deviceStatus, weatherData] = await Promise.all([
        fetchDeviceStatus(),
        fetchWeatherData()
      ]);

      // Use weather API data for temperature and humidity
      // These represent the current weather conditions in the user's location
      const avgTemp = weatherData.temperature || 24.2;
      const humidity = weatherData.humidity || 48;

      // Calculate active devices from scenes
      const active = scenes.reduce((sum, scene) => sum + (scene.activeCount || 0), 0);

      setEnvironmentData({
        averageTemp: avgTemp.toFixed(1),
        humidity: humidity,
        weatherTemp: weatherData.temperature,
        weatherCondition: weatherData.condition,
        location: weatherData.location || "Unknown Location"
      });

      setActiveDevices({
        active: active,
        total: 5
      });
    };

    loadData();
    // Refresh data every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [scenes]);

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  const serverTime = new Date(currentTime.getTime() - 3600000); // 1 hour behind

  const totalScenes = scenes.length;

  const handleToggleEnabled = (sceneId) => {
    setScenes((prev) => {
      const updated = prev.map((scene) =>
        scene.id === sceneId ? { ...scene, isEnabled: !scene.isEnabled } : scene
      );
      saveScenesToStorage(updated);
      return updated;
    });
  };

  const handleDeleteScene = (sceneId) => {
    if (window.confirm("Are you sure you want to delete this scene?")) {
      setScenes((prev) => {
        const updated = prev.filter((scene) => scene.id !== sceneId);
        saveScenesToStorage(updated);
        return updated;
      });
    }
  };

  const getNodeIcons = (scene) => {
    const icons = [];
    if (scene.triggerCount > 0) icons.push("▶️");
    if (scene.actionCount > 0) {
      // Add equipment icons based on action count
      for (let i = 0; i < Math.min(scene.actionCount, 3); i++) {
        icons.push("💡");
      }
      if (scene.actionCount > 3) {
        icons.push(`+${scene.actionCount - 3}`);
      }
    }
    return icons;
  };

  // Separate scenes into active and disabled
  const activeScenes = scenes.filter(scene => scene.isEnabled);
  const disabledScenes = scenes.filter(scene => !scene.isEnabled);

  return (
    <div className="scenes-dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <div className="logo">
            <div className="logo-icon">☰</div>
            <span className="logo-text">SceneMaster</span>
          </div>
        </div>
        <div className="header-right">
          <div className="status-item">
            <span className="status-icon">🕐</span>
            <span className="status-label">LOCAL</span>
            <span className="status-value">{formatTime(currentTime)}</span>
          </div>
          <div className="status-item">
            <span className="status-icon">🖥️</span>
            <span className="status-label">SERVER</span>
            <span className="status-value">{formatTime(serverTime)}</span>
          </div>
          <div className="status-item">
            <span className="status-icon">📍</span>
            <span className="status-label">LOCATION</span>
            <span className="status-value">{environmentData.location}</span>
          </div>
        </div>
      </header>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <div className="summary-card-icon">📋</div>
          <div className="summary-card-content">
            <div className="summary-card-title">Total Scenes</div>
            <div className="summary-card-value">{totalScenes}</div>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-card-icon">⚡</div>
          <div className="summary-card-content">
            <div className="summary-card-title">Active Devices</div>
            <div className="summary-card-value">{activeDevices.active}/{activeDevices.total}</div>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-card-icon">🌡️</div>
          <div className="summary-card-content">
            <div className="summary-card-title">Temperature</div>
            <div className="summary-card-value">{environmentData.averageTemp}°C</div>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-card-icon">💧</div>
          <div className="summary-card-content">
            <div className="summary-card-title">Humidity</div>
            <div className="summary-card-value">{environmentData.humidity}%</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="dashboard-content">
        <div className="content-header">
          <div className="content-title-section">
            <h2 className="content-title">Scene List</h2>
            <p className="content-subtitle">Manage your smart home scene configurations</p>
          </div>
          <button className="new-scene-button" onClick={onCreateNew}>
            <span className="new-scene-icon">+</span>
            New Scene
          </button>
        </div>

        <div className="scenarios-container">
          {/* Active Scenarios */}
          {activeScenes.length > 0 && (
            <div className="scenarios-section">
              <div className="scenarios-section-header">
                <span className="section-dot section-dot-active"></span>
                <h3 className="scenarios-section-title">ACTIVE SCENARIOS</h3>
              </div>
              <div className="scenarios-grid">
                {activeScenes.map((scene) => (
                  <div
                    key={scene.id}
                    className="scenario-card scenario-card-active"
                    onClick={() => onSelectScene && onSelectScene(scene)}
                  >
                    <button
                      className="scenario-delete-icon-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteScene(scene.id);
                      }}
                      onMouseDown={(e) => {
                        e.currentTarget.classList.add('scenario-delete-active');
                      }}
                      onMouseUp={(e) => {
                        e.currentTarget.classList.remove('scenario-delete-active');
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.classList.remove('scenario-delete-active');
                      }}
                      title="Delete scenario"
                    >
                      <svg width="14" height="16" viewBox="0 0 14 16" fill="none">
                        <path d="M1 4H13M11 4V13C11 13.5304 10.7893 14.0391 10.4142 14.4142C10.0391 14.7893 9.53043 15 9 15H5C4.46957 15 3.96086 14.7893 3.58579 14.4142C3.21071 14.0391 3 13.5304 3 13V4M5 4V2C5 1.46957 5.21071 0.96086 5.58579 0.585786C5.96086 0.210714 6.46957 0 7 0C7.53043 0 8.03914 0.210714 8.41421 0.585786C8.78929 0.96086 9 1.46957 9 2V4" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M6 7V12M8 7V12" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
                      </svg>
                    </button>
                    <div className="scenario-card-header">
                      <h4 className="scenario-card-title">{scene.name}</h4>
                      <div className="scenario-card-meta">
                        {scene.nodeCount || (scene.triggerCount + scene.conditionCount + scene.actionCount)} Nodes · {scene.triggerCount + scene.conditionCount + scene.actionCount} Connections
                      </div>
                    </div>
                    <div className="scenario-card-footer">
                      <div className="scenario-card-icons">
                        {getNodeIcons(scene).map((icon, idx) => (
                          <span key={idx} className="scenario-icon-badge">{icon}</span>
                        ))}
                      </div>
                      <button
                        className={`scenario-toggle-btn scenario-toggle-active`}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleToggleEnabled(scene.id);
                        }}
                      >
                        <span className="toggle-icon">🔌</span>
                        <span className="toggle-text">ON</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Disabled Scenarios */}
          {disabledScenes.length > 0 && (
            <div className="scenarios-section">
              <div className="scenarios-section-header">
                <span className="section-dot section-dot-disabled"></span>
                <h3 className="scenarios-section-title">DISABLED SCENARIOS</h3>
              </div>
              <div className="scenarios-grid">
                {disabledScenes.map((scene) => (
                  <div
                    key={scene.id}
                    className="scenario-card scenario-card-disabled"
                    onClick={() => onSelectScene && onSelectScene(scene)}
                  >
                    <button
                      className="scenario-delete-icon-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteScene(scene.id);
                      }}
                      onMouseDown={(e) => {
                        e.currentTarget.classList.add('scenario-delete-active');
                      }}
                      onMouseUp={(e) => {
                        e.currentTarget.classList.remove('scenario-delete-active');
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.classList.remove('scenario-delete-active');
                      }}
                      title="Delete scenario"
                    >
                      <svg width="14" height="16" viewBox="0 0 14 16" fill="none">
                        <path d="M1 4H13M11 4V13C11 13.5304 10.7893 14.0391 10.4142 14.4142C10.0391 14.7893 9.53043 15 9 15H5C4.46957 15 3.96086 14.7893 3.58579 14.4142C3.21071 14.0391 3 13.5304 3 13V4M5 4V2C5 1.46957 5.21071 0.96086 5.58579 0.585786C5.96086 0.210714 6.46957 0 7 0C7.53043 0 8.03914 0.210714 8.41421 0.585786C8.78929 0.96086 9 1.46957 9 2V4" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M6 7V12M8 7V12" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
                      </svg>
                    </button>
                    <div className="scenario-card-header">
                      <h4 className="scenario-card-title">{scene.name}</h4>
                      <div className="scenario-card-meta">
                        {scene.nodeCount || (scene.triggerCount + scene.conditionCount + scene.actionCount)} Nodes · {scene.triggerCount + scene.conditionCount + scene.actionCount} Connections
                      </div>
                    </div>
                    <div className="scenario-card-footer">
                      <div className="scenario-card-icons">
                        {getNodeIcons(scene).map((icon, idx) => (
                          <span key={idx} className="scenario-icon-badge scenario-icon-disabled">{icon}</span>
                        ))}
                      </div>
                      <button
                        className={`scenario-toggle-btn scenario-toggle-disabled`}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleToggleEnabled(scene.id);
                        }}
                      >
                        <span className="toggle-icon">⭕</span>
                        <span className="toggle-text">OFF</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {scenes.length === 0 && (
            <div className="scenarios-empty">
              <p>No scenarios yet. Click "New Scene" to create one.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ScenesList;
