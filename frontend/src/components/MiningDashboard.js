import React, { useState, useEffect } from 'react';

// Consolidated Mining Dashboard Components
const MiningDashboard = ({ 
  miningStatus, 
  selectedCoin, 
  walletConfig, 
  miningConfig, 
  systemStats,
  onCoinSelect,
  onWalletConfigChange,
  onMiningStart,
  onMiningStop,
  onConfigChange 
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [collapsedSections, setCollapsedSections] = useState({
    minerSetup: false,
    miningPerformance: false,
    systemMonitoring: true
  });

  const toggleSection = (section) => {
    setCollapsedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  return (
    <div className="mining-dashboard">
      {/* Mining Control Center */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">🚀 Mining Control Center</h2>
          <div className="status-badge status-success">
            {miningStatus.is_mining ? 'MINING' : 'IDLE'}
          </div>
        </div>
        <div className="card-content">
          <MiningStatusOverview 
            miningStatus={miningStatus}
            selectedCoin={selectedCoin}
            systemStats={systemStats}
          />
          <div className="mining-controls">
            <button 
              className={`btn ${miningStatus.is_mining ? 'btn-danger' : 'btn-primary'}`}
              onClick={miningStatus.is_mining ? onMiningStop : onMiningStart}
            >
              {miningStatus.is_mining ? '⏹️ STOP MINING' : '▶️ START MINING'}
            </button>
            <QuickSettings miningConfig={miningConfig} onChange={onConfigChange} />
          </div>
        </div>
      </div>

      {/* Miner Setup Section */}
      <div className="collapsible-section">
        <button 
          className="section-toggle"
          onClick={() => toggleSection('minerSetup')}
        >
          <span>⚙️ Miner Setup</span>
          <span>{collapsedSections.minerSetup ? '▼' : '▲'}</span>
        </button>
        {!collapsedSections.minerSetup && (
          <div className="section-content">
            <div className="dashboard-grid">
              <CoinSelector 
                selectedCoin={selectedCoin}
                onCoinSelect={onCoinSelect}
              />
              <WalletConfig 
                config={walletConfig}
                onChange={onWalletConfigChange}
                selectedCoin={selectedCoin}
              />
            </div>
          </div>
        )}
      </div>

      {/* Mining Performance Section */}
      <div className="collapsible-section">
        <button 
          className="section-toggle"
          onClick={() => toggleSection('miningPerformance')}
        >
          <span>📊 Mining Performance</span>
          <span>{collapsedSections.miningPerformance ? '▼' : '▲'}</span>
        </button>
        {!collapsedSections.miningPerformance && (
          <div className="section-content">
            <MiningPerformance miningStatus={miningStatus} />
          </div>
        )}
      </div>

      {/* System Monitoring Section */}
      <div className="collapsible-section">
        <button 
          className="section-toggle"
          onClick={() => toggleSection('systemMonitoring')}
        >
          <span>🖥️ System Monitoring</span>
          <span>{collapsedSections.systemMonitoring ? '▼' : '▲'}</span>
        </button>
        {!collapsedSections.systemMonitoring && (
          <div className="section-content">
            <SystemMonitoring systemStats={systemStats} />
          </div>
        )}
      </div>
    </div>
  );
};

// Mining Status Overview Component
const MiningStatusOverview = ({ miningStatus, selectedCoin, systemStats }) => {
  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <div className="metric-value">
          {miningStatus.stats?.hashrate?.toFixed(2) || '0.00'} H/s
        </div>
        <div className="metric-label">Hash Rate</div>
      </div>
      <div className="metric-card">
        <div className="metric-value">{selectedCoin?.symbol || 'None'}</div>
        <div className="metric-label">Selected Coin</div>
      </div>
      <div className="metric-card">
        <div className="metric-value">
          {systemStats?.cpu_usage?.toFixed(1) || '0.0'}%
        </div>
        <div className="metric-label">CPU Usage</div>
      </div>
      <div className="metric-card">
        <div className="metric-value">
          {miningStatus.is_mining ? 'ACTIVE' : 'IDLE'}
        </div>
        <div className="metric-label">Mining Status</div>
      </div>
    </div>
  );
};

// Quick Settings Component
const QuickSettings = ({ miningConfig, onChange }) => {
  return (
    <div className="control-group">
      <div className="checkbox-container">
        <input 
          type="checkbox" 
          className="checkbox"
          checked={miningConfig.ai_enabled}
          onChange={(e) => onChange({ ...miningConfig, ai_enabled: e.target.checked })}
        />
        <label>AI Optimization</label>
      </div>
      <div className="checkbox-container">
        <input 
          type="checkbox" 
          className="checkbox"
          checked={miningConfig.auto_optimize}
          onChange={(e) => onChange({ ...miningConfig, auto_optimize: e.target.checked })}
        />
        <label>Auto-Optimize</label>
      </div>
    </div>
  );
};

// Coin Selector Component
const CoinSelector = ({ selectedCoin, onCoinSelect }) => {
  const [coinPresets, setCoinPresets] = useState({});

  useEffect(() => {
    fetch(`${process.env.REACT_APP_BACKEND_URL}/api/coins/presets`)
      .then(response => response.json())
      .then(data => setCoinPresets(data.presets))
      .catch(error => console.error('Failed to load coin presets:', error));
  }, []);

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">💰 Cryptocurrency Selection</h3>
      </div>
      <div className="card-content">
        <div className="coin-grid">
          {Object.entries(coinPresets).map(([key, coin]) => (
            <div 
              key={key}
              className={`coin-card ${selectedCoin?.symbol === coin.symbol ? 'selected' : ''}`}
              onClick={() => onCoinSelect(coin)}
            >
              <div className="coin-icon">{coin.symbol}</div>
              <h4>{coin.name}</h4>
              <p className="metric-label">Reward: {coin.block_reward} {coin.symbol}</p>
              <p className="metric-label">Block Time: {coin.block_time}s</p>
            </div>
          ))}
        </div>
        {selectedCoin && (
          <div className="mt-4">
            <h4>Selected: {selectedCoin.name}</h4>
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-value">{selectedCoin.algorithm}</div>
                <div className="metric-label">Algorithm</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{selectedCoin.network_hashrate}</div>
                <div className="metric-label">Network Hashrate</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Wallet Configuration Component
const WalletConfig = ({ config, onChange, selectedCoin }) => {
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionResult, setConnectionResult] = useState(null);

  const handleInputChange = (field, value) => {
    onChange({ ...config, [field]: value });
  };

  const testConnection = async () => {
    setTestingConnection(true);
    try {
      const endpoint = config.mode === 'pool' ? '/api/pool/test-connection' : '/api/pool/test-connection';
      const testData = config.mode === 'pool' 
        ? {
            pool_address: config.custom_pool_address,
            pool_port: config.custom_pool_port,
            type: 'pool'
          }
        : {
            pool_address: config.custom_rpc_host,
            pool_port: config.custom_rpc_port,
            type: 'rpc'
          };

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testData)
      });

      const result = await response.json();
      setConnectionResult(result);
    } catch (error) {
      setConnectionResult({ success: false, error: error.message });
    } finally {
      setTestingConnection(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">💼 Wallet & Pool Configuration</h3>
      </div>
      <div className="card-content">
        {/* Mining Mode Selection */}
        <div className="form-group">
          <label className="form-label">Mining Mode</label>
          <select 
            className="form-select"
            value={config.mode}
            onChange={(e) => handleInputChange('mode', e.target.value)}
          >
            <option value="pool">Pool Mining</option>
            <option value="solo">Solo Mining</option>
          </select>
        </div>

        {config.mode === 'pool' ? (
          <>
            <div className="form-group">
              <label className="form-label">Pool Username</label>
              <input 
                type="text"
                className="form-input"
                value={config.pool_username}
                onChange={(e) => handleInputChange('pool_username', e.target.value)}
                placeholder="Enter pool username or wallet address"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Pool Password</label>
              <input 
                type="text"
                className="form-input"
                value={config.pool_password}
                onChange={(e) => handleInputChange('pool_password', e.target.value)}
                placeholder="Enter pool password"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Custom Pool Address</label>
              <input 
                type="text"
                className="form-input"
                value={config.custom_pool_address}
                onChange={(e) => handleInputChange('custom_pool_address', e.target.value)}
                placeholder="stratum+tcp://pool.example.com"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Custom Pool Port</label>
              <input 
                type="number"
                className="form-input"
                value={config.custom_pool_port}
                onChange={(e) => handleInputChange('custom_pool_port', parseInt(e.target.value) || '')}
                placeholder="4444"
              />
            </div>
          </>
        ) : (
          <>
            <div className="form-group">
              <label className="form-label">Wallet Address</label>
              <input 
                type="text"
                className="form-input"
                value={config.wallet_address}
                onChange={(e) => handleInputChange('wallet_address', e.target.value)}
                placeholder={selectedCoin?.wallet_format || "Enter wallet address"}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Custom RPC Host</label>
              <input 
                type="text"
                className="form-input"
                value={config.custom_rpc_host}
                onChange={(e) => handleInputChange('custom_rpc_host', e.target.value)}
                placeholder="127.0.0.1"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Custom RPC Port</label>
              <input 
                type="number"
                className="form-input"
                value={config.custom_rpc_port}
                onChange={(e) => handleInputChange('custom_rpc_port', parseInt(e.target.value) || '')}
                placeholder="9332"
              />
            </div>
          </>
        )}

        <button 
          className="btn btn-secondary"
          onClick={testConnection}
          disabled={testingConnection}
        >
          {testingConnection ? '⏳ Testing...' : '🔍 Test Connection'}
        </button>

        {connectionResult && (
          <div className={`status-badge ${connectionResult.success ? 'status-success' : 'status-error'} mt-2`}>
            {connectionResult.success ? '✅ Connection successful' : `❌ ${connectionResult.error}`}
          </div>
        )}
      </div>
    </div>
  );
};

// Mining Performance Component
const MiningPerformance = ({ miningStatus }) => {
  const stats = miningStatus.stats || {};
  
  const getPerformanceGrade = (efficiency) => {
    if (efficiency > 50) return { grade: 'A+', color: 'status-success' };
    if (efficiency > 30) return { grade: 'A', color: 'status-success' };
    if (efficiency > 20) return { grade: 'B', color: 'status-warning' };
    if (efficiency > 10) return { grade: 'C', color: 'status-warning' };
    return { grade: 'D', color: 'status-error' };
  };

  const performance = getPerformanceGrade(stats.efficiency || 0);

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">📈 Mining Performance Analytics</h3>
        <div className={`status-badge ${performance.color}`}>
          Grade: {performance.grade}
        </div>
      </div>
      <div className="card-content">
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-value">{(stats.hashrate || 0).toFixed(2)} H/s</div>
            <div className="metric-label">Current Hashrate</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{stats.accepted_shares || 0}</div>
            <div className="metric-label">Accepted Shares</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{stats.rejected_shares || 0}</div>
            <div className="metric-label">Rejected Shares</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{(stats.efficiency || 0).toFixed(1)}</div>
            <div className="metric-label">Efficiency Score</div>
          </div>
        </div>
        
        <div className="mt-4">
          <h4>Performance Analysis</h4>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${Math.min(stats.efficiency || 0, 100)}%` }}
            ></div>
          </div>
          <p className="mt-2 text-center">
            Efficiency: {(stats.efficiency || 0).toFixed(1)}% 
            ({performance.grade} Grade)
          </p>
        </div>
      </div>
    </div>
  );
};

// System Monitoring Component  
const SystemMonitoring = ({ systemStats }) => {
  const stats = systemStats || {};
  
  const getHealthStatus = (cpu, memory) => {
    const avgUsage = (cpu + memory) / 2;
    if (avgUsage < 60) return { status: 'Optimal', color: 'status-success', score: 100 - avgUsage };
    if (avgUsage < 80) return { status: 'Good', color: 'status-warning', score: 100 - avgUsage };
    return { status: 'High Load', color: 'status-error', score: 100 - avgUsage };
  };

  const health = getHealthStatus(stats.cpu_usage || 0, stats.memory_usage || 0);

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">🖥️ System Resource Monitor</h3>
        <div className={`status-badge ${health.color}`}>
          {health.status}
        </div>
      </div>
      <div className="card-content">
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-value">{(stats.cpu_usage || 0).toFixed(1)}%</div>
            <div className="metric-label">CPU Usage</div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${stats.cpu_usage || 0}%` }}></div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{(stats.memory_usage || 0).toFixed(1)}%</div>
            <div className="metric-label">Memory Usage</div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${stats.memory_usage || 0}%` }}></div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{(stats.disk_usage || 0).toFixed(1)}%</div>
            <div className="metric-label">Disk Usage</div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${stats.disk_usage || 0}%` }}></div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{health.score.toFixed(0)}%</div>
            <div className="metric-label">System Health</div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${health.score}%` }}></div>
            </div>
          </div>
        </div>

        <div className="health-indicator">
          <span className="health-score">System Status: {health.status}</span>
          <span>Overall health score: {health.score.toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
};

export default MiningDashboard;