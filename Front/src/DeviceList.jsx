import React, { useState, useEffect } from "react";
import { Server, Activity, ArrowLeft, RefreshCw, Cpu, Zap, Radio, CheckCircle, XCircle } from 'lucide-react';

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
      setError("Unable to connect to Smart Home Demo Lab backend. Please ensure the server is running.");
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
  const getStatusBadge = (status) => {
    // Map device status to badges similar to logs
    const unifiedStatus = status ? status.toLowerCase() : 'unknown';

    if (unifiedStatus === 'enabled' || unifiedStatus === 'online' || unifiedStatus === 'active') {
      return (
        <span className="status-badge status-success">
          <CheckCircle size={12} /> Active
        </span>
      );
    } else if (unifiedStatus === 'disabled' || unifiedStatus === 'offline') {
      return (
        <span className="status-badge status-failed">
          <XCircle size={12} /> Offline
        </span>
      );
    } else {
      return <span className="status-badge status-unknown">{status || 'Unknown'}</span>;
    }
  };

  // Calculate stats
  const total = devices.length;
  const active = devices.filter(d => ['enabled', 'online', 'active'].includes(d.status?.toLowerCase())).length;
  const offline = devices.filter(d => ['disabled', 'offline'].includes(d.status?.toLowerCase())).length;

  return (
    <div className="orchestrator-page">
      {/* Header */}
      <header className="orchestrator-header">
        <div className="orchestrator-header-left">
          <button className="back-button" onClick={onBack}>
            <ArrowLeft size={20} />
            <span>Back</span>
          </button>
          <div className="orchestrator-title-section">
            <h1 className="orchestrator-title">
              <Server size={24} className="orchestrator-title-icon" />
              Connected Equipment
            </h1>
            <p className="orchestrator-subtitle">Information-dense view of all synchronized home devices</p>
          </div>
        </div>
        <button className="orchestrator-refresh-btn" onClick={fetchDevices} disabled={loading}>
          <RefreshCw size={16} className={loading ? "spin" : ""} />
          <span>Refresh</span>
        </button>
      </header>

      {/* Stats Cards */}
      <div className="orchestrator-stats">
        <div className="orchestrator-stat-card stat-total">
          <div className="stat-icon-wrapper">
            <Server size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{total}</div>
            <div className="stat-label">Total Devices</div>
          </div>
        </div>
        <div className="orchestrator-stat-card stat-active">
          <div className="stat-icon-wrapper">
            <CheckCircle size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{active}</div>
            <div className="stat-label">Active</div>
          </div>
        </div>
        <div className="orchestrator-stat-card stat-error">
          <div className="stat-icon-wrapper">
            <XCircle size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{offline}</div>
            <div className="stat-label">Offline/Disabled</div>
          </div>
        </div>
        {/* Placeholder for future stat or layout balance */}
        <div className="orchestrator-stat-card stat-stopped">
          <div className="stat-icon-wrapper">
            <Activity size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{loading ? 'Syncing' : 'Online'}</div>
            <div className="stat-label">System Status</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="orchestrator-table-container">
        {error && (
          <div className="orchestrator-error">
            <p>Error: {error}</p>
            <button onClick={fetchDevices}>Retry Connection</button>
          </div>
        )}

        {loading && !devices.length ? (
          <div className="orchestrator-loading">
            <RefreshCw size={32} className="loading-spinner" />
            <p>Loading equipment...</p>
          </div>
        ) : (
          !loading && devices.length === 0 ? (
            <div className="orchestrator-empty">
              <Server size={48} />
              <p>No connected equipment found</p>
            </div>
          ) : (
            <table className="orchestrator-table">
              <thead>
                <tr>
                  <th>Device Name</th>
                  <th>Entity ID</th>
                  <th>Type</th>
                  <th>Adapter</th>
                  <th>Manufacturer</th>
                  <th style={{ minWidth: '450px' }}>Capabilities</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {devices.map((device) => (
                  <tr key={device.id}>
                    <td>
                      <span className="text-indigo-400 font-medium">{device.label}</span>
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
                            <span
                              key={idx}
                              className="capability-badge"
                              title={cap.constraints ? JSON.stringify(cap.constraints, null, 2) : ''}
                            >
                              {cap.name}
                              {cap.value_type && cap.value_type !== 'void' && (
                                <span style={{ opacity: 0.7, marginLeft: '4px', fontSize: '0.9em' }}>
                                  ({cap.value_type})
                                </span>
                              )}
                            </span>
                          ))
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </div>
                    </td>
                    <td>
                      {getStatusBadge(device.status)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        )}
      </div>
    </div>
  );
};

export default DeviceList;
