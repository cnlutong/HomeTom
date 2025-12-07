import React, { useCallback, useMemo, useState, useEffect, useRef } from "react";

const USER_SOURCE = {
  id: "user-source",
  label: "Residents",
  icon: "👥",
  type: "user",
};

const initialSidebarSections = [
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
  {
    title: "Sensor List",
    items: [
      { icon: "📡", label: "Motion", type: "sensor" },
      { icon: "📶", label: "Sound", type: "sensor" },
      { icon: "🌡️", label: "Temp", type: "sensor" },
    ],
  },
  {
    title: "Scene parameters",
    items: [
      { icon: "⏰", label: "Time", type: "scene" },
      { icon: "🌡️", label: "Temperature", type: "scene" },
      { icon: "💧", label: "Humidity", type: "scene" },
    ],
  },
];

const defaultActions = [];

function Header({ onReset, onPreviewJson, onImportJson }) {
  return (
    <header className="header">
      <div className="header-title">Smart Home Demo Lab</div>
      <div className="header-buttons">
        <button className="pill-button pill-button-primary" onClick={onPreviewJson}>
          Running automated scenarios
        </button>
        <button className="pill-button pill-button-purple" onClick={onImportJson}>
          Import automated Json
        </button>
        <button className="pill-button pill-button-danger" onClick={onReset}>
          Reset canvas
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
  const isSensorList = title === "Sensor List";
  const isSceneParameters = title === "Scene parameters";
  const isScrollable = isEquipmentList || isSensorList || isSceneParameters;
  const showAddButton = isEquipmentList || isSensorList || isSceneParameters;

  const getAddButtonTitle = () => {
    if (isEquipmentList) return "Add new equipment";
    if (isSensorList) return "Add new sensor";
    if (isSceneParameters) return "Add new scene parameter";
    return "Add new item";
  };

  const getTitleClassName = () => {
    if (isEquipmentList) return "sidebar-title sidebar-title-equipment";
    if (isSensorList) return "sidebar-title sidebar-title-sensor";
    if (isSceneParameters) return "sidebar-title sidebar-title-scene";
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
      <div className={`sidebar-items ${isScrollable ? "sidebar-items-scrollable" : ""}`}>
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
    if (window.confirm(`Are you sure you want to delete "${item.label}"?`)) {
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
    if (sectionTitle === "Sensor List") return "sensor";
    if (sectionTitle === "Scene parameters") return "scene";
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

function ToggleRow({ label, icon, actionId, onRemove }) {
  const handleToggleClick = () => {
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
      <div className="toggle-switch" onClick={handleToggleClick} style={{ cursor: 'pointer' }}>
        <div className="toggle-knob" />
      </div>
    </div>
  );
}

function SliderRow({ label, compact, icon, actionId, onRemove }) {
  const handleSliderClick = () => {
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
      <div 
        className={compact ? "slider slider-compact" : "slider"} 
        onClick={handleSliderClick}
        style={{ cursor: 'pointer' }}
      />
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
              style={{ '--value': `${percentage}%` }}
            />
          </div>
          <span className="scene-value">{value}°C</span>
        </div>
      </div>
    );
  }

  if (action.label === "Humidity") {
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
              style={{ '--value': `${percentage}%` }}
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
      label={`${action.label}:`}
      icon={action.icon}
    />
  );
}

function CanvasNodes({ actions, connections, connectingFrom, onConnectionStart, onConnectionDelete }) {
  const { sensors, scenes, equipment } = useMemo(() => {
    // Filter actions in the order they appear in the actions array
    // This ensures the display order matches the JSON generation order
    const sensors = actions.filter((a) => a.type === "sensor");
    const scenes = actions.filter((a) => a.type === "scene");
    const equipment = actions.filter((a) => a.type === "equipment" || !a.type);
    return { sensors, scenes, equipment };
  }, [actions]);

  // Get all nodes including USER_SOURCE
  const allNodes = [USER_SOURCE, ...actions];
  
  if (!actions.length) {
    return (
      <div className="canvas-node-sequence canvas-node-sequence-empty">
        <div className="canvas-node-row">
          <CanvasNode 
            action={USER_SOURCE} 
            isSelected={connectingFrom === USER_SOURCE.id}
            onConnectionClick={onConnectionStart}
          />
        </div>
        <div className="canvas-placeholder">
          Drag the component to the Action on the right, 
          and you can then view the selected component here.
        </div>
      </div>
    );
  }

  const rows = [];
  
  // Row 1: User node
  rows.push(
    <div key="row-user" className="canvas-node-row">
      <CanvasNode 
        key={USER_SOURCE.id} 
        action={USER_SOURCE}
        isSelected={connectingFrom === USER_SOURCE.id || connectingFrom === "user-source"}
        onConnectionClick={onConnectionStart}
      />
    </div>
  );
  
  // Row 2: Sensors (all in one row)
  if (sensors.length > 0) {
    const sensorRow = [];
    sensorRow.push(
      <div key="connector-user-to-sensor" className="canvas-connector-vertical" />
    );
    sensorRow.push(
      <div key="sensor-group" className="canvas-node-group">
        {sensors.map((sensor, idx) => (
          <React.Fragment key={sensor.id}>
            <CanvasNode 
              action={sensor}
              isSelected={connectingFrom === sensor.id}
              onConnectionClick={onConnectionStart}
            />
            {idx < sensors.length - 1 && (
              <div key={`${sensor.id}-connector`} className="canvas-connector-line" />
            )}
          </React.Fragment>
        ))}
      </div>
    );
    rows.push(<div key="row-sensors" className="canvas-node-row">{sensorRow}</div>);
  }
  
  // Row 3: Scenes (all in one row)
  if (scenes.length > 0) {
    const sceneRow = [];
    sceneRow.push(
      <div key="connector-to-scene" className="canvas-connector-vertical" />
    );
    sceneRow.push(
      <div key="scene-group" className="canvas-node-group">
        {scenes.map((scene, idx) => (
          <React.Fragment key={scene.id}>
            <CanvasNode 
              action={scene}
              isSelected={connectingFrom === scene.id}
              onConnectionClick={onConnectionStart}
            />
            {idx < scenes.length - 1 && (
              <div key={`${scene.id}-connector`} className="canvas-connector-line" />
            )}
          </React.Fragment>
        ))}
      </div>
    );
    rows.push(<div key="row-scenes" className="canvas-node-row">{sceneRow}</div>);
  }
  
  // Row 4: Equipment (all in one row, as peers)
  if (equipment.length > 0) {
    const equipmentRow = [];
    equipmentRow.push(
      <div key="connector-to-equipment" className="canvas-connector-vertical" />
    );
    equipmentRow.push(
      <div key="equipment-group" className="canvas-node-group">
        {equipment.map((eq) => (
          <CanvasNode 
            key={eq.id} 
            action={eq}
            isSelected={connectingFrom === eq.id}
            onConnectionClick={onConnectionStart}
          />
        ))}
      </div>
    );
    rows.push(<div key="row-equipment" className="canvas-node-row">{equipmentRow}</div>);
  }

  // Render custom connections based on connections array
  // For now, we'll use simple vertical connectors between rows
  // The actual line drawing will be handled by CSS or a more sophisticated system

  return (
    <div className="canvas-node-sequence">
      {rows}
    </div>
  );
}

function canConnect(fromType, toType) {
  if (fromType === "user" && toType === "sensor") return true;
  if (fromType === "sensor" && toType === "scene") return true;
  if (fromType === "scene" && toType === "equipment") return true;
  // Allow equipment to equipment connections
  if (fromType === "equipment" && toType === "equipment") return true;
  return false;
}

function CanvasNode({ action, isConnecting, isSelected, onConnectionClick }) {
  const nodeClass = action.type === "user" ? "canvas-node-user" :
                    action.type === "sensor" ? "canvas-node-sensor" :
                    action.type === "scene" ? "canvas-node-scene" :
                    "canvas-node-equipment";
  
  const handleOutputClick = (e) => {
    e.stopPropagation();
    onConnectionClick?.(action.id);
  };

  return (
    <div className={`canvas-node ${nodeClass} ${isSelected ? "canvas-node-connecting" : ""}`}>
      <div className="canvas-node-connector canvas-node-connector-output" onClick={handleOutputClick} title="Click to connect">
        <div className={`connector-dot ${isSelected ? "connector-dot-active" : ""}`} />
      </div>
      {action.type === "user" ? (
        <>
          <div className="canvas-node-icon">{action.icon}</div>
          <div className="canvas-node-label">{action.label}</div>
        </>
      ) : action.type === "sensor" ? (
        <>
          <div className="canvas-node-icon">{action.icon ?? "📡"}</div>
          <div className="canvas-node-label">{action.label}</div>
        </>
      ) : action.type === "scene" ? (
        <>
          <div className="canvas-scene-icon">{action.icon ?? "⏰"}</div>
          <div className="canvas-scene-label">{action.label}</div>
        </>
      ) : (
        <>
          <div className="canvas-node-icon">{action.icon ?? "🔘"}</div>
          <div className="canvas-node-label">{action.label}</div>
        </>
      )}
      {action.type !== "user" && (
        <div className="canvas-node-connector canvas-node-connector-input" onClick={handleOutputClick} title="Click to connect">
          <div className="connector-dot" />
        </div>
      )}
    </div>
  );
}

function ActionPanel({ actions, onDropItem, onUpdateAction, onRemoveAction }) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "copy";
    setIsDragOver(true);
  };

  const handleDragLeave = () => setIsDragOver(false);

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragOver(false);
    const payload = event.dataTransfer.getData("application/json");
    if (payload) {
      try {
        const item = JSON.parse(payload);
        onDropItem?.(item);
      } catch (error) {
        console.error("Invalid drag payload", error);
      }
    }
  };

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
    <div
      className={`action-panel ${isDragOver ? "action-panel-drop" : ""}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <h3 className="action-title">Action:</h3>
      {hasAnyActions ? (
        <>
          {groupedActions.sensor.length > 0 && (
            <div className="action-group">
              <h4 className="action-group-title action-group-title-sensor">Sensor List</h4>
              {groupedActions.sensor.map((action) =>
                action.control === "slider" ? (
                  <SliderRow
                    key={action.id}
                    label={`${action.label}:`}
                    icon={action.icon}
                    compact={action.compact}
                    actionId={action.id}
                    onRemove={onRemoveAction}
                  />
                ) : (
                  <ToggleRow
                    key={action.id}
                    label={`${action.label}:`}
                    icon={action.icon}
                    actionId={action.id}
                    onRemove={onRemoveAction}
                  />
                )
              )}
            </div>
          )}
          {groupedActions.scene.length > 0 && (
            <div className="action-group">
              <h4 className="action-group-title action-group-title-scene">Scene parameters</h4>
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
                    label={`${action.label}:`}
                    icon={action.icon}
                    compact={action.compact}
                    actionId={action.id}
                    onRemove={onRemoveAction}
                  />
                ) : (
                  <ToggleRow
                    key={action.id}
                    label={`${action.label}:`}
                    icon={action.icon}
                    actionId={action.id}
                    onRemove={onRemoveAction}
                  />
                )
              )}
            </div>
          )}
        </>
      ) : (
        <div className="action-panel-empty">Drag the left component here.</div>
      )}
    </div>
  );
}

function Canvas({ actions, connections, connectingFrom, onDropItem, automationName, onAutomationNameChange, onUpdateAction, onRemoveAction, onConnectionStart, onConnectionDelete }) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);

  const handleWheel = useCallback((e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    const newZoom = Math.max(0.5, Math.min(2, zoom + delta));
    setZoom(newZoom);
  }, [zoom]);

  const handleMouseDown = useCallback((e) => {
    if (e.button === 1 || (e.button === 0 && e.ctrlKey) || (e.button === 0 && e.metaKey)) {
      e.preventDefault();
      setIsPanning(true);
      setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  }, [pan]);

  const handleMouseMove = useCallback((e) => {
    if (isPanning) {
      setPan({
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y,
      });
    }
  }, [isPanning, panStart]);

  const handleMouseUp = useCallback(() => {
    setIsPanning(false);
  }, []);

  const handleZoomIn = useCallback(() => {
    setZoom(prev => Math.min(2, prev + 0.1));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom(prev => Math.max(0.5, prev - 0.1));
  }, []);

  const handleZoomReset = useCallback(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, []);

  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      canvas.addEventListener('wheel', handleWheel, { passive: false });
      return () => canvas.removeEventListener('wheel', handleWheel);
    }
  }, [handleWheel]);

  return (
    <main className="canvas-wrapper">
      <div className="canvas-board" ref={canvasRef}>
        <div className="canvas-zoom-controls">
          <button className="zoom-button" onClick={handleZoomOut} title="Zoom Out">−</button>
          <span className="zoom-level">{Math.round(zoom * 100)}%</span>
          <button className="zoom-button" onClick={handleZoomIn} title="Zoom In">+</button>
          <button className="zoom-button zoom-reset" onClick={handleZoomReset} title="Reset Zoom">⌂</button>
        </div>
        <div className="canvas-title-input">
          <input
            type="text"
            placeholder="Enter automation name..."
            value={automationName}
            onChange={(e) => onAutomationNameChange(e.target.value)}
            className="automation-name-input"
          />
        </div>
        <div 
          className="canvas-content-wrapper"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'top left',
          }}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <CanvasNodes 
            actions={actions} 
            connections={connections}
            connectingFrom={connectingFrom}
            onConnectionStart={onConnectionStart}
            onConnectionDelete={onConnectionDelete}
          />
        </div>
        <ActionPanel actions={actions} onDropItem={onDropItem} onUpdateAction={onUpdateAction} onRemoveAction={onRemoveAction} />
      </div>
    </main>
  );
}

function JsonPreviewModal({ json, onClose, onImport, isImportMode = false, validationError = null }) {
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
  const [actions, setActions] = useState(defaultActions);
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

  const handleItemDragStart = useCallback((event, item) => {
    event.dataTransfer.setData("application/json", JSON.stringify(item));
    event.dataTransfer.effectAllowed = "copy";
  }, []);

  const handleDropItem = useCallback((item) => {
    const itemType = item.type ?? "equipment";
    
    // Check if it's a sensor or scene type
    if (itemType === "sensor" || itemType === "scene") {
      // Check if the same label already exists in actions
      const existingItem = actions.find(
        (action) => action.type === itemType && action.label === item.label
      );
      
      if (existingItem) {
        const typeName = itemType === "sensor" ? "Sensor List" : "Scene parameters";
        setAlertMessage(
          `The element "${item.label}" from ${typeName} has already been added to the canvas. Each ${typeName} element can only be added once.`
        );
        return;
      }
    }
    
    // Allow adding equipment multiple times, or new sensor/scene
    setActions((prev) => [
      ...prev,
      {
        id: `action-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
        label: item.label,
        icon: item.icon,
        type: itemType,
        control: "toggle",
      },
    ]);
  }, [actions]);

  const handleResetClick = useCallback(() => {
    setConfirmReset(true);
  }, []);

  const resetCanvas = useCallback(() => {
    setActions(defaultActions);
    setConnections([]);
    setConnectingFrom(null);
    setAutomationName("");
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
        setAlertMessage(`Cannot connect ${fromAction.type || "user"} to ${toAction.type || "equipment"}`);
        setConnectingFrom(null);
      }
    } else {
      // Start connection
      setConnectingFrom(actionId);
    }
  }, [connectingFrom, actions, connections]);

  const handleConnectionDelete = useCallback((fromId, toId) => {
    setConnections(prev => prev.filter(
      conn => !(conn.from === fromId && conn.to === toId)
    ));
  }, []);

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
      deviceId: `sensor_${sensor.label.toLowerCase().replace(/\s+/g, "_")}_01`,
      capability: sensor.label.toLowerCase(),
      state: "detected",
    }));

    // Generate conditions from scenes (in the same order as displayed on canvas)
    const conditions = scenes.map((scene) => {
      if (scene.label === "Time") {
        const timeValue = scene.timeValue || "17:00";
        return {
          type: "time",
          time: timeValue,
        };
      } else if (scene.label === "Temperature") {
        const tempValue = scene.temperatureValue ?? 20;
        return {
          type: "deviceState",
          deviceId: `sensor_temp_01`,
          capability: "temperature",
          state: `>= ${tempValue}`,
        };
      } else if (scene.label === "Humidity") {
        const humidityValue = scene.humidityValue ?? 60;
        return {
          type: "deviceState",
          deviceId: `sensor_humidity_01`,
          capability: "humidity",
          state: `>= ${humidityValue}`,
        };
      }
      return {
        type: "deviceState",
        deviceId: `sensor_${scene.label.toLowerCase().replace(/\s+/g, "_")}_01`,
        capability: scene.label.toLowerCase(),
        state: "active",
      };
    });

    // Generate actions from equipment (in the same order as displayed on canvas)
    const actionsList = equipment.map((eq) => ({
      type: "deviceCommand",
      deviceId: `device_${eq.label.toLowerCase().replace(/\s+/g, "_")}_01`,
      capability: eq.label.toLowerCase().includes("light") || eq.label.toLowerCase().includes("lamp") || eq.label.toLowerCase().includes("ceiling")
        ? "onOff"
        : eq.label.toLowerCase().includes("conditioner")
        ? "temperature"
        : "onOff",
      value: eq.label.toLowerCase().includes("conditioner") ? 26 : true,
    }));

    const automationId = automationName
      ? `auto_${automationName.toLowerCase().replace(/\s+/g, "_")}`
      : `auto_${Date.now()}`;

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

  return (
    <div className="app">
      <Header onReset={handleResetClick} onPreviewJson={handlePreviewJson} onImportJson={handleImportJson} />
      <div className="body">
        <Sidebar
          onItemDragStart={handleItemDragStart}
          onItemDoubleClick={handleItemDoubleClick}
          sidebarSections={sidebarSections}
          onAddItem={handleAddItem}
        />
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
        />
      </div>
      {previewJson && (
        <JsonPreviewModal
          json={previewJson}
          onClose={() => {
            setPreviewJson(null);
            setImportJson(null);
          }}
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
                validationError = `Invalid JSON format: Missing required fields: ${missingFields.join(', ')}`;
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
                  
                  const sensorSection = sidebarSections.find(s => s.title === "Sensor List");
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
                    const actionId = `imported-sensor-${idx}-${Date.now()}`;
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
                  const sceneSection = sidebarSections.find(s => s.title === "Scene parameters");
                  const timeItem = sceneSection?.items.find(item => item.label === "Time");
                  
                  if (timeItem) {
                    const actionId = `imported-scene-time-${idx}-${Date.now()}`;
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
                    const sceneSection = sidebarSections.find(s => s.title === "Scene parameters");
                    const sceneItem = sceneSection?.items.find(item => item.label === sceneLabel);
                    
                    if (sceneItem) {
                      const actionId = `imported-scene-${sceneLabel.toLowerCase()}-${idx}-${Date.now()}`;
                      importedActions.push({
                        id: actionId,
                        label: sceneLabel,
                        icon: sceneItem.icon,
                        type: 'scene',
                        ...(sceneLabel === 'Temperature' ? { temperatureValue: sceneValue } : {}),
                        ...(sceneLabel === 'Humidity' ? { humidityValue: sceneValue } : {}),
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
                    const actionId = `imported-equipment-${idx}-${Date.now()}`;
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
            setAlertMessage(`Successfully imported automation: ${jsonContent.name || 'Untitled'}`);
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
