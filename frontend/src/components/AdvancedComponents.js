import React, { useState, useEffect, useCallback } from 'react';

// ============================================================================
// ENTERPRISE THREAD MANAGER COMPONENT
// ============================================================================

const EnterpriseThreadManager = ({ miningConfig, onConfigChange, systemStats }) => {
  const [cpuInfo, setCpuInfo] = useState({});
  const [threadPresets, setThreadPresets] = useState({});
  const [isEnterprise, setIsEnterprise] = useState(false);
  const [customThreadCount, setCustomThreadCount] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loadingCpuInfo, setLoadingCpuInfo] = useState(false);

  const fetchCpuInfo = useCallback(async () => {
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
  }, [miningConfig, onConfigChange]);

  useEffect(() => {
    fetchCpuInfo();
  }, [fetchCpuInfo]);

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

// ============================================================================
// ENTERPRISE DATABASE CONFIG COMPONENT
// ============================================================================

const EnterpriseDBConfig = ({ onConfigChange }) => {
  const [dbConfig, setDbConfig] = useState({
    useRemoteDB: false,
    remoteUrl: '',
    connectionStatus: 'Unknown',
    testingConnection: false
  });

  const [showAdvancedConfig, setShowAdvancedConfig] = useState(false);

  const checkDatabaseStatus = useCallback(async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/health`);
      if (response.ok) {
        const data = await response.json();
        const dbStatus = data.database?.status || 'unknown';
        
        let connectionStatus = 'Unknown';
        if (dbStatus === 'connected') {
          connectionStatus = 'Connected';
        } else if (dbStatus === 'disconnected') {
          connectionStatus = 'Disconnected';
        } else {
          connectionStatus = 'Error';
        }
        
        setDbConfig(prev => ({
          ...prev,
          connectionStatus: connectionStatus
        }));
      } else {
        setDbConfig(prev => ({
          ...prev,
          connectionStatus: 'Error'
        }));
      }
    } catch (error) {
      console.error('Database status check failed:', error);
      setDbConfig(prev => ({
        ...prev,
        connectionStatus: 'Error'
      }));
    }
  }, []);

  useEffect(() => {
    // Check current database configuration
    checkDatabaseStatus();
  }, [checkDatabaseStatus]);

  const testDatabaseConnection = async (url) => {
    setDbConfig(prev => ({ ...prev, testingConnection: true }));
    
    try {
      // For now, this would need to be implemented in the backend
      // The frontend can't directly test database connections for security
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/test-db-connection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ database_url: url })
      });

      const result = await response.json();
      
      setDbConfig(prev => ({
        ...prev,
        connectionStatus: result.success ? 'Connected' : 'Failed',
        testingConnection: false
      }));

      return result.success;
    } catch (error) {
      console.error('Database connection test failed:', error);
      setDbConfig(prev => ({
        ...prev,
        connectionStatus: 'Error',
        testingConnection: false
      }));
      return false;
    }
  };

  const handleRemoteDBToggle = (enabled) => {
    setDbConfig(prev => ({
      ...prev,
      useRemoteDB: enabled
    }));

    if (onConfigChange) {
      onConfigChange({
        remote_db_enabled: enabled,
        remote_mongo_url: dbConfig.remoteUrl
      });
    }
  };

  const handleRemoteUrlChange = (url) => {
    setDbConfig(prev => ({
      ...prev,
      remoteUrl: url
    }));
  };

  const applyDatabaseConfig = async () => {
    if (dbConfig.useRemoteDB && dbConfig.remoteUrl) {
      const success = await testDatabaseConnection(dbConfig.remoteUrl);
      if (success && onConfigChange) {
        onConfigChange({
          remote_db_enabled: true,
          remote_mongo_url: dbConfig.remoteUrl
        });
      }
    } else {
      if (onConfigChange) {
        onConfigChange({
          remote_db_enabled: false,
          remote_mongo_url: ''
        });
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Connected': return 'status-success';
      case 'Disconnected': return 'status-warning';
      case 'Error': case 'Failed': return 'status-error';
      default: return 'status-secondary';
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">🗄️ Enterprise Database Configuration</h3>
        <div className={`status-badge ${getStatusColor(dbConfig.connectionStatus)}`}>
          {dbConfig.connectionStatus}
        </div>
      </div>
      <div className="card-content">
        {/* Database Status Overview */}
        <div className="db-status-overview">
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-value">
                {dbConfig.useRemoteDB ? 'Remote' : 'Local'}
              </div>
              <div className="metric-label">Database Type</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">
                {dbConfig.connectionStatus}
              </div>
              <div className="metric-label">Connection Status</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">MongoDB</div>
              <div className="metric-label">Database Engine</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">
                {dbConfig.useRemoteDB ? 'Enterprise' : 'Standard'}
              </div>
              <div className="metric-label">Configuration Mode</div>
            </div>
          </div>
        </div>

        {/* Database Configuration Options */}
        <div className="db-config-options">
          <div className="form-group">
            <div className="checkbox-container">
              <input
                type="checkbox"
                className="checkbox"
                checked={dbConfig.useRemoteDB}
                onChange={(e) => handleRemoteDBToggle(e.target.checked)}
              />
              <label className="db-config-label">
                <span>Use Remote Database Server</span>
                <small>Connect to a separate MongoDB server for enterprise scalability</small>
              </label>
            </div>
          </div>

          {dbConfig.useRemoteDB && (
            <div className="remote-db-config fade-in">
              <div className="form-group">
                <label className="form-label">Remote MongoDB URL</label>
                <div className="input-group">
                  <input
                    type="text"
                    className="form-input"
                    value={dbConfig.remoteUrl}
                    onChange={(e) => handleRemoteUrlChange(e.target.value)}
                    placeholder="mongodb://username:password@host:port/database"
                  />
                  <button
                    className="btn btn-secondary"
                    onClick={() => testDatabaseConnection(dbConfig.remoteUrl)}
                    disabled={dbConfig.testingConnection || !dbConfig.remoteUrl}
                  >
                    {dbConfig.testingConnection ? '⏳ Testing...' : '🔍 Test'}
                  </button>
                </div>
                <small className="form-help">
                  Format: mongodb://[username:password@]host[:port][/database]
                </small>
              </div>

              <div className="remote-db-examples">
                <h5>Example Configurations:</h5>
                <div className="example-configs">
                  <div className="example-config">
                    <code>mongodb://192.168.1.100:27017/crypto_miner_db</code>
                    <small>Local network server</small>
                  </div>
                  <div className="example-config">
                    <code>mongodb://user:pass@db.example.com:27017/crypto_miner_db</code>
                    <small>Remote server with authentication</small>
                  </div>
                  <div className="example-config">
                    <code>mongodb+srv://cluster.mongodb.net/crypto_miner_db</code>
                    <small>MongoDB Atlas cluster</small>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Advanced Configuration Toggle */}
        <button
          className="advanced-toggle"
          onClick={() => setShowAdvancedConfig(!showAdvancedConfig)}
        >
          <span>⚙️ Advanced Database Settings</span>
          <span>{showAdvancedConfig ? '▲' : '▼'}</span>
        </button>

        {/* Advanced Configuration Panel */}
        {showAdvancedConfig && (
          <div className="advanced-settings">
            <div className="enterprise-notice">
              <span className="info-icon">ℹ️</span>
              <div>
                <strong>Enterprise Database Features</strong>
                <ul>
                  <li>✅ Separate database server support</li>
                  <li>✅ Connection pooling for high-throughput</li>
                  <li>✅ Automatic failover support</li>
                  <li>✅ Read/Write splitting capabilities</li>
                  <li>✅ Real-time replication monitoring</li>
                </ul>
              </div>
            </div>

            <div className="db-performance-info">
              <h5>Database Performance Optimization</h5>
              <div className="performance-tips">
                <div className="tip-item">
                  <span className="tip-icon">🚀</span>
                  <div>
                    <strong>High-Throughput Setup</strong>
                    <p>For mining operations with 50,000+ threads, consider MongoDB sharding</p>
                  </div>
                </div>
                <div className="tip-item">
                  <span className="tip-icon">📊</span>
                  <div>
                    <strong>Data Center Deployment</strong>
                    <p>Use replica sets for high availability in enterprise environments</p>
                  </div>
                </div>
                <div className="tip-item">
                  <span className="tip-icon">🔒</span>
                  <div>
                    <strong>Security Considerations</strong>
                    <p>Enable authentication and use SSL/TLS for remote connections</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Apply Configuration Button */}
        <div className="config-actions">
          <button
            className="btn btn-primary"
            onClick={applyDatabaseConfig}
            disabled={dbConfig.testingConnection}
          >
            {dbConfig.testingConnection ? '⏳ Applying...' : '💾 Apply Configuration'}
          </button>
          
          <button
            className="btn btn-secondary"
            onClick={checkDatabaseStatus}
          >
            🔄 Refresh Status
          </button>
        </div>

        {/* Configuration Warnings */}
        {dbConfig.useRemoteDB && !dbConfig.remoteUrl && (
          <div className="warning-message">
            <span className="warning-icon">⚠️</span>
            <div>
              <strong>Configuration Required</strong>
              <p>Please enter a remote MongoDB URL to enable remote database access.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// SAVED POOLS MANAGER COMPONENT
// ============================================================================

const SavedPoolsManager = ({ onUsePool, onClose, currentConfig }) => {
    const [savedPools, setSavedPools] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    const [editingPool, setEditingPool] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        coin_symbol: 'LTC',
        wallet_address: '',
        pool_address: '',
        pool_port: 3333,
        pool_password: 'x',
        pool_username: '',
        description: ''
    });

    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

    useEffect(() => {
        fetchSavedPools();
    }, [fetchSavedPools]);

    const fetchSavedPools = useCallback(async () => {
        try {
            const response = await fetch(`${backendUrl}/api/pools/saved`);
            if (response.ok) {
                const data = await response.json();
                setSavedPools(data.pools || []);
            }
        } catch (error) {
            console.error('Failed to fetch saved pools:', error);
        }
        setLoading(false);
    }, [backendUrl]);

    const handleSave = async () => {
        try {
            const url = editingPool 
                ? `${backendUrl}/api/pools/saved/${editingPool._id}`
                : `${backendUrl}/api/pools/saved`;
            
            const method = editingPool ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                await fetchSavedPools();
                setShowAddForm(false);
                setEditingPool(null);
                resetForm();
            } else {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            }
        } catch (error) {
            console.error('Save error:', error);
            alert('Failed to save pool configuration');
        }
    };

    const handleDelete = async (poolId) => {
        if (window.confirm('Are you sure you want to delete this pool configuration?')) {
            try {
                const response = await fetch(`${backendUrl}/api/pools/saved/${poolId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    await fetchSavedPools();
                }
            } catch (error) {
                console.error('Delete error:', error);
            }
        }
    };

    const handleUse = async (pool) => {
        try {
            const response = await fetch(`${backendUrl}/api/pools/saved/${pool._id}/use`, {
                method: 'POST'
            });

            if (response.ok) {
                const data = await response.json();
                onUsePool(data.mining_config, pool);
                onClose();
            }
        } catch (error) {
            console.error('Use pool error:', error);
        }
    };

    const handleEdit = (pool) => {
        setFormData({
            name: pool.name,
            coin_symbol: pool.coin_symbol,
            wallet_address: pool.wallet_address,
            pool_address: pool.pool_address,
            pool_port: pool.pool_port,
            pool_password: pool.pool_password || 'x',
            pool_username: pool.pool_username || '',
            description: pool.description || ''
        });
        setEditingPool(pool);
        setShowAddForm(true);
    };

    const saveCurrentConfig = () => {
        if (currentConfig) {
            setFormData({
                name: `${currentConfig.coin?.symbol || 'Unknown'} Pool Config`,
                coin_symbol: currentConfig.coin?.symbol || 'LTC',
                wallet_address: currentConfig.wallet_address || '',
                pool_address: currentConfig.coin?.custom_pool_address || '',
                pool_port: currentConfig.coin?.custom_pool_port || 3333,
                pool_password: currentConfig.pool_password || 'x',
                pool_username: currentConfig.pool_username || '',
                description: 'Auto-saved from current configuration'
            });
            setShowAddForm(true);
        }
    };

    const resetForm = () => {
        setFormData({
            name: '',
            coin_symbol: 'LTC',
            wallet_address: '',
            pool_address: '',
            pool_port: 3333,
            pool_password: 'x',
            pool_username: '',
            description: ''
        });
    };

    if (loading) {
        return <div className="text-center p-8">Loading saved pools...</div>;
    }

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-green-400">
                        💾 Saved Pool Configurations
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white text-xl"
                    >
                        ✕
                    </button>
                </div>

                {!showAddForm ? (
                    <>
                        <div className="flex gap-3 mb-6">
                            <button
                                onClick={() => setShowAddForm(true)}
                                className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-medium"
                            >
                                ➕ Add New Pool
                            </button>
                            {currentConfig && (
                                <button
                                    onClick={saveCurrentConfig}
                                    className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium"
                                >
                                    💾 Save Current Config
                                </button>
                            )}
                        </div>

                        {savedPools.length === 0 ? (
                            <div className="text-center text-gray-400 py-8">
                                <p className="text-lg mb-2">No saved pool configurations yet</p>
                                <p>Save your frequently used pool settings for quick access!</p>
                            </div>
                        ) : (
                            <div className="grid gap-4">
                                {savedPools.map((pool) => (
                                    <div key={pool._id} className="bg-gray-700 rounded-lg p-4">
                                        <div className="flex justify-between items-start">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <h3 className="text-lg font-semibold text-white">
                                                        {pool.name}
                                                    </h3>
                                                    <span className="bg-green-600 px-2 py-1 rounded text-sm">
                                                        {pool.coin_symbol}
                                                    </span>
                                                </div>
                                                
                                                <div className="grid grid-cols-2 gap-4 text-sm text-gray-300">
                                                    <div>
                                                        <span className="text-gray-400">Pool:</span>{' '}
                                                        {pool.pool_address}:{pool.pool_port}
                                                    </div>
                                                    <div>
                                                        <span className="text-gray-400">Wallet:</span>{' '}
                                                        {pool.wallet_address ? 
                                                            `${pool.wallet_address.slice(0, 10)}...${pool.wallet_address.slice(-4)}` 
                                                            : 'Not set'
                                                        }
                                                    </div>
                                                </div>
                                                
                                                {pool.description && (
                                                    <p className="text-gray-400 text-sm mt-2">
                                                        {pool.description}
                                                    </p>
                                                )}
                                                
                                                {pool.last_used && (
                                                    <p className="text-gray-500 text-xs mt-2">
                                                        Last used: {new Date(pool.last_used).toLocaleDateString()}
                                                    </p>
                                                )}
                                            </div>
                                            
                                            <div className="flex gap-2 ml-4">
                                                <button
                                                    onClick={() => handleUse(pool)}
                                                    className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm"
                                                >
                                                    ▶️ Use
                                                </button>
                                                <button
                                                    onClick={() => handleEdit(pool)}
                                                    className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm"
                                                >
                                                    ✏️ Edit
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(pool._id)}
                                                    className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm"
                                                >
                                                    🗑️
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </>
                ) : (
                    <div>
                        <h3 className="text-xl font-semibold mb-4">
                            {editingPool ? 'Edit Pool Configuration' : 'Add New Pool Configuration'}
                        </h3>
                        
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Configuration Name *
                                </label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="My Pool Config"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Coin Symbol *
                                </label>
                                <select
                                    value={formData.coin_symbol}
                                    onChange={(e) => setFormData({...formData, coin_symbol: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                >
                                    <option value="LTC">Litecoin (LTC)</option>
                                    <option value="DOGE">Dogecoin (DOGE)</option>
                                    <option value="FTC">Feathercoin (FTC)</option>
                                    <option value="EFL">E-Gulden (EFL)</option>
                                </select>
                            </div>
                            
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Wallet Address *
                                </label>
                                <input
                                    type="text"
                                    value={formData.wallet_address}
                                    onChange={(e) => setFormData({...formData, wallet_address: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="Your wallet address"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Pool Address *
                                </label>
                                <input
                                    type="text"
                                    value={formData.pool_address}
                                    onChange={(e) => setFormData({...formData, pool_address: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="pool.example.com"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Pool Port *
                                </label>
                                <input
                                    type="number"
                                    value={formData.pool_port}
                                    onChange={(e) => setFormData({...formData, pool_port: parseInt(e.target.value)})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="3333"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Pool Username
                                </label>
                                <input
                                    type="text"
                                    value={formData.pool_username}
                                    onChange={(e) => setFormData({...formData, pool_username: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="Usually your wallet address"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Pool Password
                                </label>
                                <input
                                    type="text"
                                    value={formData.pool_password}
                                    onChange={(e) => setFormData({...formData, pool_password: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="x"
                                />
                            </div>
                            
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Description (Optional)
                                </label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white h-20"
                                    placeholder="Notes about this pool configuration..."
                                />
                            </div>
                        </div>
                        
                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={handleSave}
                                className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded-lg font-medium"
                            >
                                💾 Save Configuration
                            </button>
                            <button
                                onClick={() => {
                                    setShowAddForm(false);
                                    setEditingPool(null);
                                    resetForm();
                                }}
                                className="bg-gray-600 hover:bg-gray-700 px-6 py-2 rounded-lg font-medium"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

// ============================================================================
// CUSTOM COINS MANAGER COMPONENT
// ============================================================================

const CustomCoinsManager = ({ onSelectCoin, onClose }) => {
    const [customCoins, setCustomCoins] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    const [editingCoin, setEditingCoin] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        symbol: '',
        algorithm: 'Scrypt',
        block_reward: 25.0,
        block_time: 150,
        difficulty: 1000.0,
        scrypt_params: {
            n: 1024,
            r: 1,
            p: 1
        },
        network_hashrate: 'Unknown',
        wallet_format: 'Standard',
        description: ''
    });

    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

    useEffect(() => {
        fetchCustomCoins();
    }, [fetchCustomCoins]);

    const fetchCustomCoins = useCallback(async () => {
        try {
            const response = await fetch(`${backendUrl}/api/coins/custom`);
            if (response.ok) {
                const data = await response.json();
                setCustomCoins(data.coins || []);
            }
        } catch (error) {
            console.error('Failed to fetch custom coins:', error);
        }
        setLoading(false);
    }, [backendUrl]);

    const handleSave = async () => {
        try {
            // Validate required fields
            if (!formData.name.trim() || !formData.symbol.trim()) {
                alert('Name and Symbol are required');
                return;
            }

            const url = editingCoin 
                ? `${backendUrl}/api/coins/custom/${editingCoin._id}`
                : `${backendUrl}/api/coins/custom`;
            
            const method = editingCoin ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                await fetchCustomCoins();
                setShowAddForm(false);
                setEditingCoin(null);
                resetForm();
            } else {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            }
        } catch (error) {
            console.error('Save error:', error);
            alert('Failed to save custom coin');
        }
    };

    const handleDelete = async (coinId) => {
        if (window.confirm('Are you sure you want to delete this custom coin?')) {
            try {
                const response = await fetch(`${backendUrl}/api/coins/custom/${coinId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    await fetchCustomCoins();
                }
            } catch (error) {
                console.error('Delete error:', error);
            }
        }
    };

    const handleSelect = (coin) => {
        // Convert custom coin to CoinConfig format
        const coinConfig = {
            name: coin.name,
            symbol: coin.symbol,
            algorithm: coin.algorithm,
            block_reward: coin.block_reward,
            block_time: coin.block_time,
            difficulty: coin.difficulty,
            scrypt_params: coin.scrypt_params,
            network_hashrate: coin.network_hashrate,
            wallet_format: coin.wallet_format,
            is_custom: true
        };
        
        onSelectCoin(coinConfig);
        onClose();
    };

    const handleEdit = (coin) => {
        setFormData({
            name: coin.name,
            symbol: coin.symbol,
            algorithm: coin.algorithm,
            block_reward: coin.block_reward,
            block_time: coin.block_time,
            difficulty: coin.difficulty,
            scrypt_params: coin.scrypt_params,
            network_hashrate: coin.network_hashrate,
            wallet_format: coin.wallet_format,
            description: coin.description || ''
        });
        setEditingCoin(coin);
        setShowAddForm(true);
    };

    const resetForm = () => {
        setFormData({
            name: '',
            symbol: '',
            algorithm: 'Scrypt',
            block_reward: 25.0,
            block_time: 150,
            difficulty: 1000.0,
            scrypt_params: {
                n: 1024,
                r: 1,
                p: 1
            },
            network_hashrate: 'Unknown',
            wallet_format: 'Standard',
            description: ''
        });
    };

    const algorithmOptions = [
        'Scrypt',
        'SHA-256',
        'X11',
        'Lyra2REv2',
        'Equihash',
        'CryptoNote',
        'Other'
    ];

    if (loading) {
        return <div className="text-center p-8">Loading custom coins...</div>;
    }

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 max-w-5xl w-full max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-green-400">
                        🪙 Custom Coin Manager
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white text-xl"
                    >
                        ✕
                    </button>
                </div>

                {!showAddForm ? (
                    <>
                        <div className="flex gap-3 mb-6">
                            <button
                                onClick={() => setShowAddForm(true)}
                                className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-medium"
                            >
                                ➕ Add Custom Coin
                            </button>
                        </div>

                        {customCoins.length === 0 ? (
                            <div className="text-center text-gray-400 py-8">
                                <p className="text-lg mb-2">No custom coins created yet</p>
                                <p>Add custom coins to mine new or unlisted cryptocurrencies!</p>
                            </div>
                        ) : (
                            <div className="grid gap-4">
                                {customCoins.map((coin) => (
                                    <div key={coin._id} className="bg-gray-700 rounded-lg p-4">
                                        <div className="flex justify-between items-start">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <h3 className="text-lg font-semibold text-white">
                                                        {coin.name}
                                                    </h3>
                                                    <span className="bg-purple-600 px-2 py-1 rounded text-sm">
                                                        {coin.symbol}
                                                    </span>
                                                    <span className="bg-gray-600 px-2 py-1 rounded text-xs">
                                                        {coin.algorithm}
                                                    </span>
                                                </div>
                                                
                                                <div className="grid grid-cols-3 gap-4 text-sm text-gray-300">
                                                    <div>
                                                        <span className="text-gray-400">Block Reward:</span>{' '}
                                                        {coin.block_reward} {coin.symbol}
                                                    </div>
                                                    <div>
                                                        <span className="text-gray-400">Block Time:</span>{' '}
                                                        {coin.block_time}s
                                                    </div>
                                                    <div>
                                                        <span className="text-gray-400">Difficulty:</span>{' '}
                                                        {coin.difficulty.toLocaleString()}
                                                    </div>
                                                </div>

                                                {coin.algorithm === 'Scrypt' && (
                                                    <div className="text-sm text-gray-300 mt-2">
                                                        <span className="text-gray-400">Scrypt Params:</span>{' '}
                                                        N={coin.scrypt_params?.n}, R={coin.scrypt_params?.r}, P={coin.scrypt_params?.p}
                                                    </div>
                                                )}
                                                
                                                {coin.description && (
                                                    <p className="text-gray-400 text-sm mt-2">
                                                        {coin.description}
                                                    </p>
                                                )}
                                            </div>
                                            
                                            <div className="flex gap-2 ml-4">
                                                <button
                                                    onClick={() => handleSelect(coin)}
                                                    className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm"
                                                >
                                                    ⚡ Select
                                                </button>
                                                <button
                                                    onClick={() => handleEdit(coin)}
                                                    className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm"
                                                >
                                                    ✏️ Edit
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(coin._id)}
                                                    className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm"
                                                >
                                                    🗑️
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </>
                ) : (
                    <div>
                        <h3 className="text-xl font-semibold mb-4">
                            {editingCoin ? 'Edit Custom Coin' : 'Add Custom Coin'}
                        </h3>
                        
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Coin Name *
                                </label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="Bitcoin Gold"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Symbol *
                                </label>
                                <input
                                    type="text"
                                    value={formData.symbol}
                                    onChange={(e) => setFormData({...formData, symbol: e.target.value.toUpperCase()})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="BTG"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Algorithm
                                </label>
                                <select
                                    value={formData.algorithm}
                                    onChange={(e) => setFormData({...formData, algorithm: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                >
                                    {algorithmOptions.map(algo => (
                                        <option key={algo} value={algo}>{algo}</option>
                                    ))}
                                </select>
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Block Reward
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={formData.block_reward}
                                    onChange={(e) => setFormData({...formData, block_reward: parseFloat(e.target.value)})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Block Time (seconds)
                                </label>
                                <input
                                    type="number"
                                    value={formData.block_time}
                                    onChange={(e) => setFormData({...formData, block_time: parseInt(e.target.value)})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Difficulty
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={formData.difficulty}
                                    onChange={(e) => setFormData({...formData, difficulty: parseFloat(e.target.value)})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                />
                            </div>

                            {formData.algorithm === 'Scrypt' && (
                                <>
                                    <div className="col-span-2">
                                        <h4 className="text-lg font-medium text-gray-300 mb-3">Scrypt Parameters</h4>
                                        <div className="grid grid-cols-3 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-400 mb-1">N</label>
                                                <input
                                                    type="number"
                                                    value={formData.scrypt_params.n}
                                                    onChange={(e) => setFormData({
                                                        ...formData, 
                                                        scrypt_params: {
                                                            ...formData.scrypt_params,
                                                            n: parseInt(e.target.value)
                                                        }
                                                    })}
                                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-400 mb-1">R</label>
                                                <input
                                                    type="number"
                                                    value={formData.scrypt_params.r}
                                                    onChange={(e) => setFormData({
                                                        ...formData, 
                                                        scrypt_params: {
                                                            ...formData.scrypt_params,
                                                            r: parseInt(e.target.value)
                                                        }
                                                    })}
                                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-400 mb-1">P</label>
                                                <input
                                                    type="number"
                                                    value={formData.scrypt_params.p}
                                                    onChange={(e) => setFormData({
                                                        ...formData, 
                                                        scrypt_params: {
                                                            ...formData.scrypt_params,
                                                            p: parseInt(e.target.value)
                                                        }
                                                    })}
                                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </>
                            )}
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Network Hashrate
                                </label>
                                <input
                                    type="text"
                                    value={formData.network_hashrate}
                                    onChange={(e) => setFormData({...formData, network_hashrate: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="10 MH/s"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Wallet Format
                                </label>
                                <input
                                    type="text"
                                    value={formData.wallet_format}
                                    onChange={(e) => setFormData({...formData, wallet_format: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="Standard / Legacy / Bech32"
                                />
                            </div>
                            
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Description (Optional)
                                </label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white h-20"
                                    placeholder="Notes about this custom coin..."
                                />
                            </div>
                        </div>
                        
                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={handleSave}
                                className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded-lg font-medium"
                            >
                                🪙 Save Custom Coin
                            </button>
                            <button
                                onClick={() => {
                                    setShowAddForm(false);
                                    setEditingCoin(null);
                                    resetForm();
                                }}
                                className="bg-gray-600 hover:bg-gray-700 px-6 py-2 rounded-lg font-medium"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

// Export consolidated components
export { SavedPoolsManager, CustomCoinsManager, EnterpriseThreadManager, EnterpriseDBConfig };