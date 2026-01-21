import React, { useState, useEffect } from "react";
import { Server, Activity, ArrowLeft, RefreshCw, Cpu, Zap, Radio } from 'lucide-react';

const DeviceList = ({ onBack }) => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDevices = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/devices/equipment');
      if (!response.ok) {
        throw new Error('Failed to fetch devices');
      }
      const data = await response.json();
      setDevices(data);
      setError(null);
    } catch (err) {
      console.error("Error fetching devices:", err);
      setError("Unable to connect to HomeTom backend. Please ensure the server is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  const getDeviceIcon = (device) => {
    if (device.icon) return <span className="device-table-icon">{device.icon}</span>;

    switch (device.type) {
      case 'sensor': return <Radio size={16} className="text-emerald-400" />;
      case 'equipment': return <Zap size={16} className="text-amber-400" />;
      default: return <Cpu size={16} className="text-slate-400" />;
    }
  };

  return (
    <div className="scenes-dashboard">
      {/* Header */}
      <header className="header-refactored">
        <div className="header-left">
          <button className="header-back-btn" onClick={onBack} title="Back to Scenes">
            <ArrowLeft size={20} />
          </button>
          <div className="header-brand">
            <span className="header-title-text">Backend <span className="header-title-accent">Devices</span></span>
          </div>
        </div>
        <div className="header-widgets">
          <div className="header-widget">
            <Server size={14} className="widget-icon widget-icon-indigo" />
            <div className="widget-content">
              <span className="widget-label">TOTAL</span>
              <span className="widget-value">{devices.length}</span>
            </div>
          </div>
          <div className="header-widget">
            <Activity size={14} className="widget-icon widget-icon-emerald" />
            <div className="widget-content">
              <span className="widget-label">STATUS</span>
              <span className="widget-value">{loading ? "Syncing..." : "Online"}</span>
            </div>
          </div>
          <button className="refresh-button" onClick={fetchDevices} disabled={loading}>
            <RefreshCw size={16} className={loading ? "spin" : ""} />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="dashboard-content dashboard-content-tight">
        <div className="content-header content-header-compact">
          <div className="content-title-section">
            <h2 className="content-title">Connected Equipment</h2>
            <p className="content-subtitle">Information-dense view of all synchronized home devices</p>
          </div>
        </div>

        {error && (
          <div className="error-container">
            <p className="error-text">{error}</p>
            <button className="retry-button" onClick={fetchDevices}>Retry Connection</button>
          </div>
        )}

        {loading && !devices.length ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Synchronizing device metadata...</p>
          </div>
        ) : (
          <div className="device-table-container">
            <table className="device-high-density-table">
              <thead>
                <tr>
                  <th>Device Name</th>
                  <th>Entity ID</th>
                  <th>Type</th>
                  <th>Adapter</th>
                  <th>Manufacturer</th>
                  <th>Capabilities</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {devices.map((device) => (
                  <tr key={device.id}>
                    <td>
                      <div className="device-table-name-cell">
                        {getDeviceIcon(device)}
                        <span className="device-table-label">{device.label}</span>
                      </div>
                    </td>
                    <td><code className="device-table-code">{device.entity_id}</code></td>
                    <td>
                      <span className={`device-table-badge ${device.type === 'sensor' ? 'badge-sensor' : 'badge-equipment'}`}>
                        {device.type.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <span className="device-table-adapter">{device.adapter_type || 'Unknown'}</span>
                    </td>
                    <td>
                      <span className="device-table-manufacturer">{device.manufacturer || 'Generic'}</span>
                    </td>
                    <td>
                      <div className="device-table-capabilities">
                        {device.capabilities && device.capabilities.length > 0 ? (
                          device.capabilities.map((cap, idx) => (
                            <span key={idx} className="capability-badge">
                              {cap.name}
                            </span>
                          ))
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </div>
                    </td>
                    <td>
                      <div className="device-table-status">
                        <span className={device.status === 'enabled' ? "status-dot-green" : "status-dot-gray"}></span>
                        <span>{device.status ? device.status.charAt(0).toUpperCase() + device.status.slice(1) : 'Active'}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {devices.length === 0 && !loading && (
              <div className="empty-state-padding">
                <p className="text-slate-400">No devices found on the backend server.</p>
              </div>
            )}
          </div>
        )}
      </div>

    </div>
  );
};

export default DeviceList;
