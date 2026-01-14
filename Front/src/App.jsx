import React, { useCallback, useMemo, useState, useEffect, useRef } from "react";
import ScenesList from "./ScenesList.jsx";
import DeviceList from "./DeviceList.jsx";
import "./styles.css";
import {
  ArrowLeft,
  Layers,
  Clock,
  Server,
  Activity,
  CloudSun,
  Play,
  FileJson,
  RotateCcw
} from 'lucide-react';

const USER_SOURCE = {
  id: "user-source",
  label: "Residents",
  icon: "👥",
  type: "user",
};

const initialSidebarSections = [
  {
    title: "Triggers",
    items: [
      { icon: "📡", label: "Motion Sensor", type: "sensor" },
      { icon: "📶", label: "Sound Sensor", type: "sensor" },
      { icon: "🌡️", label: "Temperature Sensor", type: "sensor" },
    ],
  },
  {
    title: "Conditions",
    items: [
      { icon: "⏰", label: "Time", type: "scene" },
      { icon: "🌡️", label: "Temperature Threshold", type: "scene" },
      { icon: "💧", label: "Humidity Threshold", type: "scene" },
    ],
  },
  {
    title: "Equipment List",
    items: [
      { icon: "💡", label: "Main light", type: "equipment" },
      { icon: "💡", label: "Lamp", type: "equipment" },
      { icon: "💡", label: "Ceiling", type: "equipment" },
      { icon: "📺", label: "TV", type: "equipment" },
      { icon: "🪟", label: "Curtain", type: "equipment" },
      { icon: "❄️", label: "Conditioner", type: "equipment" },
    ],
  },
];

const defaultActions = [];

function Header({ onReset, onPreviewJson, onImportJson, onBackToScenes, sceneName }) {
  const [localTime, setLocalTime] = useState(new Date());
  const [uptime, setUptime] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setLocalTime(new Date());
      setUptime(prev => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatUptime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return `${h}h ${m} m`;
  };

  const serverTimeStr = localTime.toISOString().split('T')[1].split('.')[0];
  const localTimeStr = localTime.toLocaleTimeString('zh-CN', { hour12: false });

  return (
    <header className="header-refactored">
      <div className="header-left">
        {onBackToScenes && (
          <button className="header-back-btn" onClick={onBackToScenes}>
            <ArrowLeft size={20} />
          </button>
        )}
        <div className="header-brand">
          {!onBackToScenes ? (
            <>
              <div className="header-logo">
                <Layers size={18} />
              </div>
              <span className="header-title-text">Home <span className="header-title-accent">Tom</span></span>
            </>
          ) : (
            <div className="header-scene-info">
              <span className="header-scene-name">
                {sceneName || 'Workflow Editor'}
                <span className="header-scene-badge">Active</span>
              </span>
              <span className="header-scene-id">Workflow ID: {Math.floor(Math.random() * 10000)}</span>
            </div>
          )}
        </div>
      </div>

      <div className="header-widgets">
        <div className="header-widget">
          <Clock size={14} className="widget-icon widget-icon-blue" />
          <div className="widget-content">
            <span className="widget-label">LOCAL</span>
            <span className="widget-value">{localTimeStr}</span>
          </div>
        </div>
        <div className="header-widget header-widget-lg">
          <Server size={14} className="widget-icon widget-icon-indigo" />
          <div className="widget-content">
            <span className="widget-label">SERVER</span>
            <span className="widget-value">{serverTimeStr}</span>
          </div>
        </div>
        <div className="header-widget header-widget-xl">
          <Activity size={14} className="widget-icon widget-icon-emerald" />
          <div className="widget-content">
            <span className="widget-label">UPTIME</span>
            <span className="widget-value">{formatUptime(uptime)}</span>
          </div>
        </div>
        <div className="header-widget">
          <CloudSun size={16} className="widget-icon widget-icon-orange" />
          <div className="widget-content">
            <span className="widget-value">26°C</span>
            <span className="widget-label-inline">多云</span>
          </div>
        </div>
      </div>

      <div className="header-buttons">
        <button className="header-btn header-btn-primary" onClick={onPreviewJson}>
          <Play size={16} />
          <span>Execute</span>
        </button>
        <button className="header-btn header-btn-purple" onClick={onImportJson}>
          <FileJson size={16} />
          <span>Import</span>
        </button>
        <button className="header-btn header-btn-danger" onClick={onReset}>
          <RotateCcw size={16} />
          <span>Reset</span>
        </button>
      </div>
    </header>
  );
}

function SidebarSection({ title, items, onItemDragStart, onItemDoubleClick, onAddItem }) {
  const [query, setQuery] = useState("");

  const filteredItems = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) return items;
    return items.filter((item) =>
      item.label.toLowerCase().includes(normalizedQuery)
    );
  }, [items, query]);

  const isEquipmentList = title === "Equipment List";
  const isTriggerList = title === "Triggers";
  const isConditionList = title === "Conditions";
  const isScrollable = isEquipmentList || isTriggerList || isConditionList;
  const showAddButton = isEquipmentList || isTriggerList || isConditionList;

  const getAddButtonTitle = () => {
    if (isEquipmentList) return "Add new equipment";
    if (isTriggerList) return "Add new trigger";
    if (isConditionList) return "Add new condition";
    return "Add new item";
  };

  const getTitleClassName = () => {
    if (isEquipmentList) return "sidebar-title sidebar-title-equipment";
    if (isTriggerList) return "sidebar-title sidebar-title-sensor";
    if (isConditionList) return "sidebar-title sidebar-title-scene";
    return "sidebar-title";
  };

  return (
    <section className="sidebar-section">
      <h2 className={getTitleClassName()}>{title}</h2>
      <div className="search-bar-container">
        <div className="search-bar">
          <span className="search-icon">🔍</span>
          <input
            placeholder="Search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        {showAddButton && (
          <button
            className="add-item-button"
            onClick={() => onAddItem?.(title)}
            title={getAddButtonTitle()}
          >
            ➕
          </button>
        )}
      </div>
      <div className={`sidebar - items ${isScrollable ? "sidebar-items-scrollable" : ""} `}>
        {filteredItems.length ? (
          filteredItems.map((item, idx) => (
            <div
              key={idx}
              className="sidebar-item"
              draggable
              onDragStart={(e) => onItemDragStart?.(e, item)}
              onDoubleClick={() => onItemDoubleClick?.(item, title)}
            >
              <div className="sidebar-item-icon">{item.icon}</div>
              <div className="sidebar-item-label">{item.label}</div>
            </div>
          ))
        ) : (
          <div className="sidebar-empty">No results</div>
        )}
      </div>
    </section>
  );
}

function Sidebar({ onItemDragStart, onItemDoubleClick, sidebarSections, onAddItem }) {
  return (
    <aside className="sidebar">
      {sidebarSections.map((section) => (
        <SidebarSection
          key={section.title}
          title={section.title}
          items={section.items}
          onItemDragStart={onItemDragStart}
          onItemDoubleClick={onItemDoubleClick}
          onAddItem={onAddItem}
        />
      ))}
    </aside>
  );
}

