import React, { useState, useEffect } from 'react';
import { useDataFetch } from './hooks/useDataFetch';
import { InteractivePlayer } from './components/InteractivePlayer';
import './App.css';

export function TooltipMarker({ text }) {
  return (
    <span className="tooltip-icon" data-tooltip={text} tabIndex={0} aria-label={text}>
      ?
    </span>
  );
}

function App() {
  const [topic, setTopic] = useState('');
  const [canvasFormats, setCanvasFormats] = useState({ landscape: true, portrait: false });
  const [stylePreset, setStylePreset] = useState('scientific_schematic');
  const [platforms, setPlatforms] = useState({ youtube: true, tiktok: false, instagram: false, twitter: false });
  const [skipUpload, setSkipUpload] = useState(true);
  const [duckingDb, setDuckingDb] = useState(-18.0);
  const [customToken, setCustomToken] = useState('');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authError, setAuthError] = useState('');
  const [authSuccess, setAuthSuccess] = useState('');

  // Service health state
  const [serviceStatus, setServiceStatus] = useState({ status: 'checking', redis_connected: false, api_version: '0.4.0' });

  // Task execution polling
  const [activeTaskId, setActiveTaskId] = useState('');
  const [taskDetails, setTaskDetails] = useState(null);
  const [pollingActive, setPollingActive] = useState(false);

  // Analytics inspector state
  const [analyticsProject, setAnalyticsProject] = useState('heart_circulatory');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);

  // ERP Order simulation state
  const [orderId, setOrderId] = useState('ORD-5501');
  const [orderStatus, setOrderStatus] = useState('PENDING');
  const [orderDispatchResult, setOrderDispatchResult] = useState(null);

  const { data, loading, error, authRequired, setAuthRequired, fetchData } = useDataFetch();

  // Poll system health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/status');
        if (res.ok) {
          const json = await res.json();
          setServiceStatus(json);
        } else {
          setServiceStatus({ status: 'unreachable', redis_connected: false, api_version: 'offline' });
        }
      } catch {
        setServiceStatus({ status: 'offline', redis_connected: false, api_version: 'offline' });
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // When authRequired triggers from hook, open modal
  useEffect(() => {
    if (authRequired) {
      setShowAuthModal(true);
    }
  }, [authRequired]);

  // Task Poller
  useEffect(() => {
    let timer;
    if (pollingActive && activeTaskId) {
      const poll = async () => {
        try {
          const headers = customToken ? { Authorization: `Basic ${btoa(customToken)}` } : {};
          const res = await fetch(`/api/tasks/${activeTaskId}`, { headers });
          if (res.ok) {
            const data = await res.json();
            setTaskDetails(data);
            if (data.ready) {
              setPollingActive(false);
            }
          }
        } catch (e) {
          console.error("Task query error:", e);
        }
      };
      poll();
      timer = setInterval(poll, 3000);
    }
    return () => clearInterval(timer);
  }, [pollingActive, activeTaskId, customToken]);

  // When job generation dispatches, track task ID
  useEffect(() => {
    if (data && data.task_id) {
      setActiveTaskId(data.task_id);
      setPollingActive(true);
    }
  }, [data]);

  const handleGenerate = (e) => {
    e.preventDefault();
    if (!topic.trim()) return;

    const selectedFormats = Object.keys(canvasFormats).filter(k => canvasFormats[k]);
    const selectedPlatforms = Object.keys(platforms).filter(k => platforms[k]);

    fetchData(topic, {
      skip_upload: skipUpload,
      style_preset: stylePreset,
      canvas_format: selectedFormats.length ? selectedFormats : ['landscape'],
      platforms: selectedPlatforms.length ? selectedPlatforms : ['youtube'],
      customToken: customToken || undefined
    });
  };

  const handleTokenHandshake = async (e) => {
    e.preventDefault();
    setAuthError('');
    setAuthSuccess('');
    try {
      const res = await fetch('/api/auth/verify', {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${btoa(customToken)}`
        }
      });
      if (res.ok) {
        setAuthSuccess('Token verified successfully! Background processors retained.');
        setAuthRequired(false);
        setTimeout(() => setShowAuthModal(false), 1200);
      } else {
        setAuthError('Authentication handshake rejected: 401 Unauthorized.');
      }
    } catch {
      setAuthError('Network error during auth handshake.');
    }
  };

  const handleFetchAnalytics = async () => {
    if (!analyticsProject.trim()) return;
    setAnalyticsLoading(true);
    try {
      const headers = customToken ? { Authorization: `Basic ${btoa(customToken)}` } : {};
      const res = await fetch(`/api/analytics/${encodeURIComponent(analyticsProject.trim())}`, { headers });
      if (res.ok) {
        const json = await res.json();
        setAnalyticsData(json);
      }
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const handleOrderTransition = async (e) => {
    e.preventDefault();
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (customToken) headers['Authorization'] = `Basic ${btoa(customToken)}`;
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers,
        body: JSON.stringify({ order_id: orderId, new_status: orderStatus })
      });
      if (res.ok) {
        const json = await res.json();
        setOrderDispatchResult(json);
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="dashboard-container">
      {/* Top Header & Ribbon */}
      <header className="dashboard-header">
        <div>
          <h1 style={{ margin: 0, fontSize: '28px', display: 'flex', alignItems: 'center' }}>
            Educational Video Pipeline
            <span className="brand-badge">v{serviceStatus.api_version || '0.4.0'}</span>
          </h1>
          <p style={{ margin: '4px 0 0', color: 'var(--text-muted)', fontSize: '13px' }}>
            Unified Autonomous Operations Center & Syndication Hub
          </p>
        </div>

        <div className="system-ribbon">
          <div className="status-indicator" title="FastAPI Backend Health">
            <span className={`dot ${serviceStatus.status === 'online' ? 'online' : 'offline'}`} />
            API: {serviceStatus.status}
          </div>
          <div className="status-indicator" title="Redis Message Broker Connection">
            <span className={`dot ${serviceStatus.redis_connected ? 'online' : 'offline'}`} />
            Redis Broker: {serviceStatus.redis_connected ? 'Active' : 'Offline'}
          </div>
          <button
            className="quick-action-btn"
            onClick={() => setShowAuthModal(true)}
            title="Configure or refresh authentication token credentials"
          >
            🔐 Auth Credentials
          </button>
        </div>
      </header>

      {/* Main Grid: Prominent Generator & Monitoring Hub */}
      <div className="dashboard-grid">
        {/* Left Column: High-Value Core Workflows */}
        <div>
          {/* Generation Studio */}
          <section className="dashboard-card">
            <h2 className="card-title">
              Autonomous Video Studio
              <TooltipMarker text="Submits a topic to Wikipedia ingestion, GPT-4o structured script drafting, Stable Diffusion image generation, edge-tts subtitles, and FFmpeg composition." />
            </h2>

            <form onSubmit={handleGenerate}>
              <div className="form-group">
                <label className="form-label">
                  Topic Prompt
                  <TooltipMarker text="Enter an educational subject (e.g. 'Photosynthesis', 'Quantum Computing', or 'Mitosis')." />
                </label>
                <input
                  type="text"
                  className="form-input"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g. The Circulatory System"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  Visual Style Paradigm & Coherence Preset
                  <TooltipMarker text="Select an aesthetic style anchor applied cohesively across all scenes to ensure visual consistency and eliminate jarring scene cuts." />
                </label>
                <select
                  className="form-input"
                  value={stylePreset}
                  onChange={(e) => setStylePreset(e.target.value)}
                >
                  <option value="scientific_schematic">Scientific Schematic (Crisp vector lines, volumetric lighting, clean textbook clarity)</option>
                  <option value="cinematic_documentary">Cinematic Documentary (35mm anamorphic, natural rim lighting, subtle film grain)</option>
                  <option value="historical_engraving">Historical Engraving (19th-century copperplate, intricate cross-hatching, antique sepia)</option>
                  <option value="microscopic_render">Microscopic Render (Confocal microscope, false-color luminescence, sub-cellular glow)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">
                  Canvas Format & Aspect Ratio
                  <TooltipMarker text="Select output layout resolutions. Standard Landscape compiles to 1920x1080; Portrait compiles to 1080x1920." />
                </label>
                <div className="checkbox-row">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={canvasFormats.landscape}
                      onChange={(e) => setCanvasFormats({ ...canvasFormats, landscape: e.target.checked })}
                    />
                    Landscape 16:9 (Standard 1080p)
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={canvasFormats.portrait}
                      onChange={(e) => setCanvasFormats({ ...canvasFormats, portrait: e.target.checked })}
                    />
                    Portrait 9:16 (Shorts / Reels / TikTok)
                  </label>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">
                  Syndication Publishing Targets
                  <TooltipMarker text="Target video syndication networks. Uploads default to 'private' status." />
                </label>
                <div className="checkbox-row">
                  {['youtube', 'tiktok', 'instagram', 'twitter'].map((platform) => (
                    <label key={platform} className="checkbox-label" style={{ textTransform: 'capitalize' }}>
                      <input
                        type="checkbox"
                        checked={platforms[platform]}
                        onChange={(e) => setPlatforms({ ...platforms, [platform]: e.target.checked })}
                      />
                      {platform}
                    </label>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">
                  Continuous Ducking Decibel Attenuation ({duckingDb} dB)
                  <TooltipMarker text="Dynamic volume attenuation multiplier computed via 10^(dB/20.0) to preserve narrator speech frequencies over background music." />
                </label>
                <input
                  type="range"
                  min="-30"
                  max="-6"
                  step="0.5"
                  value={duckingDb}
                  onChange={(e) => setDuckingDb(parseFloat(e.target.value))}
                  style={{ width: '100%' }}
                />
              </div>

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={skipUpload}
                    onChange={(e) => setSkipUpload(e.target.checked)}
                  />
                  Dry Run: Compile assets locally, skip remote platform uploads
                  <TooltipMarker text="When checked, produces complete MP4 files without calling external YouTube/TikTok/Instagram/Twitter APIs." />
                </label>
              </div>

              <button type="submit" className="primary-btn" disabled={loading}>
                {loading ? 'Dispatched to Queue...' : '🚀 Generate Autonomous Video Pipeline'}
              </button>
            </form>

            {error && <div className="alert alert-danger" style={{ marginTop: '16px' }}>{error}</div>}
            {data && (
              <div className="alert alert-success" style={{ marginTop: '16px' }}>
                <strong>Job Dispatched:</strong> Task ID <span className="mono-tag">{data.task_id}</span> queued for '{data.topic}'.
              </div>
            )}
          </section>

          {/* Interactive Player (Phase 6 Branching Engine) */}
          <section className="dashboard-card">
            <h2 className="card-title">
              Interactive Story Branching Web Player
              <TooltipMarker text="Simulates dynamic storyline branches created by the LLM connector. Allows user interaction between sequence transitions." />
            </h2>
            <InteractivePlayer
              scenes={[
                {
                  sequence: 1,
                  text: "Welcome to the cardiovascular interactive tour. Choose which chamber to explore.",
                  choices: [
                    { label: "Left Ventricle (Systemic Loop)", target_sequence: 2 },
                    { label: "Right Atrium (Deoxygenated Return)", target_sequence: 3 }
                  ]
                },
                {
                  sequence: 2,
                  text: "High-pressure oxygenated blood exits through the aorta to power vital organs.",
                  choices: [{ label: "Return to Main Trunk", target_sequence: 1 }]
                },
                {
                  sequence: 3,
                  text: "Deoxygenated blood returns from the vena cava and prepares for pulmonary re-oxygenation.",
                  choices: [{ label: "Inspect Pulmonary Artery", target_sequence: 1 }]
                }
              ]}
            />
          </section>
        </div>

        {/* Right Column: Execution Monitoring & Ecosystem Controls */}
        <div>
          {/* Asynchronous Task Tracker */}
          <section className="dashboard-card">
            <h2 className="card-title">
              Celery Task Execution Monitor
              <TooltipMarker text="Tracks background FFmpeg composition and worker lifecycle states." />
            </h2>
            <div className="form-group">
              <label className="form-label">Active Task Identifier</label>
              <input
                type="text"
                className="form-input"
                value={activeTaskId}
                onChange={(e) => setActiveTaskId(e.target.value)}
                placeholder="Enter Celery Task UUID"
              />
            </div>
            <button
              className="quick-action-btn"
              style={{ width: '100%', justifyContent: 'center', marginBottom: '12px' }}
              onClick={() => setPollingActive(!pollingActive)}
            >
              {pollingActive ? '⏸ Pause Polling' : '🔄 Poll Task Status'}
            </button>

            {taskDetails && (
              <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: '6px', fontSize: '13px' }}>
                <p><strong>Status:</strong> <span className="mono-tag">{taskDetails.status}</span></p>
                <p><strong>Completed:</strong> {taskDetails.ready ? 'Yes' : 'In Progress'}</p>
                {taskDetails.result && (
                  <div style={{ marginTop: '8px' }}>
                    <strong>Output Assets:</strong>
                    <pre style={{ margin: '4px 0 0', fontSize: '11px', overflowX: 'auto' }}>
                      {JSON.stringify(taskDetails.result, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </section>

          {/* Cross-Platform Analytics Inspector */}
          <section className="dashboard-card">
            <h2 className="card-title">
              Cross-Platform Analytics
              <TooltipMarker text="Pulls synthetic platform engagement metrics and sentiment heuristic feedback fed into the LLM prompt generator." />
            </h2>
            <div className="form-group">
              <label className="form-label">Project Identifier</label>
              <input
                type="text"
                className="form-input"
                value={analyticsProject}
                onChange={(e) => setAnalyticsProject(e.target.value)}
                placeholder="project_id"
              />
            </div>
            <button
              className="quick-action-btn"
              style={{ width: '100%', justifyContent: 'center', marginBottom: '12px' }}
              onClick={handleFetchAnalytics}
              disabled={analyticsLoading}
            >
              {analyticsLoading ? 'Querying...' : '📊 Fetch Performance Metrics'}
            </button>

            {analyticsData && (
              <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: '6px', fontSize: '13px' }}>
                <p><strong>Feedback Strategy:</strong></p>
                <p style={{ color: 'var(--accent)', fontStyle: 'italic', marginBottom: '8px' }}>
                  "{analyticsData.feedback_summary}"
                </p>
                <strong>Raw Metrics:</strong>
                <pre style={{ margin: '4px 0 0', fontSize: '11px', overflowX: 'auto' }}>
                  {JSON.stringify(analyticsData.metrics, null, 2)}
                </pre>
              </div>
            )}
          </section>

          {/* ERP Order Lifecycle Studio */}
          <section className="dashboard-card">
            <h2 className="card-title">
              ERP Order Event Simulator
              <TooltipMarker text="Demonstrates event-driven queue handling by simulating upstream supply-chain status transitions." />
            </h2>
            <form onSubmit={handleOrderTransition}>
              <div className="form-group">
                <label className="form-label">Order Reference ID</label>
                <input
                  type="text"
                  className="form-input"
                  value={orderId}
                  onChange={(e) => setOrderId(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Target State</label>
                <select
                  className="form-input"
                  value={orderStatus}
                  onChange={(e) => setOrderStatus(e.target.value)}
                >
                  <option value="PENDING">PENDING</option>
                  <option value="PROCESSING">PROCESSING</option>
                  <option value="RENDERED">RENDERED</option>
                  <option value="SHIPPED">SHIPPED</option>
                </select>
              </div>
              <button type="submit" className="quick-action-btn" style={{ width: '100%', justifyContent: 'center' }}>
                ⚡ Dispatch Order Transition
              </button>
            </form>

            {orderDispatchResult && (
              <div style={{ background: 'var(--bg-card)', padding: '10px', borderRadius: '6px', fontSize: '12px', marginTop: '12px' }}>
                <p><strong>Event Dispatched:</strong></p>
                <p>Order: <span className="mono-tag">{orderDispatchResult.order_id}</span></p>
                <p>State: <span className="mono-tag">{orderDispatchResult.new_status}</span></p>
                <p>Task UUID: <span className="mono-tag">{orderDispatchResult.task_id}</span></p>
              </div>
            )}
          </section>

          {/* Desktop Tray Controller Guide */}
          <section className="dashboard-card">
            <h2 className="card-title">
              Desktop System Tray Manager
              <TooltipMarker text="Run `python -m src.tray_icon` to control background servers directly from your desktop system tray." />
            </h2>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '10px' }}>
              Control all pipeline background services with the native system tray daemon:
            </p>
            <div style={{ background: 'var(--bg-card)', padding: '10px', borderRadius: '6px', fontSize: '12px' }}>
              <code>python src/tray_icon.py</code>
              <ul style={{ paddingLeft: '18px', margin: '8px 0 0' }}>
                <li>Status Indicator & Health query</li>
                <li>Quick Dashboard Launcher</li>
                <li>Safe Service Restart</li>
                <li>Graceful Shutdown of Uvicorn & Celery</li>
              </ul>
            </div>
          </section>
        </div>
      </div>

      {/* Dynamic Token-Refresh Modal (Phase 7 Handshake) */}
      {showAuthModal && (
        <div className="modal-overlay" onClick={() => setShowAuthModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ marginTop: 0 }}>API Authentication Handshake</h3>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              Configure your Basic Auth token credentials (<span className="mono-tag">username:password</span>) without halting running Celery tasks.
            </p>

            <form onSubmit={handleTokenHandshake}>
              <div className="form-group">
                <label className="form-label">Credentials (user:password)</label>
                <input
                  type="password"
                  className="form-input"
                  value={customToken}
                  onChange={(e) => setCustomToken(e.target.value)}
                  placeholder="admin:local_dev_password"
                  required
                />
              </div>

              {authError && <div className="alert alert-danger">{authError}</div>}
              {authSuccess && <div className="alert alert-success">{authSuccess}</div>}

              <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
                <button type="submit" className="primary-btn">
                  Verify & Retain Handshake
                </button>
                <button
                  type="button"
                  className="quick-action-btn"
                  onClick={() => setShowAuthModal(false)}
                >
                  Close
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
