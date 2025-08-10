import React, { useState, useEffect } from 'react';

const EnterpriseThreadManager = ({ miningConfig, onConfigChange, systemStats }) => {
  const [cpuInfo, setCpuInfo] = useState({});
  const [threadPresets, setThreadPresets] = useState({});
  const [isEnterprise, setIsEnterprise] = useState(false);
  const [customThreadCount, setCustomThreadCount] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loadingCpuInfo, setLoadingCpuInfo] = useState(false);

  useEffect(() => {
    fetchCpuInfo();
  }, []);

  const fetchCpuInfo = async () => {
    setLoadingCpuInfo(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/system/cpu-info`);
      if (response.ok) {
        const data = await response.json();
        setCpuInfo(data);
        
        // Check if enterprise mode is detected
        setIsEnterprise(data.enterprise_mode || data.logical_cores >= 32);
        
        // Set thread presets based on system capabilities
        setThreadPresets({
          conservative: data.recommended_threads?.low || Math.max(1, Math.floor(data.logical_cores * 0.25)),
          balanced: data.recommended_threads?.medium || Math.max(1, Math.floor(data.logical_cores * 0.5)),
          aggressive: data.recommended_threads?.high || Math.max(1, Math.floor(data.logical_cores * 0.75)),
          maximum: data.recommended_threads?.maximum || data.max_safe_threads || data.logical_cores,
          enterprise_max: Math.min(data.max_safe_threads || 250000, 250000)
        });

        // Auto-set thread count if not already set
        if (miningConfig.threads <= 4 && data.recommended_threads?.medium) {
          onConfigChange({
            ...miningConfig,
            threads: data.recommended_threads.medium
          });
        }
      }
    } catch (error) {
      console.error('Failed to fetch CPU info:', error);
    } finally {
      setLoadingCpuInfo(false);
    }
  };

  const handleThreadPresetSelect = (presetName) => {
    const threadCount = threadPresets[presetName];
    if (threadCount) {
      onConfigChange({
        ...miningConfig,
        threads: threadCount
      });
      setCustomThreadCount(''); // Clear custom input when preset is selected
    }
  };

  const handleCustomThreadChange = (value) => {
    setCustomThreadCount(value);
    const numValue = parseInt(value) || 0;
    if (numValue > 0) {
      onConfigChange({
        ...miningConfig,
        threads: Math.min(numValue, cpuInfo.max_safe_threads || 250000)
      });
    }
  };

  const formatNumber = (num) => {
    if (!num) return '0';
    return num.toLocaleString();
  };

  const getThreadEfficiencyEstimate = (threads) => {
    if (!cpuInfo.logical_cores) return 'Unknown';
    const ratio = threads / cpuInfo.logical_cores;
    if (ratio <= 1) return 'Conservative';
    if (ratio <= 4) return 'Balanced';
    if (ratio <= 16) return 'Aggressive';
    if (ratio <= 64) return 'Enterprise';
    return 'Maximum';
  };

  const getPerformanceProjection = (threads) => {
    if (!cpuInfo.logical_cores || !threads) return { cpu: 0, efficiency: 'Low' };
    
    const coreRatio = threads / cpuInfo.logical_cores;
    let estimatedCpu = Math.min(coreRatio * 25, 100); // Rough estimation
    
    if (coreRatio >= 4) estimatedCpu = Math.min(85 + (coreRatio - 4) * 2, 100);
    if (coreRatio >= 16) estimatedCpu = Math.min(95 + (coreRatio - 16) * 0.5, 100);
    
    let efficiency = 'Low';
    if (estimatedCpu >= 90) efficiency = 'Maximum';
    else if (estimatedCpu >= 70) efficiency = 'High';
    else if (estimatedCpu >= 40) efficiency = 'Medium';
    
    return { cpu: estimatedCpu, efficiency };
  };

  const projection = getPerformanceProjection(miningConfig.threads);

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">⚡ Enterprise Thread Manager</h3>
        {isEnterprise && (
          <div className="status-badge status-success">
            Enterprise Mode
          </div>
        )}
      </div>
      <div className="card-content">
        {loadingCpuInfo ? (
          <div className="loading-indicator">
            <span>🔍 Analyzing system capabilities...</span>
          </div>
        ) : (
          <>
            {/* System Overview */}
            <div className="system-overview">
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-value">{formatNumber(cpuInfo.logical_cores || 0)}</div>
                  <div className="metric-label">Logical Cores</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{formatNumber(cpuInfo.max_safe_threads || 0)}</div>
                  <div className="metric-label">Max Safe Threads</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{(cpuInfo.total_memory_gb || 0).toFixed(1)}GB</div>
                  <div className="metric-label">Total Memory</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{cpuInfo.architecture || 'Unknown'}</div>
                  <div className="metric-label">Architecture</div>
                </div>
              </div>
            </div>

            {/* Thread Configuration */}
            <div className="thread-config-section">
              <h4>Thread Configuration</h4>
              
              {/* Current Configuration Display */}
              <div className="current-config-display">
                <div className="config-summary">
                  <span className="config-threads">
                    {formatNumber(miningConfig.threads)} threads
                  </span>
                  <span className="config-efficiency">
                    ({getThreadEfficiencyEstimate(miningConfig.threads)} Mode)
                  </span>
                </div>
                <div className="performance-projection">
                  <div className="projection-item">
                    <span className="projection-label">Est. CPU Usage:</span>
                    <span className="projection-value">{projection.cpu.toFixed(1)}%</span>
                  </div>
                  <div className="projection-item">
                    <span className="projection-label">Performance Level:</span>
                    <span className="projection-value">{projection.efficiency}</span>
                  </div>
                </div>
              </div>

              {/* Thread Presets */}
              <div className="thread-presets">
                <h5>Quick Presets</h5>
                <div className="preset-buttons">
                  {Object.entries(threadPresets).filter(([_, count]) => 
                    typeof count === 'number' && count > 0
                  ).map(([presetName, threadCount]) => {
                    const isActive = miningConfig.threads === threadCount;
                    const displayName = presetName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                    
                    return (
                      <button
                        key={presetName}
                        className={`preset-btn ${isActive ? 'active' : ''}`}
                        onClick={() => handleThreadPresetSelect(presetName)}
                        title={`${formatNumber(threadCount)} threads`}
                      >
                        <div className="preset-name">{displayName}</div>
                        <div className="preset-count">{formatNumber(threadCount)}</div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Custom Thread Input */}
              <div className="custom-thread-input">
                <label className="form-label">
                  Custom Thread Count (1 - {formatNumber(cpuInfo.max_safe_threads || 250000)})
                </label>
                <div className="input-group">
                  <input
                    type="number"
                    className="form-input"
                    value={customThreadCount}
                    onChange={(e) => handleCustomThreadChange(e.target.value)}
                    placeholder="Enter custom thread count"
                    min="1"
                    max={cpuInfo.max_safe_threads || 250000}
                  />
                  <button
                    className="btn btn-secondary"
                    onClick={() => handleCustomThreadChange(customThreadCount)}
                    disabled={!customThreadCount}
                  >
                    Apply
                  </button>
                </div>
              </div>

              {/* Advanced Settings Toggle */}
              <button
                className="advanced-toggle"
                onClick={() => setShowAdvanced(!showAdvanced)}
              >
                <span>⚙️ Advanced Settings</span>
                <span>{showAdvanced ? '▲' : '▼'}</span>
              </button>

              {/* Advanced Settings Panel */}
              {showAdvanced && (
                <div className="advanced-settings">
                  <div className="form-group">
                    <label className="form-label">Thread Profile</label>
                    <select
                      className="form-select"
                      value={miningConfig.thread_profile}
                      onChange={(e) => onConfigChange({
                        ...miningConfig,
                        thread_profile: e.target.value
                      })}
                    >
                      <option value="conservative">Conservative (Low Resource)</option>
                      <option value="standard">Standard (Balanced)</option>
                      <option value="aggressive">Aggressive (High Performance)</option>
                      <option value="enterprise">Enterprise (Maximum Throughput)</option>
                    </select>
                  </div>

                  <div className="checkbox-group">
                    <div className="checkbox-container">
                      <input
                        type="checkbox"
                        className="checkbox"
                        checked={miningConfig.auto_thread_detection}
                        onChange={(e) => onConfigChange({
                          ...miningConfig,
                          auto_thread_detection: e.target.checked
                        })}
                      />
                      <label>Auto Thread Detection</label>
                    </div>
                    <div className="checkbox-container">
                      <input
                        type="checkbox"
                        className="checkbox"
                        checked={miningConfig.thread_scaling_enabled !== false}
                        onChange={(e) => onConfigChange({
                          ...miningConfig,
                          thread_scaling_enabled: e.target.checked
                        })}
                      />
                      <label>Dynamic Thread Scaling</label>
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Target CPU Utilization (%)</label>
                    <input
                      type="range"
                      className="range-slider"
                      min="25"
                      max="100"
                      step="5"
                      value={(miningConfig.target_cpu_utilization || 1.0) * 100}
                      onChange={(e) => onConfigChange({
                        ...miningConfig,
                        target_cpu_utilization: parseFloat(e.target.value) / 100
                      })}
                    />
                    <div className="range-value">
                      {((miningConfig.target_cpu_utilization || 1.0) * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Performance Warnings */}
            {miningConfig.threads > (cpuInfo.logical_cores || 1) * 32 && (
              <div className="warning-message">
                <span className="warning-icon">⚠️</span>
                <div>
                  <strong>High Thread Count Warning</strong>
                  <p>You're using {Math.round(miningConfig.threads / (cpuInfo.logical_cores || 1))}x your CPU core count. 
                     Monitor system stability and temperature.</p>
                </div>
              </div>
            )}

            {isEnterprise && miningConfig.threads >= 1000 && (
              <div className="enterprise-notice">
                <span className="info-icon">ℹ️</span>
                <div>
                  <strong>Enterprise Scale Detected</strong>
                  <p>Running {formatNumber(miningConfig.threads)} threads in enterprise mode. 
                     Ensure adequate cooling and power supply.</p>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default EnterpriseThreadManager;