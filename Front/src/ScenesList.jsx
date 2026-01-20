import React, { useState, useEffect } from "react";
import {
  Layers,
  Clock,
  Server,
  MapPin,
  Activity,
  CloudSun,
  Plus,
  Edit2,
  Trash2,
  Power,
  CheckCircle,
  FileText,
  MoreVertical,
  Zap
} from 'lucide-react';

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

// Load scene data from backend API and localStorage
const loadScenesFromStorage = async () => {
  try {
    // Fetch from backend API
    const response = await fetch('http://localhost:8000/api/scenes');
    if (response.ok) {
      const backendScenes = await response.json();
      if (backendScenes && backendScenes.length > 0) {
        // Map backend scenes to frontend format
        return backendScenes.map(scene => ({
          ...scene,
          name: translateSceneName(scene.name)
        }));
      }
    }

    // Fallback to localStorage if backend is empty or unavailable
    const saved = localStorage.getItem("smart-home-scenes");
    if (saved) {
      const scenes = JSON.parse(saved);
      return scenes.map(scene => ({
        ...scene,
        name: translateSceneName(scene.name)
      }));
    }
  } catch (error) {
    console.error("Failed to load scenes:", error);
  }
  return []; // Return empty list instead of hardcoded data
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

function ScenesList({ onSelectScene, onCreateNew, onViewDevices, onUpdateSceneStatus, onDeleteScene }) {
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
    const loadData = async () => {
      const loadedScenes = await loadScenesFromStorage();
      if (loadedScenes) {
        setScenes(loadedScenes);
      }
    };
    loadData();
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

      // Fetch total devices from backend
      let totalCount = 5;
      try {
        const devResponse = await fetch('http://localhost:8000/api/devices/equipment');
        if (devResponse.ok) {
          const devices = await devResponse.json();
          totalCount = devices.length;
        }
      } catch (err) {
        console.error("Failed to fetch total count from backend:", err);
      }

      setActiveDevices({
        active: active,
        total: totalCount
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

  const handleStatusChange = async (sceneId, newStatus) => {
    if (onUpdateSceneStatus) {
      const success = await onUpdateSceneStatus(sceneId, newStatus);
      if (success) {
        // Refresh scenes list
        const loadedScenes = await loadScenesFromStorage();
        if (loadedScenes) {
          setScenes(loadedScenes);
        }
      }
    }
  };

  const handleToggleEnabled = async (sceneId, currentStatus) => {
    const nextStatus = currentStatus === "published" ? "disabled" : "published";
    await handleStatusChange(sceneId, nextStatus);
  };

  const handleDeleteScene = async (sceneId) => {
    if (onDeleteScene) {
      const success = await onDeleteScene(sceneId);
      if (success) {
        setScenes((prev) => {
          const updated = prev.filter((scene) => scene.id !== sceneId);
          return updated;
        });
      }
    } else {
      // Fallback for local-only deletion if no prop provided
      if (window.confirm("Are you sure you want to delete this scene?")) {
        setScenes((prev) => {
          const updated = prev.filter((scene) => scene.id !== sceneId);
          saveScenesToStorage(updated);
          return updated;
        });
      }
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

  const getTriggerTypeBadge = (scene) => {
    // Extract T0 trigger type from automationData
    // T0 trigger types are: manual, auto, always_on
    // Device triggers have type: deviceState
    if (!scene.automationData || !scene.automationData.triggers || scene.automationData.triggers.length === 0) {
      return { text: 'Manual', className: 'trigger-badge-manual' };
    }

    // Find the T0 trigger (type is manual, auto, or always_on)
    const t0Trigger = scene.automationData.triggers.find(
      t => t.type === 'manual' || t.type === 'auto' || t.type === 'always_on'
    );

    if (!t0Trigger) {
      // No T0 trigger found, default to manual
      return { text: 'Manual', className: 'trigger-badge-manual' };
    }

    const triggerType = t0Trigger.type;

    if (triggerType === 'auto') {
      return { text: 'Auto', className: 'trigger-badge-auto' };
    } else if (triggerType === 'always_on') {
      return { text: 'Always On', className: 'trigger-badge-always-on' };
    } else {
      return { text: 'Manual', className: 'trigger-badge-manual' };
    }
  };

  // Group scenes by status
  const activeScenes = scenes.filter(scene => scene.status === "published");
  const disabledScenes = scenes.filter(scene => scene.status === "disabled");
  const draftScenes = scenes.filter(scene => scene.status === "draft" || !scene.status);

  return (
    <div className="scenes-dashboard">
      {/* Header */}
      <header className="header-refactored">
        <div className="header-left">
          <div className="header-brand">
            <div className="header-logo">
              <Layers size={18} />
            </div>
            <span className="header-title-text">Home <span className="header-title-accent">Tom</span></span>
          </div>
        </div>
        <div className="header-widgets">
          <div className="header-widget">
            <Clock size={14} className="widget-icon widget-icon-blue" />
            <div className="widget-content">
              <span className="widget-label">LOCAL</span>
              <span className="widget-value">{formatTime(currentTime)}</span>
            </div>
          </div>
          <div className="header-widget header-widget-lg">
            <Server size={14} className="widget-icon widget-icon-indigo" />
            <div className="widget-content">
              <span className="widget-label">SERVER</span>
              <span className="widget-value">{formatTime(serverTime)}</span>
            </div>
          </div>
          <div className="header-widget header-widget-xl">
            <Activity size={14} className="widget-icon widget-icon-emerald" />
            <div className="widget-content">
              <span className="widget-label">UPTIME</span>
              <span className="widget-value">0h 0m</span>
            </div>
          </div>
          <div className="header-widget">
            <CloudSun size={16} className="widget-icon widget-icon-orange" />
            <div className="widget-content">
              <span className="widget-value">{environmentData.averageTemp}°C</span>
              <span className="widget-label-inline">{environmentData.weatherCondition}</span>
            </div>
          </div>
        </div>
        <div className="header-buttons">
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
        <div
          className="summary-card clickable"
          onClick={onViewDevices}
          title="View all device details"
        >
          <div className="summary-card-icon">⚡</div>
          <div className="summary-card-content">
            <div className="summary-card-title">Active Devices</div>
            <div className="summary-card-value font-bold">{activeDevices.active}/{activeDevices.total}</div>
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
                <h3 className="scenarios-section-title">Active Scenes</h3>
              </div>
              <div className="scenarios-grid">
                {activeScenes.map((scene) => (
                  <div
                    key={scene.id}
                    className="scenario-card scenario-card-active"
                    onClick={() => onSelectScene && onSelectScene(scene)}
                  >
                    <div className="scenario-card-glow"></div>
                    <div className="scenario-card-actions">
                      <button
                        className="scenario-action-icon-btn edit-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectScene && onSelectScene(scene);
                        }}
                        title="Edit scenario"
                      >
                        <Edit2 size={14} />
                      </button>
                      <button
                        className="scenario-action-icon-btn delete-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteScene(scene.id);
                        }}
                        title="Delete scenario"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>

                    <div className="scenario-card-body no-icon">
                      <div className="scenario-card-info">
                        <h4 className="scenario-card-title">{scene.name}</h4>
                        <div className="scenario-card-stats">
                          <span className="stat-item">
                            {scene.nodeCount || 0} nodes
                          </span>
                          <span className="stat-divider"></span>
                          <span className="stat-item">
                            {scene.activeCount || 0} running
                          </span>
                          <span className="stat-divider"></span>
                          <span className={`stat-item trigger-badge ${getTriggerTypeBadge(scene).className}`}>
                            {getTriggerTypeBadge(scene).text}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="scenario-card-footer">
                      <div className="scenario-card-button-group">
                        <button className="card-btn btn-active" disabled>Active</button>
                        <button
                          className="card-btn btn-secondary"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStatusChange(scene.id, "disabled");
                          }}
                        >
                          Disable
                        </button>
                        <button
                          className="card-btn btn-secondary"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStatusChange(scene.id, "draft");
                          }}
                        >
                          To Draft
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Draft Scenarios */}
          {draftScenes.length > 0 && (
            <div className="scenarios-section">
              <div className="scenarios-section-header">
                <span className="section-dot section-dot-draft"></span>
                <h3 className="scenarios-section-title">Draft Scenes</h3>
              </div>
              <div className="scenarios-grid">
                {draftScenes.map((scene) => (
                  <div
                    key={scene.id}
                    className="scenario-card scenario-card-draft"
                    onClick={() => onSelectScene && onSelectScene(scene)}
                  >
                    <div className="scenario-card-actions">
                      <button
                        className="scenario-action-icon-btn edit-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectScene && onSelectScene(scene);
                        }}
                        title="Edit scenario"
                      >
                        <Edit2 size={14} />
                      </button>
                      <button
                        className="scenario-action-icon-btn delete-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteScene(scene.id);
                        }}
                        title="Delete draft"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>

                    <div className="scenario-card-body no-icon">
                      <div className="scenario-card-info">
                        <h4 className="scenario-card-title">{scene.name}</h4>
                        <div className="scenario-card-stats">
                          <span className="stat-item">
                            {scene.nodeCount || 0} nodes
                          </span>
                          <span className="stat-divider"></span>
                          <span className="stat-item draft-badge">Draft</span>
                          <span className="stat-divider"></span>
                          <span className={`stat-item trigger-badge ${getTriggerTypeBadge(scene).className}`}>
                            {getTriggerTypeBadge(scene).text}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="scenario-card-footer">
                      <div className="scenario-card-button-group">
                        <button className="card-btn btn-draft" disabled>Draft</button>
                        <button
                          className="card-btn btn-primary"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStatusChange(scene.id, "published");
                          }}
                        >
                          Activate
                        </button>
                        <button
                          className="card-btn btn-secondary"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStatusChange(scene.id, "disabled");
                          }}
                        >
                          Disable
                        </button>
                      </div>
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
                <h3 className="scenarios-section-title">Disabled Scenes</h3>
              </div>
              <div className="scenarios-grid">
                {disabledScenes.map((scene) => (
                  <div
                    key={scene.id}
                    className="scenario-card scenario-card-disabled"
                    onClick={() => onSelectScene && onSelectScene(scene)}
                  >
                    <div className="scenario-card-actions">
                      <button
                        className="scenario-action-icon-btn edit-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectScene && onSelectScene(scene);
                        }}
                        title="Edit scenario"
                      >
                        <Edit2 size={14} />
                      </button>
                      <button
                        className="scenario-action-icon-btn delete-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteScene(scene.id);
                        }}
                        title="Delete scenario"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>

                    <div className="scenario-card-body no-icon">
                      <div className="scenario-card-info">
                        <h4 className="scenario-card-title">{scene.name}</h4>
                        <div className="scenario-card-stats">
                          <span className="stat-item">
                            {scene.nodeCount || 0} nodes
                          </span>
                          <span className="stat-divider"></span>
                          <span className="stat-item disabled-badge">Disabled</span>
                          <span className="stat-divider"></span>
                          <span className={`stat-item trigger-badge ${getTriggerTypeBadge(scene).className}`}>
                            {getTriggerTypeBadge(scene).text}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="scenario-card-footer">
                      <div className="scenario-card-button-group">
                        <button className="card-btn btn-disabled" disabled>Disabled</button>
                        <button
                          className="card-btn btn-primary"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStatusChange(scene.id, "published");
                          }}
                        >
                          Enable
                        </button>
                        <button
                          className="card-btn btn-secondary"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStatusChange(scene.id, "draft");
                          }}
                        >
                          Draft
                        </button>
                      </div>
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
