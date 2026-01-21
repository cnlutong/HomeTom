import React, { useState, useEffect } from "react";
import { Server, Activity, ArrowLeft, RefreshCw, FileText, Clock, AlertCircle, CheckCircle } from 'lucide-react';

const SceneLogs = ({ onBack }) => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [todayCount, setTodayCount] = useState(0);

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const [logsRes, statsRes] = await Promise.all([
                fetch('http://localhost:8000/api/executions?page=1&page_size=50'),
                fetch('http://localhost:8000/api/executions/stats/today')
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
            // Fallback data for demo if backend fails (can be removed later)
            // setLogs([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
    }, []);

    const getStatusBadge = (status) => {
        switch (status) {
            case 'success':
                return (
                    <span className="status-badge status-success">
                        <CheckCircle size={12} /> Success
                    </span>
                );
            case 'failed':
                return (
                    <span className="status-badge status-failed">
                        <AlertCircle size={12} /> Failed
                    </span>
                );
            case 'running':
                return (
                    <span className="status-badge status-running">
                        <Activity size={12} className="spin-slow" /> Running
                    </span>
                );
            default:
                return <span className="status-badge status-unknown">{status}</span>;
        }
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

    const formatDuration = (seconds) => {
        if (seconds === null || seconds === undefined) return '-';
        if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
        return `${seconds.toFixed(2)}s`;
    };

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
                            <Clock size={24} className="orchestrator-title-icon" />
                            Execution History
                        </h1>
                        <p className="orchestrator-subtitle">Recent automation and scene execution records</p>
                    </div>
                </div>
                <button className="orchestrator-refresh-btn" onClick={fetchLogs} disabled={loading}>
                    <RefreshCw size={16} className={loading ? "spin" : ""} />
                    <span>Refresh</span>
                </button>
            </header>

            {/* Stats Cards */}
            <div className="orchestrator-stats">
                <div className="orchestrator-stat-card stat-total">
                    <div className="stat-icon-wrapper">
                        <FileText size={24} />
                    </div>
                    <div className="stat-content">
                        <div className="stat-value">{todayCount}</div>
                        <div className="stat-label">Today's Executions</div>
                    </div>
                </div>
                <div className="orchestrator-stat-card stat-active">
                    <div className="stat-icon-wrapper">
                        <Activity size={24} />
                    </div>
                    <div className="stat-content">
                        <div className="stat-value">{loading ? "Syncing..." : "Online"}</div>
                        <div className="stat-label">System Status</div>
                    </div>
                </div>
                {/* Placeholders to fill the grid if needed, or leave as 2 cards.
                     Orchestrator stats grid is 4 columns.
                     We can add empty or relevant cards. For now, maybe just 2 is fine or add placeholders.
                     Let's add 2 placeholders to keep layout consistent if grid expects 4,
                     or we can leave it and it will just take 2 spots.
                     Actually the CSS grid is 4 columns. Let's add placeholders or relevant info.
                  */}
                <div className="orchestrator-stat-card stat-stopped">
                    <div className="stat-icon-wrapper">
                        <CheckCircle size={24} />
                    </div>
                    <div className="stat-content">
                        <div className="stat-value">{logs.filter(l => l.status === 'success').length}</div>
                        <div className="stat-label">Success (Page)</div>
                    </div>
                </div>
                <div className="orchestrator-stat-card stat-error">
                    <div className="stat-icon-wrapper">
                        <AlertCircle size={24} />
                    </div>
                    <div className="stat-content">
                        <div className="stat-value">{logs.filter(l => l.status === 'failed').length}</div>
                        <div className="stat-label">Failed (Page)</div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="orchestrator-table-container">
                {error && (
                    <div className="orchestrator-error">
                        <p>Error: {error}</p>
                        <button onClick={fetchLogs}>Retry Connection</button>
                    </div>
                )}

                {loading && !logs.length ? (
                    <div className="orchestrator-loading">
                        <RefreshCw size={32} className="loading-spinner" />
                        <p>Loading records...</p>
                    </div>
                ) : (
                    !loading && logs.length === 0 ? (
                        <div className="orchestrator-empty">
                            <FileText size={48} />
                            <p>No execution records found</p>
                        </div>
                    ) : (
                        <table className="orchestrator-table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Scene</th>
                                    <th>Execution ID</th>
                                    <th>Scene ID</th>
                                    <th>Trigger</th>
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
                                                {formatTime(log.started_at)}
                                            </div>
                                        </td>
                                        <td>
                                            <span className="text-indigo-400 font-medium">{log.scene_name}</span>
                                        </td>
                                        <td>
                                            <code className="device-table-code">{log.id}</code>
                                        </td>
                                        <td>
                                            <code className="device-table-code">{log.scene_id}</code>
                                        </td>
                                        <td>
                                            <span className="trigger-badge">
                                                {log.trigger_source}
                                            </span>
                                        </td>
                                        <td>
                                            {getStatusBadge(log.status)}
                                        </td>
                                        <td>
                                            <span className="duration-text">{formatDuration(log.duration)}</span>
                                        </td>
                                        <td>
                                            {log.error_message ? (
                                                <span className="error-message" title={log.error_message}>
                                                    {log.error_message.length > 50 ? log.error_message.slice(0, 50) + '...' : log.error_message}
                                                </span>
                                            ) : (
                                                <span className="text-muted text-xs">No errors</span>
                                            )}
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

export default SceneLogs;