function EditItemModal({ item, sectionTitle, onClose, onSave, onDelete }) {
  const [editedLabel, setEditedLabel] = useState(item?.label || "");
  const [editedIcon, setEditedIcon] = useState(item?.icon || "");

  if (!item) return null;

  const handleSave = () => {
    if (editedLabel.trim()) {
      onSave?.({
        ...item,
        label: editedLabel.trim(),
        icon: editedIcon,
      });
      onClose();
    }
  };

  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete "${item.label}" ? `)) {
      onDelete?.(item);
      onClose();
    }
  };

  return (
    <div className="edit-modal-overlay" onClick={onClose}>
      <div className="edit-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="edit-modal-header">
          <h3>Edit {sectionTitle} Item</h3>
          <button className="edit-modal-close" onClick={onClose}>×</button>
        </div>
        <div className="edit-modal-body">
          <div className="edit-form-group">
            <label>Icon:</label>
            <input
              type="text"
              value={editedIcon}
              onChange={(e) => setEditedIcon(e.target.value)}
              placeholder="Enter emoji or icon"
              className="edit-icon-input"
            />
          </div>
          <div className="edit-form-group">
            <label>Name:</label>
            <input
              type="text"
              value={editedLabel}
              onChange={(e) => setEditedLabel(e.target.value)}
              placeholder="Enter item name"
              className="edit-label-input"
            />
          </div>
        </div>
        <div className="edit-modal-footer">
          <button className="pill-button pill-button-danger" onClick={handleDelete}>
            Delete
          </button>
          <div style={{ display: "flex", gap: "1rem" }}>
            <button className="pill-button" onClick={onClose}>
              Cancel
            </button>
            <button className="pill-button" onClick={handleSave}>
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function AddItemModal({ sectionTitle, onClose, onSave }) {
  const [newLabel, setNewLabel] = useState("");
  const [newIcon, setNewIcon] = useState("");

  const getItemType = () => {
    if (sectionTitle === "Equipment List") return "equipment";
    if (sectionTitle === "Triggers") return "sensor";
    if (sectionTitle === "Conditions") return "scene";
    return "equipment";
  };

  const handleSave = () => {
    if (newLabel.trim()) {
      onSave?.({
        icon: newIcon || "🔘",
        label: newLabel.trim(),
        type: getItemType(),
      });
      onClose();
    }
  };

  return (
    <div className="edit-modal-overlay" onClick={onClose}>
      <div className="edit-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="edit-modal-header">
          <h3>Add New {sectionTitle} Item</h3>
          <button className="edit-modal-close" onClick={onClose}>×</button>
        </div>
        <div className="edit-modal-body">
          <div className="edit-form-group">
            <label>Icon:</label>
            <input
              type="text"
              value={newIcon}
              onChange={(e) => setNewIcon(e.target.value)}
              placeholder="Enter emoji or icon (optional)"
              className="edit-icon-input"
            />
          </div>
          <div className="edit-form-group">
            <label>Name:</label>
            <input
              type="text"
              value={newLabel}
              onChange={(e) => setNewLabel(e.target.value)}
              placeholder="Enter item name"
              className="edit-label-input"
            />
          </div>
        </div>
        <div className="edit-modal-footer">
          <div style={{ display: "flex", gap: "1rem", marginLeft: "auto" }}>
            <button className="pill-button" onClick={onClose}>
              Cancel
            </button>
            <button className="pill-button" onClick={handleSave}>
              Add
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ToggleRow({ label, icon, actionId, action, onUpdate, onRemove }) {
  const isEnabled = action?.isEnabled !== false;

  const handleToggleClick = (e) => {
    e.stopPropagation();
    if (onUpdate && actionId) {
      onUpdate(actionId, { isEnabled: !isEnabled });
    }
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    if (onRemove && actionId) {
      onRemove(actionId);
    }
  };

  return (
    <div className="toggle-row">
      <span className="toggle-label">
        {icon && <span className="toggle-icon">{icon}</span>}
        {label}
      </span>
      <div className="toggle-row-actions">
        <div
          className={`toggle -switch ${isEnabled ? 'toggle-switch-on' : ''}`}
          onClick={handleToggleClick}
          style={{ cursor: 'pointer' }}
        >
          <div className="toggle-knob" />
        </div>
        <button
          className="action-remove-button"
          onClick={handleRemove}
          title="Remove from canvas"
        >
          ×
        </button>
      </div>
    </div>
  );
}

function SliderRow({ label, compact, icon, actionId, action, onUpdate, onRemove }) {
  const value = action?.value ?? (compact ? 50 : 0);
  const min = action?.min ?? 0;
  const max = action?.max ?? 100;
  const percentage = ((value - min) / (max - min)) * 100;

  const handleSliderChange = (e) => {
    e.stopPropagation();
    if (onUpdate && actionId) {
      onUpdate(actionId, { value: parseInt(e.target.value) });
    }
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    if (onRemove && actionId) {
      onRemove(actionId);
    }
  };

  return (
    <div className="toggle-row">
      <span className="toggle-label">
        {icon && <span className="toggle-icon">{icon}</span>}
        {label}
      </span>
      <div className="toggle-row-actions">
        <div className="slider-wrapper">
          <input
            type="range"
            min={min}
            max={max}
            value={value}
            onChange={handleSliderChange}
            className={compact ? "slider slider-compact" : "slider"}
            style={{ '--value': `${percentage}% ` }}
          />
        </div>
        <button
          className="action-remove-button"
          onClick={handleRemove}
          title="Remove from canvas"
        >
          ×
        </button>
      </div>
    </div>
  );
}

function SceneRow({ action, onUpdate, onRemove }) {
  const handleRemove = () => {
    if (onRemove && action.id) {
      onRemove(action.id);
    }
  };
  if (action.label === "Temperature") {
    const minTemp = -15;
    const maxTemp = 45;
    const value = action.temperatureValue ?? 20;
    const percentage = ((value - minTemp) / (maxTemp - minTemp)) * 100;
    return (
      <div className="scene-row">
        <div className="toggle-row">
          <span className="toggle-label">
            {action.icon && <span className="toggle-icon">{action.icon}</span>}
            {action.label}:
          </span>
          <button
            className="scene-remove-button"
            onClick={handleRemove}
            title="Remove from canvas"
          >
            ×
          </button>
        </div>
        <div className="scene-control">
          <div className="slider-wrapper">
            <input
              type="range"
              min={minTemp}
              max={maxTemp}
              value={value}
              onChange={(e) => onUpdate?.(action.id, { temperatureValue: parseInt(e.target.value) })}
              className="temperature-slider"
              style={{ '--value': `${percentage}% ` }}
            />
          </div>
          <span className="scene-value">{value}°C</span>
        </div>
      </div>
    );
  }

  if (action.label === "Humidity Threshold" || action.label === "Humidity") {
    const value = action.humidityValue ?? 60;
    const percentage = (value / 100) * 100;
    return (
      <div className="scene-row">
        <div className="toggle-row">
          <span className="toggle-label">
            {action.icon && <span className="toggle-icon">{action.icon}</span>}
            {action.label}:
          </span>
          <button
            className="scene-remove-button"
            onClick={handleRemove}
            title="Remove from canvas"
          >
            ×
          </button>
        </div>
        <div className="scene-control">
          <div className="slider-wrapper">
            <input
              type="range"
              min="0"
              max="100"
              value={value}
              onChange={(e) => onUpdate?.(action.id, { humidityValue: parseInt(e.target.value) })}
              className="humidity-slider"
              style={{ '--value': `${percentage}% ` }}
            />
          </div>
          <span className="scene-value">{value}%</span>
        </div>
      </div>
    );
  }

  if (action.label === "Time") {
    const timeValue = action.timeValue ?? "17:00";
    return (
      <div className="scene-row">
        <div className="toggle-row">
          <span className="toggle-label">
            {action.icon && <span className="toggle-icon">{action.icon}</span>}
            {action.label}:
          </span>
          <button
            className="scene-remove-button"
            onClick={handleRemove}
            title="Remove from canvas"
          >
            ×
          </button>
        </div>
        <div className="scene-control">
          <input
            type="time"
            value={timeValue}
            onChange={(e) => onUpdate?.(action.id, { timeValue: e.target.value })}
            className="time-input"
          />
        </div>
      </div>
    );
  }

  // Default toggle for other scene types
  return (
    <ToggleRow
      label={`${action.label}: `}
      icon={action.icon}
    />
  );
}

function ConnectionLines({ connections, nodeRefs, connectingFrom, onConnectionDelete, actions, onConnectionUpdate, USER_SOURCE }) {
  const [hoveredConnection, setHoveredConnection] = useState(null);
  const [draggingEndpoint, setDraggingEndpoint] = useState(null); // { connection, isSource, mousePos: {x, y} }
  const [dragTarget, setDragTarget] = useState(null); // nodeId that can be connected to

  // Handle mouse move for dragging endpoints
  useEffect(() => {
    if (!draggingEndpoint) return;

    const handleMouseMove = (e) => {
      const container = document.querySelector('.canvas-node-sequence');
      if (!container) return;

      const containerRect = container.getBoundingClientRect();
      const scrollLeft = container.scrollLeft || 0;
      const scrollTop = container.scrollTop || 0;

      const mouseX = e.clientX - containerRect.left + scrollLeft;
      const mouseY = e.clientY - containerRect.top + scrollTop;

      setDraggingEndpoint(prev => ({
        ...prev,
        mousePos: { x: mouseX, y: mouseY }
      }));

      // Check which node the mouse is over
      let targetNodeId = null;
      const allNodes = [USER_SOURCE, ...actions];

      for (const node of allNodes) {
        const nodeRef = nodeRefs.current[node.id];
        if (!nodeRef) continue;

        const rect = nodeRef.getBoundingClientRect();
        const nodeX = rect.left - containerRect.left + scrollLeft;
        const nodeY = rect.top - containerRect.top + scrollTop;

        if (mouseX >= nodeX && mouseX <= nodeX + rect.width &&
          mouseY >= nodeY && mouseY <= nodeY + rect.height) {
          targetNodeId = node.id;
          break;
        }
      }

      setDragTarget(targetNodeId);
    };

    const handleMouseUp = () => {
      if (draggingEndpoint && dragTarget && onConnectionUpdate) {
        const { connection, isSource } = draggingEndpoint;

        // Get node types for validation
        const allNodes = [USER_SOURCE, ...actions];
        const sourceNode = allNodes.find(n => n.id === (isSource ? connection.from : connection.to));
        const targetNode = allNodes.find(n => n.id === dragTarget);

        if (sourceNode && targetNode) {
          const sourceType = sourceNode.type || "user";
          const targetType = targetNode.type || "equipment";

          // Check if connection is valid
          if (canConnect(sourceType, targetType)) {
            // Update connection
            if (isSource) {
              // Changing source (from)
              onConnectionUpdate(connection, { from: dragTarget, to: connection.to });
            } else {
              // Changing target (to)
              onConnectionUpdate(connection, { from: connection.from, to: dragTarget });
            }
          }
        }
      }

      setDraggingEndpoint(null);
      setDragTarget(null);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [draggingEndpoint, dragTarget, actions, USER_SOURCE, nodeRefs, onConnectionUpdate]);

  const getNodePosition = (nodeId, isSource = true) => {
    const nodeRef = nodeRefs.current[nodeId];
    if (!nodeRef) return null;

    const rect = nodeRef.getBoundingClientRect();
    const container = nodeRef.closest('.canvas-node-sequence');
    if (!container) return null;

    const containerRect = container.getBoundingClientRect();
    const scrollLeft = container.scrollLeft || 0;
    const scrollTop = container.scrollTop || 0;

    // Get node edge position (output at right edge, input at left edge for horizontal layout)
    const edgeOffset = 0; // Directly use node edge

    return {
      x: (isSource ? rect.right - edgeOffset : rect.left + edgeOffset) - containerRect.left + scrollLeft,
      y: rect.top + rect.height / 2 - containerRect.top + scrollTop,
    };
  };

  const renderConnection = (connection) => {
    const fromPos = getNodePosition(connection.from, true);
    const toPos = getNodePosition(connection.to, false);

    if (!fromPos || !toPos) return null;

    const isHovered = hoveredConnection === connection;
    const dx = toPos.x - fromPos.x;
    const dy = toPos.y - fromPos.y;

    // Calculate control points for smooth bezier curve (horizontal layout)
    // Use a smoother curve with better control point positioning
    const curveOffset = Math.max(80, Math.abs(dx) * 0.4);
    const cp1x = fromPos.x + curveOffset;
    const cp1y = fromPos.y;
    const cp2x = toPos.x - curveOffset;
    const cp2y = toPos.y;

    // Arrow head calculations
    const angle = Math.atan2(dy, dx);
    const arrowLength = 8;
    const arrowX = toPos.x - Math.cos(angle) * 12;
    const arrowY = toPos.y - Math.sin(angle) * 12;

    const arrowPoints = [
      `${arrowX},${arrowY} `,
      `${arrowX - arrowLength * Math.cos(angle - Math.PI / 6)},${arrowY - arrowLength * Math.sin(angle - Math.PI / 6)} `,
      `${arrowX - arrowLength * Math.cos(angle + Math.PI / 6)},${arrowY - arrowLength * Math.sin(angle + Math.PI / 6)} `,
    ].join(' ');

    const pathId = `connection - ${connection.from} -${connection.to} `;
    const isDraggingThis = draggingEndpoint?.connection === connection;
    const endpointRadius = 6;

    // Handle endpoint drag start
    const handleEndpointMouseDown = (e, isSource) => {
      e.stopPropagation();
      const container = document.querySelector('.canvas-node-sequence');
      if (!container) return;

      const containerRect = container.getBoundingClientRect();
      const scrollLeft = container.scrollLeft || 0;
      const scrollTop = container.scrollTop || 0;

      setDraggingEndpoint({
        connection,
        isSource,
        mousePos: {
          x: e.clientX - containerRect.left + scrollLeft,
          y: e.clientY - containerRect.top + scrollTop
        }
      });
    };

    return (
      <g
        key={pathId}
        className="connection-line-group"
        onMouseEnter={() => !isDraggingThis && setHoveredConnection(connection)}
        onMouseLeave={() => !isDraggingThis && setHoveredConnection(null)}
        onClick={(e) => {
          e.stopPropagation();
          if (!isDraggingThis && onConnectionDelete && window.confirm("Delete this connection?")) {
            onConnectionDelete(connection.from, connection.to);
          }
        }}
        style={{ cursor: 'pointer', pointerEvents: 'all' }}
      >
        <path
          d={`M ${fromPos.x} ${fromPos.y} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${toPos.x} ${toPos.y} `}
          fill="none"
          stroke={isHovered ? "#4a90e2" : "#6b7280"}
          strokeWidth={isHovered ? 2.5 : 2}
          strokeLinecap="round"
          className="connection-path"
        />
        <polygon
          points={arrowPoints}
          fill={isHovered ? "#4a90e2" : "#6b7280"}
          className="connection-arrow"
        />
        {/* Draggable endpoints */}
        <circle
          cx={fromPos.x}
          cy={fromPos.y}
          r={endpointRadius}
          fill={isHovered ? "#4a90e2" : "#6b7280"}
          stroke="#ffffff"
          strokeWidth={2}
          style={{ cursor: 'grab' }}
          onMouseDown={(e) => handleEndpointMouseDown(e, true)}
        />
        <circle
          cx={toPos.x}
          cy={toPos.y}
          r={endpointRadius}
          fill={isHovered ? "#4a90e2" : "#6b7280"}
          stroke="#ffffff"
          strokeWidth={2}
          style={{ cursor: 'grab' }}
          onMouseDown={(e) => handleEndpointMouseDown(e, false)}
        />
      </g>
    );
  };

  // Render dragging preview line
  const renderDraggingLine = () => {
    if (!draggingEndpoint) return null;

    const { connection, isSource, mousePos } = draggingEndpoint;
    const fixedPos = isSource
      ? getNodePosition(connection.to, false)
      : getNodePosition(connection.from, true);

    if (!fixedPos) return null;

    const dx = mousePos.x - fixedPos.x;
    const dy = mousePos.y - fixedPos.y;
    const curveOffset = Math.max(80, Math.abs(dx) * 0.4);
    const cp1x = fixedPos.x + (isSource ? 0 : curveOffset);
    const cp1y = fixedPos.y;
    const cp2x = mousePos.x - (isSource ? curveOffset : 0);
    const cp2y = mousePos.y;

    // Check if target is valid
    const allNodes = [USER_SOURCE, ...actions];
    const fixedNode = allNodes.find(n => n.id === (isSource ? connection.to : connection.from));
    const targetNode = dragTarget ? allNodes.find(n => n.id === dragTarget) : null;

    let isValid = false;
    if (targetNode && fixedNode && fixedNode.id !== targetNode.id) {
      const fixedType = fixedNode.type || "user";
      const targetType = targetNode.type || "equipment";

      if (isSource) {
        // Changing source - check if target can connect to fixed
        isValid = canConnect(targetType, fixedType);
      } else {
        // Changing target - check if fixed can connect to target
        isValid = canConnect(fixedType, targetType);
      }
    }

    return (
      <g>
        <path
          d={`M ${fixedPos.x} ${fixedPos.y} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${mousePos.x} ${mousePos.y} `}
          fill="none"
          stroke={isValid ? "#10b981" : "#ef4444"}
          strokeWidth={2.5}
          strokeDasharray="5,5"
          strokeLinecap="round"
        />
        {targetNode && (
          <circle
            cx={mousePos.x}
            cy={mousePos.y}
            r={8}
            fill={isValid ? "#10b981" : "#ef4444"}
            stroke="#ffffff"
            strokeWidth={2}
          />
        )}
      </g>
    );
  };

  return (
    <svg
      className="connection-lines-svg"
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
        overflow: 'visible'
      }}
    >
      {connections.map(renderConnection)}
      {renderDraggingLine()}
    </svg>
  );
}

function CanvasNodes({ actions, connections, connectingFrom, onConnectionStart, onConnectionDelete, onConnectionUpdate, nodePositions, onNodePositionChange, onRemoveAction, onUpdateAction, onOpenSettings, USER_SOURCE, userTriggerMode, onUserTriggerModeChange }) {
  const nodeRefs = useRef({});

  const { sensors, scenes, equipment } = useMemo(() => {
    // Filter actions in the order they appear in the actions array
    // This ensures the display order matches the JSON generation order
    const sensors = actions.filter((a) => a.type === "sensor");
    const scenes = actions.filter((a) => a.type === "scene");
    const equipment = actions.filter((a) => a.type === "equipment" || !a.type);
    return { sensors, scenes, equipment };
  }, [actions]);

  const setNodeRef = (nodeId, element) => {
    if (element) {
      nodeRefs.current[nodeId] = element;
    } else {
      delete nodeRefs.current[nodeId];
    }
  };

  // Helper function to get default position
  const getDefaultPosition = (nodeId, index, type) => {
    if (nodePositions[nodeId]) {
      return nodePositions[nodeId];
    }

    // Default layout: columns with more spacing to avoid overlap
    const columnSpacing = 350; // spacing between trigger / condition / equipment columns
    const rowSpacing = 200; // vertical spacing between nodes (avoid overlap)
    const startX = 100;
    const startY = 150;

    let x = startX;
    let y = startY;

    if (nodeId === USER_SOURCE.id) {
      x = startX;
      y = startY;
    } else if (type === "sensor") {
      x = startX + columnSpacing;
      const sensorIndex = sensors.findIndex(s => s.id === nodeId);
      y = startY + sensorIndex * rowSpacing;
    } else if (type === "scene") {
      x = startX + columnSpacing * 2;
      const sceneIndex = scenes.findIndex(s => s.id === nodeId);
      y = startY + sceneIndex * rowSpacing;
    } else if (type === "equipment" || !type) {
      x = startX + columnSpacing * 3;
      const eqIndex = equipment.findIndex(e => e.id === nodeId);
      y = startY + eqIndex * rowSpacing;
    }

    return { x, y };
  };

  if (!actions.length) {
    const defaultUserPos = getDefaultPosition(USER_SOURCE.id, 0, "user");
    return (
      <div className="canvas-node-sequence canvas-node-sequence-empty">
        <CanvasNode
          action={USER_SOURCE}
          isSelected={connectingFrom === USER_SOURCE.id}
          onConnectionClick={onConnectionStart}
          nodeRef={(el) => setNodeRef(USER_SOURCE.id, el)}
          position={defaultUserPos}
          onPositionChange={(newPos) => onNodePositionChange?.(USER_SOURCE.id, newPos)}
          onRemove={undefined}
        />
        <div className="canvas-placeholder">
          Drag components from the left sidebar to the canvas
        </div>
      </div>
    );
  }

  // Get all nodes with their positions
  const allNodes = [
    { ...USER_SOURCE, position: getDefaultPosition(USER_SOURCE.id, 0, "user") },
    ...actions.map((action, idx) => ({
      ...action,
      position: getDefaultPosition(action.id, idx, action.type)
    }))
  ];

  return (
    <div className="canvas-node-sequence">
      <ConnectionLines
        connections={connections}
        nodeRefs={nodeRefs}
        connectingFrom={connectingFrom}
        onConnectionDelete={onConnectionDelete}
        actions={actions}
        onConnectionUpdate={onConnectionUpdate}
        USER_SOURCE={USER_SOURCE}
      />
      {allNodes.map((node) => (
        <CanvasNode
          key={node.id}
          action={node}
          isSelected={connectingFrom === node.id || (node.id === USER_SOURCE.id && connectingFrom === "user-source")}
          onConnectionClick={onConnectionStart}
          nodeRef={(el) => setNodeRef(node.id, el)}
          position={node.position}
          onPositionChange={(newPos) => onNodePositionChange?.(node.id, newPos)}
          onRemove={node.id !== USER_SOURCE.id ? onRemoveAction : undefined}
          onUpdate={onUpdateAction}
          onOpenSettings={onOpenSettings}
          userTriggerMode={node.id === USER_SOURCE.id ? userTriggerMode : undefined}
          onUserTriggerModeChange={node.id === USER_SOURCE.id ? onUserTriggerModeChange : undefined}
        />
      ))}
    </div>
  );
}

function canConnect(fromType, toType) {
  if (fromType === "user" && toType === "sensor") return true;
  if (fromType === "sensor" && toType === "scene") return true;
  if (fromType === "scene" && toType === "equipment") return true;
  // Don't allow equipment to equipment connections - each equipment should connect from scene/sensor
  return false;
}

function CanvasNode({ action, isConnecting, isSelected, onConnectionClick, nodeRef, position, onPositionChange, onRemove, onUpdate, onOpenSettings, userTriggerMode, onUserTriggerModeChange }) {
  const nodeClass = action.type === "user" ? "canvas-node-user" :
    action.type === "sensor" ? "canvas-node-sensor" :
      action.type === "scene" ? "canvas-node-scene" :
        "canvas-node-equipment";

  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const nodeElementRef = useRef(null);

  const handleMouseDown = (e) => {
    if (e.button !== 0) return; // Only left mouse button

    // Don't start dragging if clicking on interactive elements
    if (e.target.tagName === 'INPUT' ||
      e.target.tagName === 'BUTTON' ||
      e.target.tagName === 'SELECT' ||
      e.target.closest('button') ||
      e.target.closest('input') ||
      e.target.closest('select')) {
      return;
    }

    setIsDragging(true);
    const rect = nodeElementRef.current?.getBoundingClientRect();
    if (rect) {
      setDragStart({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      });
    }
    e.preventDefault();
  };

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e) => {
      const container = nodeElementRef.current?.closest('.canvas-node-sequence');
      if (!container) return;

      const containerRect = container.getBoundingClientRect();
      const scrollLeft = container.scrollLeft || 0;
      const scrollTop = container.scrollTop || 0;

      const newX = e.clientX - containerRect.left - dragStart.x + scrollLeft;
      const newY = e.clientY - containerRect.top - dragStart.y + scrollTop;

      onPositionChange?.({ x: newX, y: newY });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragStart, onPositionChange]);

  const nodeStyle = {
    position: 'absolute',
    left: `${position?.x || 0} px`,
    top: `${position?.y || 0} px`,
    cursor: isDragging ? 'grabbing' : 'grab',
  };

  const getTypeLabel = () => {
    switch (action.type) {
      case "user": return "User";
      case "sensor": return "Sensor";
      case "scene": return "Scene";
      default: return "Equipment";
    }
  };

  return (
    <div
      ref={(el) => {
        nodeElementRef.current = el;
        if (nodeRef) nodeRef(el);
      }}
      className={`canvas - node ${nodeClass} ${isSelected ? "canvas-node-connecting" : ""} ${isDragging ? "canvas-node-dragging" : ""} `}
      style={nodeStyle}
      onMouseDown={handleMouseDown}
    >
      {action.type === "user" ? (
        <>
          <div className="canvas-node-header-start">
            <div className="start-trigger-icon">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M2 2L10 6L2 10V2Z" fill="currentColor" />
              </svg>
            </div>
            <div className="start-trigger-label">Start Trigger</div>
          </div>
          <div className="canvas-node-content">
            <div className="canvas-node-main-text">
              On Scene Activate
              <div className="canvas-node-connector-output-inline"></div>
            </div>
            <div className="canvas-node-mode-field">
              <span className="mode-label">Mode:</span>
              <select
                className="mode-select"
                value={userTriggerMode || "manual"}
                onChange={(e) => {
                  e.stopPropagation();
                  if (onUserTriggerModeChange) {
                    onUserTriggerModeChange(e.target.value);
                  }
                }}
                onClick={(e) => e.stopPropagation()}
                onMouseDown={(e) => e.stopPropagation()}
                onFocus={(e) => e.stopPropagation()}
              >
                <option value="manual">Manual</option>
                <option value="automatic">Automatic</option>
              </select>
            </div>
          </div>
        </>
      ) : (
        <>
          <div className={`canvas - node - header ${action.type === "sensor" ? "header-sensor" : action.type === "scene" ? "header-scene" : "header-equipment"} `}>
            <div className="canvas-node-header-icon">{action.icon ?? (action.type === "sensor" ? "🌡️" : action.type === "scene" ? "⏰" : "💡")}</div>
            <div className="canvas-node-header-title">{action.label}</div>
            {onRemove && action.type !== "user" && (
              <button
                className="canvas-node-close-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  onRemove(action.id);
                }}
              >
                ×
              </button>
            )}
          </div>
          <div className="canvas-node-content">
            <div className="canvas-node-status-section">
              <div className="canvas-node-status-label">
                {(() => {
                  if (action.type === "sensor") return "ENABLED";
                  if (action.type === "scene") return "ACTIVE";
                  return "POWER";
                })()}
              </div>
              <label className="canvas-node-toggle">
                <input
                  type="checkbox"
                  checked={action.isEnabled !== false}
                  onChange={(e) => {
                    e.stopPropagation();
                    if (onUpdate && action.id) {
                      onUpdate(action.id, { isEnabled: e.target.checked });
                    }
                  }}
                />
                <span className="canvas-node-toggle-slider"></span>
              </label>
            </div>
            <div className="canvas-node-action-info">
              <span className="canvas-node-action-text">
                {(() => {
                  if (action.type === "sensor") {
                    // Different status text based on sensor type
                    if (action.label === "Temperature Sensor" || action.label === "Temp") return "Monitor";
                    if (action.label === "Motion Sensor" || action.label === "Motion") return "Detecting";
                    if (action.label === "Sound Sensor" || action.label === "Sound") return "Listening";
                    return "Monitor";
                  }
                  if (action.type === "scene") {
                    // Display current value for scene
                    if (action.label === "Temperature Threshold" || action.label === "Temperature") {
                      return `${action.temperatureValue ?? 20}°C`;
                    }
                    if (action.label === "Time") {
                      if (action.timeType === "range") {
                        return `${action.timeStart ?? "00:00"} - ${action.timeEnd ?? "23:59"} `;
                      }
                      return action.timeValue ?? "17:00";
                    }
                    if (action.label === "Humidity Threshold" || action.label === "Humidity") {
                      return `${action.humidityValue ?? 60}% `;
                    }
                    return "Active";
                  }
                  // For equipment, show status based on isEnabled
                  // Default to "Turn On" if isEnabled is undefined or true
                  return (action.isEnabled !== false) ? "Turn On" : "Standby";
                })()}
              </span>
              {action.type === "scene" && (
                <button
                  className="canvas-node-gear-button"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onOpenSettings) {
                      onOpenSettings(action);
                    }
                  }}
                  title="Settings"
                >
                  <span className="canvas-node-gear-icon">⚙️</span>
                </button>
              )}
            </div>
            {action.type === "sensor" && (
              <div className="canvas-node-last-value">
                {(() => {
                  // Different last value based on sensor type
                  if (action.label === "Temperature Sensor" || action.label === "Temp") {
                    const tempValue = action.lastValue ?? 24;
                    return `Last value: ${tempValue}°C`;
                  }
                  if (action.label === "Motion Sensor" || action.label === "Motion") {
                    const motionValue = action.lastValue ?? "No motion";
                    return `Last value: ${motionValue} `;
                  }
                  if (action.label === "Sound Sensor" || action.label === "Sound") {
                    const soundValue = action.lastValue ?? 45;
                    return `Last value: ${soundValue} dB`;
                  }
                  return "Last value: --";
                })()}
              </div>
            )}
            <div className="canvas-node-connector-output-inline"></div>
          </div>
        </>
      )}
    </div>
  );
}

function SceneSettingsModal({ action, onUpdate, onClose }) {
  const [tempValue, setTempValue] = useState(action.temperatureValue ?? 20);
  const [timeType, setTimeType] = useState(action.timeType ?? "fixed");
  const [timeValue, setTimeValue] = useState(action.timeValue ?? "17:00");
  const [timeStart, setTimeStart] = useState(action.timeStart ?? "00:00");
  const [timeEnd, setTimeEnd] = useState(action.timeEnd ?? "23:59");
  const [humidityValue, setHumidityValue] = useState(action.humidityValue ?? 60);

  const handleSave = () => {
    const updates = {};

    if (action.label === "Temperature Threshold" || action.label === "Temperature") {
      updates.temperatureValue = tempValue;
    } else if (action.label === "Time") {
      updates.timeType = timeType;
      if (timeType === "fixed") {
        updates.timeValue = timeValue;
        updates.timeStart = undefined;
        updates.timeEnd = undefined;
      } else {
        updates.timeStart = timeStart;
        updates.timeEnd = timeEnd;
        updates.timeValue = undefined;
      }
    } else if (action.label === "Humidity Threshold" || action.label === "Humidity") {
      updates.humidityValue = humidityValue;
    }

    onUpdate?.(action.id, updates);
    onClose();
  };

  const minTemp = -15;
  const maxTemp = 45;
  const tempPercentage = ((tempValue - minTemp) / (maxTemp - minTemp)) * 100;
  const humidityPercentage = (humidityValue / 100) * 100;

  return (
    <div className="scene-settings-modal-overlay" onClick={onClose}>
      <div className="scene-settings-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="scene-settings-modal-header">
          <h3 className="scene-settings-modal-title">
            {action.icon} {action.label} Settings
          </h3>
          <button className="scene-settings-modal-close" onClick={onClose}>×</button>
        </div>
        <div className="scene-settings-modal-body">
          {(action.label === "Temperature Threshold" || action.label === "Temperature") && (
            <div className="scene-settings-group">
              <label className="scene-settings-label">Temperature: {tempValue}°C</label>
              <div className="slider-wrapper">
                <input
                  type="range"
                  min={minTemp}
                  max={maxTemp}
                  value={tempValue}
                  onChange={(e) => setTempValue(parseInt(e.target.value))}
                  className="temperature-slider"
                  style={{ '--value': `${tempPercentage}% ` }}
                />
              </div>
              <div className="scene-settings-range">
                <span>{minTemp}°C</span>
                <span>{maxTemp}°C</span>
              </div>
            </div>
          )}

          {action.label === "Time" && (
            <div className="scene-settings-group">
              <label className="scene-settings-label">Time Type</label>
              <div className="scene-settings-radio-group">
                <label className="scene-settings-radio">
                  <input
                    type="radio"
                    name="timeType"
                    value="fixed"
                    checked={timeType === "fixed"}
                    onChange={(e) => setTimeType(e.target.value)}
                  />
                  <span>Fixed Time Point</span>
                </label>
                <label className="scene-settings-radio">
                  <input
                    type="radio"
                    name="timeType"
                    value="range"
                    checked={timeType === "range"}
                    onChange={(e) => setTimeType(e.target.value)}
                  />
                  <span>Time Range</span>
                </label>
              </div>

              {timeType === "fixed" ? (
                <div className="scene-settings-time-input">
                  <label className="scene-settings-label">Time:</label>
                  <input
                    type="time"
                    value={timeValue}
                    onChange={(e) => setTimeValue(e.target.value)}
                    className="time-input"
                  />
                </div>
              ) : (
                <div className="scene-settings-time-range">
                  <div className="scene-settings-time-input">
                    <label className="scene-settings-label">Start Time:</label>
                    <input
                      type="time"
                      value={timeStart}
                      onChange={(e) => setTimeStart(e.target.value)}
                      className="time-input"
                    />
                  </div>
                  <div className="scene-settings-time-input">
                    <label className="scene-settings-label">End Time:</label>
                    <input
                      type="time"
                      value={timeEnd}
                      onChange={(e) => setTimeEnd(e.target.value)}
                      className="time-input"
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {(action.label === "Humidity Threshold" || action.label === "Humidity") && (
            <div className="scene-settings-group">
              <label className="scene-settings-label">Humidity: {humidityValue}%</label>
              <div className="slider-wrapper">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={humidityValue}
                  onChange={(e) => setHumidityValue(parseInt(e.target.value))}
                  className="humidity-slider"
                  style={{ '--value': `${humidityPercentage}% ` }}
                />
              </div>
              <div className="scene-settings-range">
                <span>0%</span>
                <span>100%</span>
              </div>
            </div>
          )}
        </div>
        <div className="scene-settings-modal-footer">
          <button className="scene-settings-button scene-settings-button-cancel" onClick={onClose}>
            Cancel
          </button>
          <button className="scene-settings-button scene-settings-button-save" onClick={handleSave}>
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

function SidebarModal({ sidebarSections, onItemDragStart, onItemDoubleClick, onAddItem, onClose }) {
  const modalRef = useRef(null);
  const overlayRef = useRef(null);
  const isDraggingRef = useRef(false);

  useEffect(() => {
    const handleDragOver = (e) => {
      // Check if dragging outside the modal
      if (isDraggingRef.current && modalRef.current && overlayRef.current) {
        const modalElement = modalRef.current;
        const x = e.clientX;
        const y = e.clientY;
        const rect = modalElement.getBoundingClientRect();

        // Check if mouse is outside modal bounds
        if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
          // Make overlay and modal non-interactive to allow drop on canvas
          if (overlayRef.current) {
            overlayRef.current.style.pointerEvents = 'none';
          }
          if (modalRef.current) {
            modalRef.current.style.pointerEvents = 'none';
            modalRef.current.style.opacity = '0.3';
          }
        } else {
          // Restore interactivity if back inside modal
          if (overlayRef.current) {
            overlayRef.current.style.pointerEvents = 'auto';
          }
          if (modalRef.current) {
            modalRef.current.style.pointerEvents = 'auto';
            modalRef.current.style.opacity = '1';
          }
        }
      }
    };

    const handleDragEnd = () => {
      isDraggingRef.current = false;
      // Restore modal visibility if drag ended without drop
      if (overlayRef.current) {
        overlayRef.current.style.pointerEvents = 'auto';
      }
      if (modalRef.current) {
        modalRef.current.style.pointerEvents = 'auto';
        modalRef.current.style.opacity = '1';
      }
    };

    document.addEventListener('dragover', handleDragOver);
    document.addEventListener('dragend', handleDragEnd);

    return () => {
      document.removeEventListener('dragover', handleDragOver);
      document.removeEventListener('dragend', handleDragEnd);
    };
  }, [onClose]);

  const handleItemDragStart = (e, item) => {
    isDraggingRef.current = true;
    onItemDragStart?.(e, item);
  };

  return (
    <div
      ref={overlayRef}
      className="sidebar-modal-overlay"
      onClick={onClose}
    >
      <div
        ref={modalRef}
        className="sidebar-modal-content"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sidebar-modal-header">
          <h3 className="sidebar-modal-title">Add Components</h3>
          <button className="sidebar-modal-close" onClick={onClose}>×</button>
        </div>
        <div className="sidebar-modal-body">
          <Sidebar
            onItemDragStart={handleItemDragStart}
            onItemDoubleClick={onItemDoubleClick}
            sidebarSections={sidebarSections}
            onAddItem={onAddItem}
          />
        </div>
      </div>
    </div>
  );
}

function ActionPanel({ actions, onUpdateAction, onRemoveAction }) {

  const groupedActions = useMemo(() => {
    const groups = {
      sensor: [],
      scene: [],
      equipment: [],
    };
    actions.forEach((action) => {
      const type = action.type || "equipment";
      if (groups[type]) {
        groups[type].push(action);
      }
    });
    return groups;
  }, [actions]);

  const hasAnyActions = actions.length > 0;

  return (
    <div className="action-panel">
      <h3 className="action-title">Action:</h3>
      {hasAnyActions ? (
        <>
          {groupedActions.sensor.length > 0 && (
            <div className="action-group">
              <h4 className="action-group-title action-group-title-sensor">Triggers</h4>
              {groupedActions.sensor.map((action) =>
                action.control === "slider" ? (
                  <SliderRow
                    key={action.id}
                    label={`${action.label}: `}
                    icon={action.icon}
                    compact={action.compact}
                    actionId={action.id}
                    action={action}
                    onUpdate={onUpdateAction}
                    onRemove={onRemoveAction}
                  />
                ) : (
                  <ToggleRow
                    key={action.id}
                    label={`${action.label}: `}
                    icon={action.icon}
                    actionId={action.id}
                    action={action}
                    onUpdate={onUpdateAction}
                    onRemove={onRemoveAction}
                  />
                )
              )}
            </div>
          )}
          {groupedActions.scene.length > 0 && (
            <div className="action-group">
              <h4 className="action-group-title action-group-title-scene">Conditions</h4>
              {groupedActions.scene.map((action) => (
                <SceneRow
                  key={action.id}
                  action={action}
                  onUpdate={onUpdateAction}
                  onRemove={onRemoveAction}
                />
              ))}
            </div>
          )}
          {groupedActions.equipment.length > 0 && (
            <div className="action-group">
              <h4 className="action-group-title action-group-title-equipment">Equipment List</h4>
              {groupedActions.equipment.map((action) =>
                action.control === "slider" ? (
                  <SliderRow
                    key={action.id}
                    label={`${action.label}: `}
                    icon={action.icon}
                    compact={action.compact}
                    actionId={action.id}
                    action={action}
                    onUpdate={onUpdateAction}
                    onRemove={onRemoveAction}
                  />
                ) : (
                  <ToggleRow
                    key={action.id}
                    label={`${action.label}: `}
                    icon={action.icon}
                    actionId={action.id}
                    action={action}
                    onUpdate={onUpdateAction}
                    onRemove={onRemoveAction}
                  />
                )
              )}
            </div>
          )}
        </>
      ) : (
        <div className="action-panel-empty">Drag components to the canvas.</div>
      )}
    </div>
  );
}

function Canvas({ actions, connections, connectingFrom, onDropItem, automationName, onAutomationNameChange, onUpdateAction, onRemoveAction, onConnectionStart, onConnectionDelete, onConnectionUpdate, nodePositions, onNodePositionChange, sidebarSections, onItemDragStart, onItemDoubleClick, onAddItem, USER_SOURCE, onExecuteWorkflow, userTriggerMode, onUserTriggerModeChange }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [showSidebarModal, setShowSidebarModal] = useState(false);
  const [sceneSettingsModal, setSceneSettingsModal] = useState(null);
  const [showActionPanel, setShowActionPanel] = useState(false);

  const handleDragOver = (event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "copy";
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragOver(false);

    const payload = event.dataTransfer.getData("application/json");
    if (payload) {
      try {
        const item = JSON.parse(payload);
        // Get drop position relative to canvas
        const canvasBoard = event.currentTarget.closest('.canvas-board');
        if (canvasBoard) {
          const rect = canvasBoard.getBoundingClientRect();
          const x = event.clientX - rect.left;
          const y = event.clientY - rect.top;
          // Add item first, then close modal
          onDropItem?.(item, { x, y });
        } else {
          onDropItem?.(item);
        }
        // Close sidebar modal after drop completes
        setTimeout(() => {
          setShowSidebarModal(false);
        }, 50);
      } catch (error) {
        console.error("Invalid drag payload", error);
        // Close modal even on error
        setShowSidebarModal(false);
      }
    } else {
      // No payload, just close modal
      setShowSidebarModal(false);
    }
  };

  const handleExecuteWorkflow = () => {
    onExecuteWorkflow?.();
  };

  return (
    <main className="canvas-wrapper">
      <div
        className={`canvas - board ${isDragOver ? "canvas-board-drag-over" : ""} `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="canvas-top-controls">
          <div className="canvas-title-input">
            <input
              type="text"
              placeholder="Enter automation name..."
              value={automationName}
              onChange={(e) => onAutomationNameChange(e.target.value)}
              className="automation-name-input"
            />
          </div>
          <button
            className="canvas-add-button"
            onClick={() => setShowSidebarModal(true)}
            title="Add components"
          >
            <span className="canvas-add-icon">+</span>
          </button>
          <button
            className="execute-workflow-button"
            onClick={handleExecuteWorkflow}
            title="Execute and save workflow"
          >
            Execute Workflow
          </button>
        </div>
        <div className="canvas-content-wrapper">
          <CanvasNodes
            actions={actions}
            connections={connections}
            connectingFrom={connectingFrom}
            onConnectionStart={onConnectionStart}
            onConnectionDelete={onConnectionDelete}
            onConnectionUpdate={onConnectionUpdate}
            nodePositions={nodePositions}
            onNodePositionChange={onNodePositionChange}
            onRemoveAction={onRemoveAction}
            onUpdateAction={onUpdateAction}
            onOpenSettings={(action) => setSceneSettingsModal(action)}
            USER_SOURCE={USER_SOURCE}
            userTriggerMode={userTriggerMode}
            onUserTriggerModeChange={onUserTriggerModeChange}
          />
        </div>
      </div>
      <div className="action-panel-wrapper">
        <button
          className="action-panel-toggle"
          onClick={() => setShowActionPanel(!showActionPanel)}
          title={showActionPanel ? "Hide Action Panel" : "Show Action Panel"}
        >
          <span className="action-panel-toggle-icon">{showActionPanel ? "→" : "←"}</span>
        </button>
        {showActionPanel && (
          <ActionPanel actions={actions} onUpdateAction={onUpdateAction} onRemoveAction={onRemoveAction} />
        )}
      </div>
      {showSidebarModal && (
        <SidebarModal
          sidebarSections={sidebarSections}
          onItemDragStart={onItemDragStart}
          onItemDoubleClick={onItemDoubleClick}
          onAddItem={onAddItem}
          onClose={() => setShowSidebarModal(false)}
        />
      )}
      {sceneSettingsModal && (
        <SceneSettingsModal
          action={sceneSettingsModal}
          onUpdate={onUpdateAction}
          onClose={() => setSceneSettingsModal(null)}
        />
      )}
    </main>
  );
}

function JsonPreviewModal({ json, onClose, onImport, isImportMode = false, validationError = null, onSaveScene }) {
  if (!json) return null;

  const handleDownload = () => {
    const jsonString = JSON.stringify(json, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    // Use automation name as filename, or default to "automation"
    const fileName = json.name
      ? `${json.name.replace(/\s+/g, "_")}.json`
      : `automation_${Date.now()}.json`;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleSaveScene = () => {
    if (onSaveScene) {
      onSaveScene(json);
      alert("Scene saved successfully!");
      onClose();
    }
  };

  return (
    <div className="json-modal-overlay" onClick={onClose}>
      <div className="json-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="json-modal-header">
          <h3>{isImportMode ? "Import JSON Preview" : "Automation JSON Preview"}</h3>
          <button className="json-modal-close" onClick={onClose}>×</button>
        </div>
        {validationError && (
          <div className="json-validation-error">
            <div className="validation-error-icon">⚠️</div>
            <div className="validation-error-message">{validationError}</div>
          </div>
        )}
        <div className="json-modal-body">
          <pre className="json-preview">{JSON.stringify(json, null, 2)}</pre>
        </div>
        <div className="json-modal-footer">
          {isImportMode ? (
            <>
              <button className="pill-button pill-button-primary" onClick={onImport}>
                Confirm Import
              </button>
              <button className="pill-button" onClick={onClose}>
                Cancel
              </button>
            </>
          ) : (
            <>
              {onSaveScene && (
                <button className="pill-button pill-button-primary" onClick={handleSaveScene}>
                  Save Scene
                </button>
              )}
              <button className="pill-button" onClick={handleDownload}>
                Download JSON
              </button>
              <button className="pill-button" onClick={() => {
                navigator.clipboard.writeText(JSON.stringify(json, null, 2));
                alert("JSON copied to clipboard!");
              }}>
                Copy JSON
              </button>
              <button className="pill-button" onClick={onClose}>
                Close
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function AlertModal({ message, onClose }) {
  if (!message) return null;

  return (
    <div className="alert-modal-overlay" onClick={onClose}>
      <div className="alert-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="alert-modal-header">
          <h3>⚠️ Warning</h3>
          <button className="alert-modal-close" onClick={onClose}>×</button>
        </div>
        <div className="alert-modal-body">
          <p>{message}</p>
        </div>
        <div className="alert-modal-footer">
          <button className="pill-button" onClick={onClose}>
            OK
          </button>
        </div>
      </div>
    </div>
  );
}

function ConfirmModal({ message, onConfirm, onCancel }) {
  if (!message) return null;

  return (
    <div className="alert-modal-overlay" onClick={onCancel}>
      <div className="alert-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="alert-modal-header">
          <h3>⚠️ Confirm</h3>
          <button className="alert-modal-close" onClick={onCancel}>×</button>
        </div>
        <div className="alert-modal-body">
          <p>{message}</p>
        </div>
        <div className="alert-modal-footer">
          <button className="pill-button" onClick={onCancel}>
            Cancel
          </button>
          <button className="pill-button pill-button-danger" onClick={onConfirm}>
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}

// LocalStorage helpers
const STORAGE_KEY = "smart-home-sidebar-sections";

const loadSidebarSections = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (error) {
    console.error("Failed to load sidebar sections from localStorage:", error);
  }
  return initialSidebarSections;
};

const saveSidebarSections = (sections) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sections));
  } catch (error) {
    console.error("Failed to save sidebar sections to localStorage:", error);
  }
};

export default function App() {
  const [currentPage, setCurrentPage] = useState("scenes"); // "scenes" or "editor"
  const [actions, setActions] = useState(defaultActions);
  const [nodePositions, setNodePositions] = useState({}); // Store node positions for free dragging
  const [connections, setConnections] = useState([]); // Store connections: [{from: actionId, to: actionId}]
  const [connectingFrom, setConnectingFrom] = useState(null); // Track which node is being connected from
  const [automationName, setAutomationName] = useState("");
  const [previewJson, setPreviewJson] = useState(null);
  const [importJson, setImportJson] = useState(null); // JSON to be imported
  const [alertMessage, setAlertMessage] = useState(null);
  const [sidebarSections, setSidebarSections] = useState(loadSidebarSections);
  const [editingItem, setEditingItem] = useState(null);
  const [addingItem, setAddingItem] = useState(null);
  const [confirmReset, setConfirmReset] = useState(false);
  const [lastActionCount, setLastActionCount] = useState(0);
  const [userTriggerMode, setUserTriggerMode] = useState("manual"); // "manual" or "automatic"
  const [deletedConnections, setDeletedConnections] = useState(new Set()); // Track manually deleted connections

  // Fetch devices from backend on startup
  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/devices/equipment');
        if (response.ok) {
          const devices = await response.json();
          if (devices.length > 0) {
            const fetchedEquipment = devices.filter(d => d.type === 'equipment');
            const fetchedSensors = devices.filter(d => d.type === 'sensor');

            setSidebarSections(prev => prev.map(section => {
              if (section.title === "Equipment List" && fetchedEquipment.length > 0) {
                return { ...section, items: fetchedEquipment };
              }
              if (section.title === "Triggers" && fetchedSensors.length > 0) {
                return { ...section, items: fetchedSensors };
              }
              return section;
            }));
          }
        }
      } catch (error) {
        console.error("Failed to sync devices from backend:", error);
      }
    };
    fetchDevices();
  }, []);

  // Auto-connect newly added actions
  useEffect(() => {
    // Only process if actions count increased (new action added)
    if (actions.length <= lastActionCount) {
      setLastActionCount(actions.length);
      return;
    }

    // Find the newly added action (the last one)
    const newAction = actions[actions.length - 1];
    if (!newAction) {
      setLastActionCount(actions.length);
      return;
    }

    const itemType = newAction.type ?? "equipment";

    // Find the appropriate source node to connect from
    let sourceId = null;

    if (itemType === "sensor") {
      // Sensor should connect from USER_SOURCE
      sourceId = USER_SOURCE.id;
    } else if (itemType === "scene") {
      // Scene should connect from ALL sensors (Home Assistant logic: conditions check all triggers)
      // For simplicity, connect to the first sensor, but the logic means "when any sensor triggers, check all conditions"
      const sensors = actions.filter(a => a.type === "sensor" && a.id !== newAction.id);
      if (sensors.length > 0) {
        // Connect to the first sensor (represents the trigger group)
        sourceId = sensors[0].id;
      }
    } else if (itemType === "equipment") {
      // Equipment should connect from the last scene (Home Assistant logic: actions execute after all conditions are met)
      // If multiple scenes exist, connect to the last one (represents "all conditions satisfied")
      const scenes = actions.filter(a => a.type === "scene" && a.id !== newAction.id);
      if (scenes.length > 0) {
        sourceId = scenes[scenes.length - 1].id;
      } else {
        // If no scene, connect from last sensor (fallback: direct trigger to action)
        // Don't connect equipment to equipment - each equipment should connect from scene/sensor
        const sensors = actions.filter(a => a.type === "sensor" && a.id !== newAction.id);
        if (sensors.length > 0) {
          sourceId = sensors[sensors.length - 1].id;
        }
      }
    }

    // Create connection if source is found and connection is valid
    if (sourceId) {
      const sourceAction = sourceId === USER_SOURCE.id ? USER_SOURCE : actions.find(a => a.id === sourceId);
      if (sourceAction && canConnect(sourceAction.type || "user", itemType)) {
        // Use functional update to check and create connection
        setConnections((prevConnections) => {
          // Check if connection already exists
          const connectionExists = prevConnections.some(
            conn => conn.from === sourceId && conn.to === newAction.id
          );

          if (!connectionExists) {
            return [
              ...prevConnections,
              { from: sourceId, to: newAction.id }
            ];
          }
          return prevConnections;
        });
      }
    }

    setLastActionCount(actions.length);
  }, [actions, lastActionCount]);

  const handleItemDragStart = useCallback((event, item) => {
    event.dataTransfer.setData("application/json", JSON.stringify(item));
    event.dataTransfer.effectAllowed = "copy";
  }, []);

  const handleDropItem = useCallback((item, dropPosition) => {
    const itemType = item.type ?? "equipment";

    // Check if it's a sensor or scene type
    if (itemType === "sensor" || itemType === "scene") {
      // Check if the same label already exists in actions
      const existingItem = actions.find(
        (action) => action.type === itemType && action.label === item.label
      );

      if (existingItem) {
        const typeName = itemType === "sensor" ? "Triggers" : "Conditions";
        setAlertMessage(
          `The element "${item.label}" from ${typeName} has already been added to the canvas.Each ${typeName} element can only be added once.`
        );
        return;
      }
    }

    // Create new action
    const newActionId = `action - ${Date.now()} -${Math.floor(Math.random() * 1000)} `;
    const newAction = {
      id: newActionId,
      label: item.label,
      icon: item.icon,
      type: itemType,
      control: "toggle",
      isEnabled: true, // Default to enabled for equipment
    };

    // Set default lastValue for sensors based on type
    if (itemType === "sensor") {
      if (item.label === "Temperature Sensor" || item.label === "Temp") {
        newAction.lastValue = 24; // Default temperature in Celsius
      } else if (item.label === "Motion Sensor" || item.label === "Motion") {
        newAction.lastValue = "No motion"; // Default motion state
      } else if (item.label === "Sound Sensor" || item.label === "Sound") {
        newAction.lastValue = 45; // Default sound level in dB
      }
    }

    // Set default values for scene types
    if (itemType === "scene") {
      if (item.label === "Time") {
        newAction.timeType = "fixed"; // Default to fixed time point
        newAction.timeValue = "17:00"; // Default time
      } else if (item.label === "Temperature Threshold" || item.label === "Temperature") {
        newAction.temperatureValue = 20; // Default temperature
      } else if (item.label === "Humidity Threshold" || item.label === "Humidity") {
        newAction.humidityValue = 60; // Default humidity
      }
    }

    // If drop position is provided, set it for the new node
    if (dropPosition) {
      setNodePositions(prev => ({
        ...prev,
        [newActionId]: {
          x: dropPosition.x - 70, // Center the node on drop position
          y: dropPosition.y - 40
        }
      }));
    }

    // Find the appropriate source node to connect from (before adding new action)
    let sourceId = null;

    if (itemType === "sensor") {
      // Sensor should connect from USER_SOURCE
      sourceId = USER_SOURCE.id;
    } else if (itemType === "scene") {
      // Scene should connect from the first sensor (Home Assistant logic: conditions check all triggers)
      // This represents "when any sensor triggers, check all conditions (scenes)"
      const sensors = actions.filter(a => a.type === "sensor");
      if (sensors.length > 0) {
        sourceId = sensors[0].id; // Connect to first sensor (represents the trigger group)
      }
    } else if (itemType === "equipment") {
      // Equipment should connect from the last scene, or last equipment if no scene
      const scenes = actions.filter(a => a.type === "scene");
      if (scenes.length > 0) {
        sourceId = scenes[scenes.length - 1].id;
      } else {
        // If no scene, connect from last sensor
        // Don't connect equipment to equipment - each equipment should connect from scene/sensor
        const sensors = actions.filter(a => a.type === "sensor");
        if (sensors.length > 0) {
          sourceId = sensors[sensors.length - 1].id;
        }
      }
    }

    // Add the new action (connection will be created automatically via useEffect)
    setActions((prev) => [...prev, newAction]);
  }, [actions]);

  const handleResetClick = useCallback(() => {
    setConfirmReset(true);
  }, []);

  const resetCanvas = useCallback(() => {
    setActions(defaultActions);
    setConnections([]);
    setConnectingFrom(null);
    setAutomationName("");
    setDeletedConnections(new Set()); // Clear deleted connections
    setSidebarSections(initialSidebarSections);
    saveSidebarSections(initialSidebarSections);
    setConfirmReset(false);
  }, []);

  const handleConnectionStart = useCallback((actionId) => {
    const fromId = connectingFrom === "user-source" ? USER_SOURCE.id : connectingFrom;
    const toId = actionId === "user-source" ? USER_SOURCE.id : actionId;

    if (fromId === toId) {
      // Cancel connection if clicking the same node
      setConnectingFrom(null);
    } else if (connectingFrom) {
      // Complete connection
      const fromAction = connectingFrom === USER_SOURCE.id ? USER_SOURCE : actions.find(a => a.id === connectingFrom);
      const toAction = actionId === USER_SOURCE.id ? USER_SOURCE : actions.find(a => a.id === actionId);

      if (!fromAction || !toAction) return;

      if (canConnect(fromAction.type || "user", toAction.type || "equipment")) {
        // Check if connection already exists
        const exists = connections.some(
          conn => conn.from === fromId && conn.to === toId
        );

        if (!exists) {
          setConnections(prev => [...prev, { from: fromId, to: toId }]);
        }
        setConnectingFrom(null);
      } else {
        setAlertMessage(`Cannot connect ${fromAction.type || "user"} to ${toAction.type || "equipment"} `);
        setConnectingFrom(null);
      }
    } else {
      // Start connection
      setConnectingFrom(actionId);
    }
  }, [connectingFrom, actions, connections]);

  const handleConnectionDelete = useCallback((fromId, toId) => {
    // Mark this connection as manually deleted
    setDeletedConnections(prev => new Set([...prev, `${fromId} -${toId} `]));
    // Remove the connection
    setConnections(prev => prev.filter(
      conn => !(conn.from === fromId && conn.to === toId)
    ));
  }, []);

  const handleConnectionUpdate = useCallback((oldConnection, newConnection) => {
    setConnections(prev => {
      // Remove old connection
      const filtered = prev.filter(
        conn => !(conn.from === oldConnection.from && conn.to === oldConnection.to)
      );

      // Check if new connection already exists
      const exists = filtered.some(
        conn => conn.from === newConnection.from && conn.to === newConnection.to
      );

      // Add new connection if it doesn't exist
      if (!exists) {
        return [...filtered, newConnection];
      }

      return filtered;
    });
  }, []);

  // Function to auto-repair connections based on node types
  const autoRepairConnections = useCallback((currentActions, currentConnections) => {
    const allNodes = [USER_SOURCE, ...currentActions];
    const sensors = currentActions.filter(a => a.type === "sensor");
    const scenes = currentActions.filter(a => a.type === "scene");
    const equipment = currentActions.filter(a => a.type === "equipment" || !a.type);

    const requiredConnections = [];

    // Helper function to check if connection was manually deleted
    const isDeleted = (fromId, toId) => {
      return deletedConnections.has(`${fromId} -${toId} `);
    };

    // 1. Connect all sensors from USER_SOURCE
    sensors.forEach(sensor => {
      const exists = currentConnections.some(
        conn => conn.from === USER_SOURCE.id && conn.to === sensor.id
      );
      if (!exists && !isDeleted(USER_SOURCE.id, sensor.id)) {
        requiredConnections.push({ from: USER_SOURCE.id, to: sensor.id });
      }
    });

    // 2. Connect scenes from sensors (connect each scene to first sensor, representing trigger group)
    if (sensors.length > 0 && scenes.length > 0) {
      const firstSensorId = sensors[0].id;
      scenes.forEach(scene => {
        const exists = currentConnections.some(
          conn => conn.from === firstSensorId && conn.to === scene.id
        );
        if (!exists && !isDeleted(firstSensorId, scene.id)) {
          requiredConnections.push({ from: firstSensorId, to: scene.id });
        }
      });
    }

    // 3. Connect equipment from scenes (connect each equipment to last scene, representing all conditions met)
    // Each equipment connects independently from the scene/sensor, not from other equipment
    if (scenes.length > 0 && equipment.length > 0) {
      const lastSceneId = scenes[scenes.length - 1].id;
      equipment.forEach((eq) => {
        const exists = currentConnections.some(
          conn => conn.from === lastSceneId && conn.to === eq.id
        );
        if (!exists && !isDeleted(lastSceneId, eq.id)) {
          requiredConnections.push({ from: lastSceneId, to: eq.id });
        }
      });
    } else if (sensors.length > 0 && equipment.length > 0) {
      // If no scenes, connect equipment directly from last sensor
      const lastSensorId = sensors[sensors.length - 1].id;
      equipment.forEach((eq) => {
        const exists = currentConnections.some(
          conn => conn.from === lastSensorId && conn.to === eq.id
        );
        if (!exists && !isDeleted(lastSensorId, eq.id)) {
          requiredConnections.push({ from: lastSensorId, to: eq.id });
        }
      });
    }

    // Add missing connections
    if (requiredConnections.length > 0) {
      setConnections(prev => {
        const newConnections = [...prev];
        requiredConnections.forEach(reqConn => {
          // Check if connection already exists before adding
          const exists = newConnections.some(
            conn => conn.from === reqConn.from && conn.to === reqConn.to
          );
          if (!exists) {
            // Validate connection before adding
            const fromNode = allNodes.find(n => n.id === reqConn.from);
            const toNode = allNodes.find(n => n.id === reqConn.to);
            if (fromNode && toNode && canConnect(fromNode.type || "user", toNode.type || "equipment")) {
              newConnections.push(reqConn);
            }
          }
        });
        return newConnections;
      });
    }
  }, [USER_SOURCE, deletedConnections]);

  const handleNodePositionChange = useCallback((nodeId, newPosition) => {
    setNodePositions(prev => ({
      ...prev,
      [nodeId]: newPosition
    }));
  }, []);

  // Auto-repair connections when actions change (debounced to avoid excessive updates during drag)
  useEffect(() => {
    // Debounce the repair to avoid excessive updates during drag operations
    const timeoutId = setTimeout(() => {
      autoRepairConnections(actions, connections);
    }, 300); // Wait 300ms after last change before repairing

    return () => clearTimeout(timeoutId);
  }, [actions, connections, autoRepairConnections]);

  const handleImportJson = useCallback(() => {
    // Create a file input element
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.style.display = 'none';

    input.onchange = (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const jsonContent = JSON.parse(event.target.result);

          // Show preview FIRST, before any validation
          setPreviewJson(jsonContent);
          setAlertMessage(null);

          // Store JSON for later validation (when user clicks Confirm Import)
          setImportJson({
            json: jsonContent,
            actions: [],
            validationError: null,
          });
        } catch (error) {
          console.error('Error parsing JSON:', error);
          setAlertMessage('Failed to parse JSON file: ' + error.message);
        }
      };

      reader.onerror = () => {
        setAlertMessage('Failed to read file');
      };

      reader.readAsText(file);
    };

    document.body.appendChild(input);
    input.click();
    document.body.removeChild(input);
  }, [sidebarSections]);

  const generateAutomationJson = useCallback(() => {
    // Filter actions to match canvas display order (preserve the order they were added)
    const sensors = actions.filter((a) => a.type === "sensor");
    const scenes = actions.filter((a) => a.type === "scene");
    const equipment = actions.filter((a) => a.type === "equipment" || !a.type);

    // Generate triggers from sensors (in the same order as displayed on canvas)
    const triggers = sensors.map((sensor) => ({
      type: "deviceState",
      deviceId: `sensor_${sensor.label.toLowerCase().replace(/\s+/g, "_")} _01`,
      capability: sensor.label.toLowerCase(),
      state: "detected",
    }));

    // Generate conditions from scenes (in the same order as displayed on canvas)
    const conditions = scenes.map((scene) => {
      if (scene.label === "Time") {
        if (scene.timeType === "range") {
          return {
            type: "time",
            after: scene.timeStart || "00:00",
            before: scene.timeEnd || "23:59",
          };
        } else {
          const timeValue = scene.timeValue || "17:00";
          return {
            type: "time",
            time: timeValue,
          };
        }
      } else if (scene.label === "Temperature Threshold" || scene.label === "Temperature") {
        const tempValue = scene.temperatureValue ?? 20;
        return {
          type: "deviceState",
          deviceId: `sensor_temp_01`,
          capability: "temperature",
          state: `>= ${tempValue} `,
        };
      } else if (scene.label === "Humidity Threshold" || scene.label === "Humidity") {
        const humidityValue = scene.humidityValue ?? 60;
        return {
          type: "deviceState",
          deviceId: `sensor_humidity_01`,
          capability: "humidity",
          state: `>= ${humidityValue} `,
        };
      }
      return {
        type: "deviceState",
        deviceId: `sensor_${scene.label.toLowerCase().replace(/\s+/g, "_")} _01`,
        capability: scene.label.toLowerCase(),
        state: "active",
      };
    });

    // Generate actions from equipment (in the same order as displayed on canvas)
    const actionsList = equipment.map((eq) => ({
      type: "deviceCommand",
      deviceId: `device_${eq.label.toLowerCase().replace(/\s+/g, "_")} _01`,
      capability: eq.label.toLowerCase().includes("light") || eq.label.toLowerCase().includes("lamp") || eq.label.toLowerCase().includes("ceiling")
        ? "onOff"
        : eq.label.toLowerCase().includes("conditioner")
          ? "temperature"
          : "onOff",
      value: eq.label.toLowerCase().includes("conditioner") ? 26 : true,
    }));

    const automationId = automationName
      ? `auto_${automationName.toLowerCase().replace(/\s+/g, "_")} `
      : `auto_${Date.now()} `;

    return {
      automationId,
      name: automationName || "Untitled Automation",
      description: `Automation with ${sensors.length} trigger(s), ${scenes.length} condition(s), and ${equipment.length} action(s)`,
      isEnabled: true,
      triggers: triggers,
      conditions: conditions,
      actions: actionsList,
    };
  }, [actions, automationName]);

  const handlePreviewJson = useCallback(() => {
    const json = generateAutomationJson();
    setPreviewJson(json);
  }, [generateAutomationJson]);

  const handleUpdateAction = useCallback((actionId, updates) => {
    setActions((prev) =>
      prev.map((action) =>
        action.id === actionId ? { ...action, ...updates } : action
      )
    );
  }, []);

  const handleRemoveAction = useCallback((actionId) => {
    setActions((prev) => prev.filter((action) => action.id !== actionId));
  }, []);

  const handleItemDoubleClick = useCallback((item, sectionTitle) => {
    // Only allow editing for Equipment List
    if (sectionTitle === "Equipment List") {
      setEditingItem({ item, sectionTitle });
    }
  }, []);

  const handleSaveItem = useCallback((updatedItem) => {
    setSidebarSections((prev) => {
      const updated = prev.map((section) => {
        if (section.title === editingItem.sectionTitle) {
          return {
            ...section,
            items: section.items.map((item) =>
              item.label === editingItem.item.label ? updatedItem : item
            ),
          };
        }
        return section;
      });
      saveSidebarSections(updated);
      return updated;
    });
    setEditingItem(null);
  }, [editingItem]);

  const handleDeleteItem = useCallback((itemToDelete) => {
    setSidebarSections((prev) => {
      const updated = prev.map((section) => {
        if (section.title === editingItem.sectionTitle) {
          return {
            ...section,
            items: section.items.filter((item) => item.label !== itemToDelete.label),
          };
        }
        return section;
      });
      saveSidebarSections(updated);
      return updated;
    });
    setEditingItem(null);
  }, [editingItem]);

  const handleAddItem = useCallback((sectionTitle) => {
    setAddingItem(sectionTitle);
  }, []);

  const handleSaveNewItem = useCallback((newItem) => {
    setSidebarSections((prev) => {
      const updated = prev.map((section) => {
        if (section.title === addingItem) {
          return {
            ...section,
            items: [...section.items, newItem],
          };
        }
        return section;
      });
      saveSidebarSections(updated);
      return updated;
    });
    setAddingItem(null);
  }, [addingItem]);

  // Restore actions from automation data to canvas
  const restoreActionsFromAutomation = useCallback((automation, sidebarSections) => {
    const importedActions = [];
    const importedConnections = [];
    const importedNodePositions = {};

    // Process triggers (sensors)
    if (Array.isArray(automation.triggers)) {
      automation.triggers.forEach((trigger, idx) => {
        if (trigger.type === 'deviceState' && trigger.deviceId) {
          const sensorNameFromId = trigger.deviceId
            .replace(/^sensor_/, '')
            .replace(/_01$/, '')
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');

          const sensorSection = sidebarSections.find(s => s.title === "Triggers");
          const capability = trigger.capability?.toLowerCase() || '';

          const sensorItem = sensorSection?.items.find(item => {
            const itemLabelLower = item.label.toLowerCase();
            const sensorNameLower = sensorNameFromId.toLowerCase();
            if (itemLabelLower === sensorNameLower) return true;
            if (itemLabelLower === capability) return true;
            if (itemLabelLower.includes(capability) || capability.includes(itemLabelLower)) return true;
            if ((itemLabelLower === 'temp' && (capability === 'temperature' || capability === 'temp')) ||
              (itemLabelLower === 'temperature' && capability === 'temp')) return true;
            // 特殊处理：temp传感器
            if (capability === 'temp' && itemLabelLower === 'temp') return true;
            return false;
          });

          if (sensorItem) {
            const actionId = `imported - sensor - ${idx} -${Date.now()} `;
            const sensorAction = {
              id: actionId,
              label: sensorItem.label,
              icon: sensorItem.icon,
              type: 'sensor',
              control: 'toggle',
            };

            // Set default lastValue based on sensor type
            if (sensorItem.label === "Temperature Sensor" || sensorItem.label === "Temp") {
              sensorAction.lastValue = 24;
            } else if (sensorItem.label === "Motion Sensor" || sensorItem.label === "Motion") {
              sensorAction.lastValue = "No motion";
            } else if (sensorItem.label === "Sound Sensor" || sensorItem.label === "Sound") {
              sensorAction.lastValue = 45;
            }

            importedActions.push(sensorAction);
          }
        }
      });
    }

    // Process conditions (scenes)
    if (Array.isArray(automation.conditions)) {
      automation.conditions.forEach((condition, idx) => {
        if (condition.type === 'time') {
          const sceneSection = sidebarSections.find(s => s.title === "Conditions");
          const timeItem = sceneSection?.items.find(item => item.label === "Time");

          if (timeItem) {
            const actionId = `imported - scene - time - ${idx} -${Date.now()} `;
            // Check if it's a time range (has both after and before) or fixed time
            if (condition.after && condition.before) {
              importedActions.push({
                id: actionId,
                label: 'Time',
                icon: timeItem.icon,
                type: 'scene',
                timeType: 'range',
                timeStart: condition.after,
                timeEnd: condition.before,
              });
            } else {
              importedActions.push({
                id: actionId,
                label: 'Time',
                icon: timeItem.icon,
                type: 'scene',
                timeType: 'fixed',
                timeValue: condition.time || condition.after || "17:00",
              });
            }
          }
        } else if (condition.type === 'deviceState' && condition.deviceId) {
          const capability = condition.capability?.toLowerCase();
          let sceneLabel = '';
          let sceneValue = null;

          if (capability === 'temperature') {
            sceneLabel = 'Temperature Threshold';
            const match = condition.state?.match(/>=?\s*(\d+)/);
            sceneValue = match ? parseInt(match[1]) : 20;
          } else if (capability === 'humidity') {
            sceneLabel = 'Humidity Threshold';
            const match = condition.state?.match(/>=?\s*(\d+)/);
            sceneValue = match ? parseInt(match[1]) : 60;
          }

          if (sceneLabel) {
            const sceneSection = sidebarSections.find(s => s.title === "Conditions");
            // Try to find item with new label first, then fallback to old label
            const sceneItem = sceneSection?.items.find(item =>
              item.label === sceneLabel ||
              (sceneLabel === 'Temperature Threshold' && item.label === 'Temperature') ||
              (sceneLabel === 'Humidity Threshold' && item.label === 'Humidity')
            ) || sceneSection?.items.find(item => item.label === sceneLabel);

            if (sceneItem) {
              const actionId = `imported - scene - ${sceneLabel.toLowerCase().replace(/\s+/g, '-')} -${idx} -${Date.now()} `;
              importedActions.push({
                id: actionId,
                label: sceneItem.label, // Use the actual item label from sidebar
                icon: sceneItem.icon,
                type: 'scene',
                ...(sceneItem.label === 'Temperature Threshold' || sceneItem.label === 'Temperature' ? { temperatureValue: sceneValue } : {}),
                ...(sceneItem.label === 'Humidity Threshold' || sceneItem.label === 'Humidity' ? { humidityValue: sceneValue } : {}),
              });
            }
          }
        }
      });
    }

    // Process actions (equipment)
    if (Array.isArray(automation.actions)) {
      automation.actions.forEach((action, idx) => {
        if (action.type === 'deviceCommand' && action.deviceId) {
          const equipmentNameFromId = action.deviceId
            .replace(/^device_/, '')
            .replace(/_01$/, '')
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');

          const equipmentSection = sidebarSections.find(s => s.title === "Equipment List");
          const capability = action.capability?.toLowerCase() || '';

          const equipmentItem = equipmentSection?.items.find(item => {
            const itemLabelLower = item.label.toLowerCase();
            const equipmentNameLower = equipmentNameFromId.toLowerCase();
            if (itemLabelLower === equipmentNameLower) return true;
            if (itemLabelLower.includes(equipmentNameLower) || equipmentNameLower.includes(itemLabelLower)) return true;
            if (capability === 'onoff' && (itemLabelLower.includes('light') || itemLabelLower.includes('lamp') || itemLabelLower.includes('ceiling'))) return true;
            if (capability === 'temperature' && itemLabelLower.includes('conditioner')) return true;
            return false;
          });

          if (equipmentItem) {
            const actionId = `imported - equipment - ${idx} -${Date.now()} `;
            importedActions.push({
              id: actionId,
              label: equipmentItem.label,
              icon: equipmentItem.icon,
              type: 'equipment',
              control: 'toggle',
            });
          }
        }
      });
    }

    // Build connections based on restored actions order
    // Logic: User -> Sensors -> Scenes -> Equipment
    const restoredConnections = [];
    const sensors = importedActions.filter(a => a.type === 'sensor');
    const scenes = importedActions.filter(a => a.type === 'scene');
    const equipment = importedActions.filter(a => a.type === 'equipment' || !a.type);

    // Connect all sensors from USER_SOURCE
    sensors.forEach(sensor => {
      restoredConnections.push({ from: USER_SOURCE.id, to: sensor.id });
    });

    // Connect scenes from sensors (connect each scene to first sensor, representing trigger group)
    if (sensors.length > 0 && scenes.length > 0) {
      const firstSensorId = sensors[0].id;
      scenes.forEach(scene => {
        restoredConnections.push({ from: firstSensorId, to: scene.id });
      });
    }

    // Connect equipment from scenes (connect each equipment to last scene, representing all conditions met)
    // Each equipment connects independently from the scene/sensor, not from other equipment
    if (scenes.length > 0 && equipment.length > 0) {
      const lastSceneId = scenes[scenes.length - 1].id;
      equipment.forEach((eq) => {
        restoredConnections.push({ from: lastSceneId, to: eq.id });
      });
    } else if (sensors.length > 0 && equipment.length > 0) {
      // If no scenes, connect equipment directly from last sensor
      const lastSensorId = sensors[sensors.length - 1].id;
      equipment.forEach((eq) => {
        restoredConnections.push({ from: lastSensorId, to: eq.id });
      });
    }

    // Set default node positions (spread them out more to avoid overlap)
    const startX = 100;
    const startY = 150;
    const columnSpacing = 350; // Increased horizontal spacing
    const rowSpacing = 200; // Increased vertical spacing to prevent overlap

    let currentX = startX;
    let currentY = startY;

    // Position sensors (Triggers) - first column
    sensors.forEach((sensor, idx) => {
      importedNodePositions[sensor.id] = {
        x: startX + columnSpacing,
        y: startY + idx * rowSpacing
      };
    });

    // Position scenes (Conditions) - second column
    if (sensors.length > 0) {
      currentX = startX + columnSpacing * 2;
      currentY = startY;
    } else {
      currentX = startX + columnSpacing;
      currentY = startY;
    }
    scenes.forEach((scene, idx) => {
      importedNodePositions[scene.id] = {
        x: currentX,
        y: currentY + idx * rowSpacing
      };
    });

    // Position equipment (Actions) - third column
    if (scenes.length > 0) {
      currentX = startX + columnSpacing * 3;
    } else if (sensors.length > 0) {
      currentX = startX + columnSpacing * 2;
    } else {
      currentX = startX + columnSpacing;
    }
    currentY = startY;
    equipment.forEach((eq, idx) => {
      importedNodePositions[eq.id] = {
        x: currentX,
        y: currentY + idx * rowSpacing
      };
    });

    return {
      actions: importedActions,
      connections: restoredConnections,
      nodePositions: importedNodePositions
    };
  }, [USER_SOURCE]);

  const handleSelectScene = useCallback((scene) => {
    // Load scene data to editor
    if (scene.automationData) {
      // If there is saved automation data, restore actions to canvas
      const automation = scene.automationData;
      setAutomationName(automation.name || scene.name);

      // Restore actions, connections, and node positions from automation data
      const restored = restoreActionsFromAutomation(automation, sidebarSections);
      setActions(restored.actions);
      setConnections(restored.connections);
      setNodePositions(restored.nodePositions);
      setConnectingFrom(null);
      // Clear deleted connections when loading a new scene
      setDeletedConnections(new Set());
    } else {
      setAutomationName(scene.name);
      setActions(defaultActions);
      setConnections([]);
      setNodePositions({});
      setConnectingFrom(null);
      // Clear deleted connections when creating a new scene
      setDeletedConnections(new Set());
    }
    // Switch to editor page
    setCurrentPage("editor");
  }, [sidebarSections, restoreActionsFromAutomation]);

  const handleCreateNewScene = useCallback(() => {
    // Reset editor state
    setActions(defaultActions);
    setConnections([]);
    setConnectingFrom(null);
    setAutomationName("");
    setDeletedConnections(new Set()); // Clear deleted connections
    // Switch to editor page
    setCurrentPage("editor");
  }, []);

  const handleSaveScene = useCallback((json) => {
    // Save scene to localStorage
    try {
      const scenes = loadScenesFromStorage();
      const sceneData = {
        id: json.automationId || `scene_${Date.now()} `,
        name: json.name || "Untitled Automation",
        description: json.description || `Automation with ${json.triggers?.length || 0} trigger(s), ${json.conditions?.length || 0} condition(s), and ${json.actions?.length || 0} action(s)`,
        icon: "🎯",
        isEnabled: json.isEnabled !== undefined ? json.isEnabled : true,
        triggerCount: json.triggers?.length || 0,
        conditionCount: json.conditions?.length || 0,
        actionCount: json.actions?.length || 0,
        nodeCount: (json.triggers?.length || 0) + (json.conditions?.length || 0) + (json.actions?.length || 0),
        activeCount: (json.actions?.length || 0),
        createdAt: new Date().toISOString(),
        automationData: json, // Save complete automation data
      };

      // Check if scene with same ID already exists
      const existingIndex = scenes.findIndex(s => s.id === sceneData.id);
      if (existingIndex >= 0) {
        // Update existing scene
        scenes[existingIndex] = { ...scenes[existingIndex], ...sceneData, updatedAt: new Date().toISOString() };
      } else {
        // Add new scene
        scenes.push(sceneData);
      }

      localStorage.setItem("smart-home-scenes", JSON.stringify(scenes));
    } catch (error) {
      console.error("Failed to save scene:", error);
      alert("Failed to save scene: " + error.message);
    }
  }, []);

  // Load scenes from localStorage function (for ScenesList use)
  const loadScenesFromStorage = () => {
    try {
      const saved = localStorage.getItem("smart-home-scenes");
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (error) {
      console.error("Failed to load scenes from localStorage:", error);
    }
    return [];
  };

  const handleBackToScenes = useCallback(() => {
    setCurrentPage("scenes");
  }, []);

  return (
    <div className="app">
      {currentPage === "scenes" ? (
        <ScenesList
          onSelectScene={handleSelectScene}
          onCreateNew={handleCreateNewScene}
          onViewDevices={() => setCurrentPage("devices")}
        />
      ) : currentPage === "devices" ? (
        <DeviceList onBack={() => setCurrentPage("scenes")} />
      ) : (
        <>
          <Header
            onReset={handleResetClick}
            onPreviewJson={handlePreviewJson}
            onImportJson={handleImportJson}
            onBackToScenes={handleBackToScenes}
          />
          <div className="body">
            <Canvas
              actions={actions}
              connections={connections}
              connectingFrom={connectingFrom}
              onDropItem={handleDropItem}
              automationName={automationName}
              onAutomationNameChange={setAutomationName}
              onUpdateAction={handleUpdateAction}
              onRemoveAction={handleRemoveAction}
              onConnectionStart={handleConnectionStart}
              onConnectionDelete={handleConnectionDelete}
              onConnectionUpdate={handleConnectionUpdate}
              nodePositions={nodePositions}
              onNodePositionChange={handleNodePositionChange}
              sidebarSections={sidebarSections}
              onItemDragStart={handleItemDragStart}
              onItemDoubleClick={handleItemDoubleClick}
              onAddItem={handleAddItem}
              USER_SOURCE={USER_SOURCE}
              userTriggerMode={userTriggerMode}
              onUserTriggerModeChange={setUserTriggerMode}
              onExecuteWorkflow={() => {
                const json = generateAutomationJson();
                handleSaveScene(json);
                setAlertMessage("Workflow executed and saved successfully!");
                setTimeout(() => setAlertMessage(null), 3000);
              }}
            />
          </div>
        </>
      )}
      {previewJson && (
        <JsonPreviewModal
          json={previewJson}
          onClose={() => {
            setPreviewJson(null);
            setImportJson(null);
          }}
          onSaveScene={handleSaveScene}
          onImport={importJson ? () => {
            // Validate and import when user clicks Confirm Import
            const jsonContent = importJson.json;
            let validationError = null;

            // Validate JSON structure
            if (!jsonContent || typeof jsonContent !== 'object') {
              validationError = 'Invalid JSON file format: Root must be an object';
            } else {
              // Validate required fields
              const requiredFields = ['automationId', 'name', 'triggers', 'conditions', 'actions'];
              const missingFields = requiredFields.filter(field => !(field in jsonContent));
              if (missingFields.length > 0) {
                validationError = `Invalid JSON format: Missing required fields: ${missingFields.join(', ')} `;
              } else {
                // Validate field types
                if (typeof jsonContent.automationId !== 'string') {
                  validationError = 'Invalid JSON format: automationId must be a string';
                } else if (typeof jsonContent.name !== 'string') {
                  validationError = 'Invalid JSON format: name must be a string';
                } else if (typeof jsonContent.isEnabled !== 'boolean') {
                  validationError = 'Invalid JSON format: isEnabled must be a boolean';
                } else if (!Array.isArray(jsonContent.triggers)) {
                  validationError = 'Invalid JSON format: triggers must be an array';
                } else if (!Array.isArray(jsonContent.conditions)) {
                  validationError = 'Invalid JSON format: conditions must be an array';
                } else if (!Array.isArray(jsonContent.actions)) {
                  validationError = 'Invalid JSON format: actions must be an array';
                } else {
                  // Validate triggers structure
                  for (let i = 0; i < jsonContent.triggers.length; i++) {
                    const trigger = jsonContent.triggers[i];
                    if (!trigger || typeof trigger !== 'object') {
                      validationError = `Invalid JSON format: triggers[${i}] must be an object`;
                      break;
                    }
                    if (trigger.type !== 'deviceState') {
                      validationError = `Invalid JSON format: triggers[${i}].type must be "deviceState"`;
                      break;
                    }
                    if (!trigger.deviceId || typeof trigger.deviceId !== 'string') {
                      validationError = `Invalid JSON format: triggers[${i}].deviceId must be a string`;
                      break;
                    }
                    if (!trigger.capability || typeof trigger.capability !== 'string') {
                      validationError = `Invalid JSON format: triggers[${i}].capability must be a string`;
                      break;
                    }
                    if (!trigger.state || typeof trigger.state !== 'string') {
                      validationError = `Invalid JSON format: triggers[${i}].state must be a string`;
                      break;
                    }
                  }

                  if (!validationError) {
                    // Validate conditions structure
                    for (let i = 0; i < jsonContent.conditions.length; i++) {
                      const condition = jsonContent.conditions[i];
                      if (!condition || typeof condition !== 'object') {
                        validationError = `Invalid JSON format: conditions[${i}] must be an object`;
                        break;
                      }
                      if (condition.type === 'time') {
                        if (!condition.time && !condition.after) {
                          validationError = `Invalid JSON format: conditions[${i}] must have "time" or "after" field`;
                          break;
                        }
                      } else if (condition.type === 'deviceState') {
                        if (!condition.deviceId || typeof condition.deviceId !== 'string') {
                          validationError = `Invalid JSON format: conditions[${i}].deviceId must be a string`;
                          break;
                        }
                        if (!condition.capability || typeof condition.capability !== 'string') {
                          validationError = `Invalid JSON format: conditions[${i}].capability must be a string`;
                          break;
                        }
                        if (!condition.state || typeof condition.state !== 'string') {
                          validationError = `Invalid JSON format: conditions[${i}].state must be a string`;
                          break;
                        }
                      } else {
                        validationError = `Invalid JSON format: conditions[${i}].type must be "time" or "deviceState"`;
                        break;
                      }
                    }
                  }

                  if (!validationError) {
                    // Validate actions structure
                    for (let i = 0; i < jsonContent.actions.length; i++) {
                      const action = jsonContent.actions[i];
                      if (!action || typeof action !== 'object') {
                        validationError = `Invalid JSON format: actions[${i}] must be an object`;
                        break;
                      }
                      if (action.type === 'deviceCommand') {
                        if (!action.deviceId || typeof action.deviceId !== 'string') {
                          validationError = `Invalid JSON format: actions[${i}].deviceId must be a string`;
                          break;
                        }
                        if (!action.capability || typeof action.capability !== 'string') {
                          validationError = `Invalid JSON format: actions[${i}].capability must be a string`;
                          break;
                        }
                        if (action.value === undefined) {
                          validationError = `Invalid JSON format: actions[${i}].value is required`;
                          break;
                        }
                      } else if (action.type === 'delay') {
                        if (!action.duration || typeof action.duration !== 'string') {
                          validationError = `Invalid JSON format: actions[${i}].duration must be a string`;
                          break;
                        }
                      } else {
                        validationError = `Invalid JSON format: actions[${i}].type must be "deviceCommand" or "delay"`;
                        break;
                      }
                    }
                  }
                }
              }
            }

            // If validation failed, show error
            if (validationError) {
              setAlertMessage(validationError);
              return;
            }

            // Validation passed, reconstruct actions from JSON
            const importedActions = [];
            const actionIdMap = new Map();

            // Process triggers (sensors)
            if (Array.isArray(jsonContent.triggers)) {
              jsonContent.triggers.forEach((trigger, idx) => {
                if (trigger.type === 'deviceState' && trigger.deviceId) {
                  const sensorNameFromId = trigger.deviceId
                    .replace(/^sensor_/, '')
                    .replace(/_01$/, '')
                    .split('_')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');

                  const sensorSection = sidebarSections.find(s => s.title === "Triggers");
                  const capability = trigger.capability?.toLowerCase() || '';

                  const sensorItem = sensorSection?.items.find(item => {
                    const itemLabelLower = item.label.toLowerCase();
                    const sensorNameLower = sensorNameFromId.toLowerCase();
                    if (itemLabelLower === sensorNameLower) return true;
                    if (itemLabelLower === capability) return true;
                    if (itemLabelLower.includes(capability) || capability.includes(itemLabelLower)) return true;
                    if ((itemLabelLower === 'temp' && capability === 'temperature') ||
                      (itemLabelLower === 'temperature' && capability === 'temp')) return true;
                    return false;
                  });

                  if (sensorItem) {
                    const actionId = `imported - sensor - ${idx} -${Date.now()} `;
                    actionIdMap.set(trigger.deviceId, actionId);
                    importedActions.push({
                      id: actionId,
                      label: sensorItem.label,
                      icon: sensorItem.icon,
                      type: 'sensor',
                      control: 'toggle',
                    });
                  }
                }
              });
            }

            // Process conditions (scenes)
            if (Array.isArray(jsonContent.conditions)) {
              jsonContent.conditions.forEach((condition, idx) => {
                if (condition.type === 'time') {
                  const sceneSection = sidebarSections.find(s => s.title === "Conditions");
                  const timeItem = sceneSection?.items.find(item => item.label === "Time");

                  if (timeItem) {
                    const actionId = `imported - scene - time - ${idx} -${Date.now()} `;
                    importedActions.push({
                      id: actionId,
                      label: 'Time',
                      icon: timeItem.icon,
                      type: 'scene',
                      timeValue: condition.time || condition.after || "17:00",
                    });
                  }
                } else if (condition.type === 'deviceState' && condition.deviceId) {
                  const capability = condition.capability?.toLowerCase();
                  let sceneLabel = '';
                  let sceneValue = null;

                  if (capability === 'temperature') {
                    sceneLabel = 'Temperature';
                    const match = condition.state?.match(/>=?\s*(\d+)/);
                    sceneValue = match ? parseInt(match[1]) : 20;
                  } else if (capability === 'humidity') {
                    sceneLabel = 'Humidity';
                    const match = condition.state?.match(/>=?\s*(\d+)/);
                    sceneValue = match ? parseInt(match[1]) : 60;
                  }

                  if (sceneLabel) {
                    const sceneSection = sidebarSections.find(s => s.title === "Conditions");
                    // Try to find item with new label first, then fallback to old label
                    const sceneItem = sceneSection?.items.find(item =>
                      item.label === sceneLabel ||
                      (sceneLabel === 'Temperature Threshold' && item.label === 'Temperature') ||
                      (sceneLabel === 'Humidity Threshold' && item.label === 'Humidity')
                    ) || sceneSection?.items.find(item => item.label === sceneLabel);

                    if (sceneItem) {
                      const actionId = `imported - scene - ${sceneLabel.toLowerCase().replace(/\s+/g, '-')} -${idx} -${Date.now()} `;
                      importedActions.push({
                        id: actionId,
                        label: sceneItem.label, // Use the actual item label from sidebar
                        icon: sceneItem.icon,
                        type: 'scene',
                        ...(sceneItem.label === 'Temperature Threshold' || sceneItem.label === 'Temperature' ? { temperatureValue: sceneValue } : {}),
                        ...(sceneItem.label === 'Humidity Threshold' || sceneItem.label === 'Humidity' ? { humidityValue: sceneValue } : {}),
                      });
                    }
                  }
                }
              });
            }

            // Process actions (equipment)
            if (Array.isArray(jsonContent.actions)) {
              jsonContent.actions.forEach((action, idx) => {
                if (action.type === 'deviceCommand' && action.deviceId) {
                  const equipmentNameFromId = action.deviceId
                    .replace(/^device_/, '')
                    .replace(/_01$/, '')
                    .split('_')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');

                  const equipmentSection = sidebarSections.find(s => s.title === "Equipment List");
                  const capability = action.capability?.toLowerCase() || '';

                  const equipmentItem = equipmentSection?.items.find(item => {
                    const itemLabelLower = item.label.toLowerCase();
                    const equipmentNameLower = equipmentNameFromId.toLowerCase();
                    if (itemLabelLower === equipmentNameLower) return true;
                    if (itemLabelLower.includes(equipmentNameLower) || equipmentNameLower.includes(itemLabelLower)) return true;
                    if (capability === 'onoff' && (itemLabelLower.includes('light') || itemLabelLower.includes('lamp') || itemLabelLower.includes('ceiling'))) return true;
                    if (capability === 'temperature' && itemLabelLower.includes('conditioner')) return true;
                    return false;
                  });

                  if (equipmentItem) {
                    const actionId = `imported - equipment - ${idx} -${Date.now()} `;
                    importedActions.push({
                      id: actionId,
                      label: equipmentItem.label,
                      icon: equipmentItem.icon,
                      type: 'equipment',
                      control: 'toggle',
                    });
                  }
                }
              });
            }

            // Execute the actual import
            setActions(importedActions);
            setConnections([]);
            setConnectingFrom(null);
            if (jsonContent.name) {
              setAutomationName(jsonContent.name);
            }
            setAlertMessage(`Successfully imported automation: ${jsonContent.name || 'Untitled'} `);
            setPreviewJson(null);
            setImportJson(null);
          } : undefined}
          isImportMode={!!importJson}
          validationError={null}
        />
      )}
      {alertMessage && (
        <AlertModal
          message={alertMessage}
          onClose={() => setAlertMessage(null)}
        />
      )}
      {editingItem && (
        <EditItemModal
          item={editingItem.item}
          sectionTitle={editingItem.sectionTitle}
          onClose={() => setEditingItem(null)}
          onSave={handleSaveItem}
          onDelete={handleDeleteItem}
        />
      )}
      {addingItem && (
        <AddItemModal
          sectionTitle={addingItem}
          onClose={() => setAddingItem(null)}
          onSave={handleSaveNewItem}
        />
      )}
      {confirmReset && (
        <ConfirmModal
          message="Are you sure you want to reset the canvas? This will clear all actions and reset sidebar sections to default. This action cannot be undone."
          onConfirm={resetCanvas}
          onCancel={() => setConfirmReset(false)}
        />
      )}
    </div>
  );
}
