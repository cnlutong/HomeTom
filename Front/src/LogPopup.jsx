import React, { useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Clock, Terminal } from 'lucide-react';

const LogPopup = ({ logs, onClose, isOpen }) => {
    if (!isOpen) return null;

    useEffect(() => {
        let timer;
        if (isOpen) {
            timer = setTimeout(() => {
                onClose();
            }, 5000);
        }
        return () => clearTimeout(timer);
    }, [isOpen, onClose]);

    return (
        <div className="log-popup-container">
            <div className="log-popup-header">
                <div className="log-popup-title">
                    <Terminal size={16} />
                    <span>Execution Logs</span>
                </div>
                <button className="log-popup-close" onClick={onClose}>
                    <X size={16} />
                </button>
            </div>

            <div className="log-popup-content">
                {logs && logs.length > 0 ? (
                    <div className="log-steps">
                        {logs.map((log, index) => (
                            <div key={index} className={`log-step ${log.success ? 'log-step-success' : 'log-step-error'}`}>
                                <div className="log-step-header">
                                    <span className="log-step-number">#{log.step_number}</span>
                                    <span className="log-step-time">
                                        <Clock size={12} />
                                        {log.duration_ms}ms
                                    </span>
                                </div>

                                <div className="log-step-details">
                                    <div className="log-detail-row">
                                        <span className="log-label">Action:</span>
                                        <span className="log-value">{log.action_type || 'Unknown'}</span>
                                    </div>
                                    <div className="log-detail-row">
                                        <span className="log-label">Target:</span>
                                        <span className="log-value">{log.target || 'N/A'}</span>
                                    </div>
                                    <div className="log-detail-row">
                                        <span className="log-label">Command:</span>
                                        <span className="log-value">{log.command || 'N/A'}</span>
                                    </div>
                                    {log.error_message && (
                                        <div className="log-error-message">
                                            <AlertCircle size={12} />
                                            {log.error_message}
                                        </div>
                                    )}
                                </div>

                                <div className="log-step-status">
                                    {log.success ? (
                                        <CheckCircle size={16} className="text-green-500" />
                                    ) : (
                                        <AlertCircle size={16} className="text-red-500" />
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="log-empty">
                        No logs available for this execution.
                    </div>
                )}
            </div>
        </div>
    );
};

export default LogPopup;
