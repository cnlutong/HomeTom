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

      <style dangerouslySetInnerHTML={{
        __html: `
        .dashboard-content-tight {
          padding: 1.5rem 2rem;
        }
        .content-header-compact {
          margin-bottom: 1rem;
        }
        .device-table-container {
          background: #ffffff;
          border-radius: 12px;
          border: 1px solid #e2e8f0;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
          overflow: hidden;
        }
        .device-high-density-table {
          width: 100%;
          border-collapse: collapse;
          text-align: left;
          font-size: 13px;
        }
        .device-high-density-table th {
          background: #f8fafc;
          padding: 12px 16px;
          font-weight: 600;
          color: #64748b;
          text-transform: uppercase;
          letter-spacing: 0.025em;
          border-bottom: 1px solid #e2e8f0;
        }
        .device-high-density-table td {
          padding: 10px 16px;
          border-bottom: 1px solid #f1f5f9;
          color: #334155;
          vertical-align: middle;
        }
        .device-high-density-table tr:last-child td {
          border-bottom: none;
        }
        .device-high-density-table tr:hover td {
          background: #fdfdfd;
        }
        .device-table-name-cell {
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .device-table-label {
          font-weight: 600;
          color: #1e293b;
        }
        .device-table-icon {
          font-size: 16px;
          opacity: 0.8;
        }
        .device-table-code {
          font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          background: #f1f5f9;
          padding: 2px 6px;
          border-radius: 4px;
          color: #475569;
          font-size: 12px;
        }
        .device-table-badge {
          display: inline-flex;
          align-items: center;
          padding: 2px 8px;
          border-radius: 9999px;
          font-size: 11px;
          font-weight: 600;
        }
        .badge-sensor {
          background: #ecfdf5;
          color: #059669;
          border: 1px solid #d1fae5;
        }
        .badge-equipment {
          background: #fffbeb;
          color: #d97706;
          border: 1px solid #fef3c7;
        }
        .device-table-adapter {
          color: #4f46e5;
          font-weight: 500;
          font-size: 12px;
          background: #f5f3ff;
          padding: 2px 6px;
          border-radius: 4px;
        }
        .device-table-manufacturer {
          color: #64748b;
          font-size: 12px;
        }
        .device-table-status {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: #64748b;
        }
        .empty-state-padding {
          padding: 40px;
          text-align: center;
        }
        .status-dot-green {
          width: 8px;
          height: 8px;
          background: #10b981;
          border-radius: 50%;
          box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
        }
        .status-dot-gray {
          width: 8px;
          height: 8px;
          background: #94a3b8;
          border-radius: 50%;
        }
        .refresh-button {
          background: none;
          border: none;
          color: #94a3b8;
          cursor: pointer;
          padding: 8px;
          display: flex;
          align-items: center;
          transition: all 0.2s;
        }
        .refresh-button:hover:not(:disabled) {
          color: #4f46e5;
          background: #f1f5f9;
          border-radius: 6px;
        }
        .spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .device-table-capabilities {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
          max-width: 200px;
        }
        .capability-badge {
          background: #f1f5f9;
          color: #475569;
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 10px;
          border: 1px solid #e2e8f0;
          white-space: nowrap;
        }
        .text-muted {
            color: #cbd5e1;
        }
      `}} />
    </div>
  );
};

export default DeviceList;
