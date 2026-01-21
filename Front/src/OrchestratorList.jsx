import React, { useState, useEffect } from "react";
import {
    ArrowLeft,
    Activity,
    Clock,
    AlertCircle,
    CheckCircle,
    XCircle,
    RefreshCw,
    Zap
} from 'lucide-react';

const OrchestratorList = ({ onBack }) => {
    const [executors, setExecutors] = useState([]);
    const [stats, setStats] = useState({ total: 0, active: 0, stopped: 0, error: 0 });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchExecutors();
        fetchStats();
    }, []);

    const fetchExecutors = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:8000/api/executors');
            if (!response.ok) {
                throw new Error(`Failed to fetch: ${response.status}`);
            }
            const data = await response.json();
            setExecutors(data);
            setError(null);
        } catch (err) {
            console.error("Failed to fetch executors:", err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/executors/stats/today');
            if (response.ok) {
                const data = await response.json();
                setStats(data);
            }
        } catch (err) {
            console.error("Failed to fetch executor stats:", err);
        }
    };

    const handleRefresh = () => {
        fetchExecutors();
        fetchStats();
    };

    const formatDateTime = (isoString) => {
        if (!isoString) return '-';
        const date = new Date(isoString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'active':
                return <CheckCircle size={16} className="status-icon status-active" />;
            case 'stopped':
                return <XCircle size={16} className="status-icon status-stopped" />;
            case 'error':
                return <AlertCircle size={16} className="status-icon status-error" />;
            default:
                return <Clock size={16} className="status-icon status-unknown" />;
        }
    };

    const formatTrigger = (triggerType, triggerConfig) => {
        if (!triggerType) return '-';

        const typeLabels = {
            'timer': 'Timer',
            'manual': 'Manual',
            'always_on': 'Always On',
            'device_event': 'Device Event'
        };

        const label = typeLabels[triggerType] || triggerType;
        if (triggerConfig) {
            return `${label}: ${triggerConfig}`;
        }
        return label;
    };

    const getStatusBadge = (status) => {
        const statusClasses = {
            active: 'orchestrator-status-active',
            stopped: 'orchestrator-status-stopped',
            error: 'orchestrator-status-error'
        };
        return (
            <span className={`orchestrator-status-badge ${statusClasses[status] || 'orchestrator-status-unknown'}`}>
                {getStatusIcon(status)}
                <span>{status.charAt(0).toUpperCase() + status.slice(1)}</span>
            </span>
        );
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
                            <Zap size={24} className="orchestrator-title-icon" />
                            Orchestrator
                        </h1>
                        <p className="orchestrator-subtitle">Scene execution engine status</p>
                    </div>
                </div>
                <button className="orchestrator-refresh-btn" onClick={handleRefresh}>
                    <RefreshCw size={16} />
                    <span>Refresh</span>
                </button>
            </header>

            {/* Stats Cards */}
            <div className="orchestrator-stats">
                <div className="orchestrator-stat-card stat-total">
                    <div className="stat-icon-wrapper">
                        <Activity size={24} />
                    </div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.total}</div>
                        <div className="stat-label">Total Executors</div>
                    </div>
                </div>
                <div className="orchestrator-stat-card stat-active">
                    <div className="stat-icon-wrapper">
                        <CheckCircle size={24} />
                    </div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.active}</div>
                        <div className="stat-label">Active</div>
                    </div>
                </div>
                <div className="orchestrator-stat-card stat-stopped">
                    <div className="stat-icon-wrapper">
                        <XCircle size={24} />
                    </div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.stopped}</div>
                        <div className="stat-label">Stopped</div>
                    </div>
                </div>
                <div className="orchestrator-stat-card stat-error">
                    <div className="stat-icon-wrapper">
                        <AlertCircle size={24} />
                    </div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.error}</div>
                        <div className="stat-label">Error</div>
                    </div>
                </div>
            </div>

            {/* Executors Table */}
            <div className="orchestrator-table-container">
                {loading ? (
                    <div className="orchestrator-loading">
                        <RefreshCw size={32} className="loading-spinner" />
                        <p>Loading executors...</p>
                    </div>
                ) : error ? (
                    <div className="orchestrator-error">
                        <AlertCircle size={32} />
                        <p>Error: {error}</p>
                        <button onClick={handleRefresh}>Retry</button>
                    </div>
                ) : executors.length === 0 ? (
                    <div className="orchestrator-empty">
                        <Activity size={48} />
                        <p>No executors found</p>
                        <span>Executors are created automatically when scenes are published</span>
                    </div>
                ) : (
                    <table className="orchestrator-table">
                        <thead>
                            <tr>
                                <th>Scene</th>
                                <th>Trigger</th>
                                <th>Status</th>
                                <th>Trigger Count</th>
                                <th>Last Triggered</th>
                                <th>Updated</th>
                                <th>Flow</th>
                            </tr>
                        </thead>
                        <tbody>
                            {executors.map((executor) => (
                                <tr key={executor.id} className={`executor-row executor-${executor.status}`}>
                                    <td className="executor-scene-name">
                                        <span className="scene-name-text">{executor.sceneName}</span>
                                        <span className="scene-id-text">{executor.sceneId}</span>
                                    </td>
                                    <td className="executor-trigger">
                                        <span className="trigger-text">{formatTrigger(executor.triggerType, executor.triggerConfig)}</span>
                                    </td>
                                    <td>{getStatusBadge(executor.status)}</td>
                                    <td className="executor-trigger-count">
                                        <Zap size={14} />
                                        <span>{executor.triggerCount}</span>
                                    </td>
                                    <td className="executor-datetime">{formatDateTime(executor.lastTriggeredAt)}</td>
                                    <td className="executor-datetime">{formatDateTime(executor.updatedAt)}</td>
                                    <td className="executor-flow">
                                        {executor.hasFlow ? (
                                            <span className="flow-badge flow-ready">Ready</span>
                                        ) : (
                                            <span className="flow-badge flow-empty">Empty</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default OrchestratorList;
