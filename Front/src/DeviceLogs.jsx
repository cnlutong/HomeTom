import React, { useState, useEffect } from "react";
import { Server, Activity, ArrowLeft, RefreshCw, FileText, Clock, AlertCircle, CheckCircle, Terminal } from 'lucide-react';

const DeviceLogs = ({ onBack }) => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [todayCount, setTodayCount] = useState(0);

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const [logsRes, statsRes] = await Promise.all([
                fetch('http://localhost:8000/api/device-logs?page=1&page_size=50'),
                fetch('http://localhost:8000/api/device-logs/stats/today')
            ]);

            if (!logsRes.ok || !statsRes.ok) {
                throw new Error('Failed to fetch data');
            }

            const logsData = await logsRes.json();
            const statsData = await statsRes.json();

            setLogs(logsData.items || []);
            setTodayCount(statsData.count || 0);
            setError(null);
        } catch (err) {
            console.error("Error fetching logs:", err);
            setError("Unable to connect to HomeTom backend. Please ensure the server is running.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
    }, []);

    const getStatusBadge = (success) => {
        if (success) {
            return (
                <span className="status-badge status-success">
                    <CheckCircle size={12} /> Success
                </span>
            );
        } else {
            return (
                <span className="status-badge status-failed">
                    <AlertCircle size={12} /> Failed
                </span>
            );
        }
    };

    const getActionBadge = (type) => {
        return (
            <span className="trigger-badge">
                {type}
            </span>
        );
    };

    const formatTime = (isoString) => {
        if (!isoString) return '-';

        try {
            const date = new Date(isoString);
            const formatter = new Intl.DateTimeFormat('en-US', {
                month: 'short', day: 'numeric',
                hour: '2-digit', minute: '2-digit', second: '2-digit',
                hour12: false,
                timeZoneName: 'short'
            });

            const parts = formatter.formatToParts(date);

            return (
                <span>
                    {parts.map((part, index) => (
                        <span
                            key={index}
                            className={part.type === 'timeZoneName' ? 'text-timezone-dim' : ''}
                        >
                            {part.value}
                        </span>
                    ))}
                </span>
            );
        } catch (e) {
            console.error("Time formatting error:", e);
            return isoString;
        }
    };

    const formatDuration = (ms) => {
        if (ms === null || ms === undefined) return '-';
        if (ms < 1000) return `${ms}ms`;
        return `${(ms / 1000).toFixed(2)}s`;
    };

    return (
        <div className="scenes-dashboard">
            {/* Header */}
            <header className="header-refactored">
                <div className="header-left">
                    <button className="header-back-btn" onClick={onBack} title="Back">
                        <ArrowLeft size={20} />
                    </button>
                    <div className="header-brand">
                        <span className="header-title-text">Device <span className="header-title-accent">Logs</span></span>
                    </div>
                </div>
                <div className="header-widgets">
                    <div className="header-widget">
                        <Terminal size={14} className="widget-icon widget-icon-indigo" />
                        <div className="widget-content">
                            <span className="widget-label">TODAY</span>
                            <span className="widget-value">{todayCount}</span>
                        </div>
                    </div>
                    <div className="header-widget">
                        <Activity size={14} className="widget-icon widget-icon-emerald" />
                        <div className="widget-content">
                            <span className="widget-label">STATUS</span>
                            <span className="widget-value">{loading ? "Syncing..." : "Online"}</span>
                        </div>
                    </div>
                    <button className="refresh-button" onClick={fetchLogs} disabled={loading}>
                        <RefreshCw size={16} className={loading ? "spin" : ""} />
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <div className="dashboard-content dashboard-content-tight">
                <div className="content-header content-header-compact">
                    <div className="content-title-section">
                        <h2 className="content-title">Device Execution History</h2>
                        <p className="content-subtitle">Detailed record of device commands and state changes</p>
                    </div>
                </div>

                {error && (
                    <div className="error-container">
                        <p className="error-text">{error}</p>
                        <button className="retry-button" onClick={fetchLogs}>Retry Connection</button>
                    </div>
                )}

                {loading && !logs.length ? (
                    <div className="loading-container">
                        <div className="loading-spinner"></div>
                        <p>Loading records...</p>
                    </div>
                ) : (
                    <div className="device-table-container">
                        <table className="device-high-density-table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Scene</th>
                                    <th>Log ID</th>
                                    <th>Execution ID</th>
                                    <th>Target Device</th>
                                    <th>Command</th>
                                    <th>Action</th>
                                    <th>Status</th>
                                    <th>Duration</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {logs.map((log) => (
                                    <tr key={log.id}>
                                        <td>
                                            <div className="log-time">
                                                <Clock size={14} className="text-slate-400" />
                                                {formatTime(log.created_at)}
                                            </div>
                                        </td>
                                        <td>
                                            <span className="text-indigo-400 font-medium">{log.scene_name}</span>
                                        </td>
                                        <td>
                                            <code className="text-slate-400 text-xs">{log.id}</code>
                                        </td>
                                        <td>
                                            <code className="device-table-code" style={{ fontSize: '10px' }}>{log.execution_id}</code>
                                        </td>
                                        <td>
                                            <code className="device-table-code">{log.target}</code>
                                        </td>
                                        <td>
                                            <span className="device-table-manufacturer">{log.command}</span>
                                        </td>
                                        <td>
                                            {getActionBadge(log.action_type)}
                                        </td>
                                        <td>
                                            {getStatusBadge(log.success)}
                                        </td>
                                        <td>
                                            <span className="duration-text">{formatDuration(log.duration_ms)}</span>
                                        </td>
                                        <td>
                                            {log.error_message ? (
                                                <span className="error-message" title={log.error_message}>
                                                    {log.error_message.length > 50 ? log.error_message.slice(0, 50) + '...' : log.error_message}
                                                </span>
                                            ) : (
                                                <span className="text-muted text-xs">OK</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {logs.length === 0 && !loading && (
                            <div className="empty-state-padding">
                                <p className="text-slate-400">No device execution records found.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default DeviceLogs;
