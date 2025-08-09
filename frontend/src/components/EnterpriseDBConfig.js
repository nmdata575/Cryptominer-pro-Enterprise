import React, { useState, useEffect } from 'react';

const EnterpriseDBConfig = ({ onConfigChange }) => {
  const [dbConfig, setDbConfig] = useState({
    useRemoteDB: false,
    remoteUrl: '',
    connectionStatus: 'Unknown',
    testingConnection: false
  });

  const [showAdvancedConfig, setShowAdvancedConfig] = useState(false);

  useEffect(() => {
    // Check current database configuration
    checkDatabaseStatus();
  }, []);

  const checkDatabaseStatus = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/health`);
      if (response.ok) {
        const data = await response.json();
        setDbConfig(prev => ({
          ...prev,
          connectionStatus: 'Connected'
        }));
      } else {
        setDbConfig(prev => ({
          ...prev,
          connectionStatus: 'Disconnected'
        }));
      }
    } catch (error) {
      console.error('Database status check failed:', error);
      setDbConfig(prev => ({
        ...prev,
        connectionStatus: 'Error'
      }));
    }
  };

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

export default EnterpriseDBConfig;