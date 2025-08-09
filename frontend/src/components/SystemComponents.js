import React, { useState, useEffect } from 'react';

// Consolidated System Components
const SystemComponents = ({ miningConfig, onConfigChange, systemStats }) => {
  return (
    <div className="system-components">
      <MiningControls 
        config={miningConfig}
        onChange={onConfigChange}
        systemStats={systemStats}
      />
    </div>
  );
};

// Mining Controls Component
const MiningControls = ({ config, onChange, systemStats }) => {
  const [cpuInfo, setCpuInfo] = useState(null);
  const [threadProfiles, setThreadProfiles] = useState({});

  useEffect(() => {
    // Fetch CPU information for thread optimization
    fetch(`${process.env.REACT_APP_BACKEND_URL}/api/system/cpu-info`)
      .then(response => response.json())
      .then(data => {
        setCpuInfo(data);
        setThreadProfiles(data.thread_profiles || {});
      })
      .catch(error => console.error('Failed to load CPU info:', error));
  }, []);

  const handleConfigChange = (field, value) => {
    onChange({ ...config, [field]: value });
  };

  const selectProfile = (profile) => {
    const threads = threadProfiles[profile] || config.threads;
    onChange({ 
      ...config, 
      thread_profile: profile,
      threads: threads,
      auto_thread_detection: true 
    });
  };

  const getProfileDescription = (profile) => {
    const descriptions = {
      light: `Light Mining (${threadProfiles.light || 'N/A'} threads) - Minimal system impact`,
      standard: `Standard Mining (${threadProfiles.standard || 'N/A'} threads) - Balanced performance`,
      maximum: `Maximum Mining (${threadProfiles.maximum || 'N/A'} threads) - Full system utilization`
    };
    return descriptions[profile] || profile;
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">⚙️ Mining Controls</h3>
        <div className="status-badge status-success">
          {config.threads} Threads Active
        </div>
      </div>
      <div className="card-content">
        {/* System Information */}
        {cpuInfo && (
          <div className="mb-4">
            <h4>System Information</h4>
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-value">{cpuInfo.total_cores}</div>
                <div className="metric-label">Total Cores</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{cpuInfo.physical_cores}</div>
                <div className="metric-label">Physical Cores</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{(cpuInfo.average_usage || 0).toFixed(1)}%</div>
                <div className="metric-label">CPU Usage</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{cpuInfo.recommended_threads}</div>
                <div className="metric-label">Recommended</div>
              </div>
            </div>
          </div>
        )}

        {/* Mining Profile Selection */}
        <div className="form-group">
          <label className="form-label">Mining Profile</label>
          <div className="profile-selector">
            {['light', 'standard', 'maximum'].map(profile => (
              <div 
                key={profile}
                className={`profile-option ${config.thread_profile === profile ? 'selected' : ''}`}
                onClick={() => selectProfile(profile)}
              >
                <strong>{profile.charAt(0).toUpperCase() + profile.slice(1)}</strong>
                <p className="text-sm mt-1">{threadProfiles[profile] || 'N/A'} threads</p>
              </div>
            ))}
          </div>
          <p className="text-sm text-gray-400 mt-2">
            {getProfileDescription(config.thread_profile || 'standard')}
          </p>
        </div>

        {/* Thread Count Control */}
        <div className="mining-controls">
          <div className="control-group">
            <label className="control-label">Thread Count: {config.threads}</label>
            <input 
              type="range"
              className="slider"
              min="1"
              max={cpuInfo?.total_cores || 8}
              value={config.threads}
              onChange={(e) => handleConfigChange('threads', parseInt(e.target.value))}
            />
            <div className="flex justify-between text-sm text-gray-400">
              <span>1</span>
              <span>{cpuInfo?.total_cores || 8}</span>
            </div>
          </div>

          <div className="control-group">
            <label className="control-label">Mining Intensity: {(config.intensity * 100).toFixed(0)}%</label>
            <input 
              type="range"
              className="slider"
              min="0.1"
              max="1"
              step="0.1"
              value={config.intensity}
              onChange={(e) => handleConfigChange('intensity', parseFloat(e.target.value))}
            />
            <div className="flex justify-between text-sm text-gray-400">
              <span>10%</span>
              <span>100%</span>
            </div>
          </div>
        </div>

        {/* AI and Optimization Settings */}
        <div className="mt-4">
          <h4>AI & Optimization</h4>
          <div className="space-y-2">
            <div className="checkbox-container">
              <input 
                type="checkbox" 
                className="checkbox"
                checked={config.ai_enabled}
                onChange={(e) => handleConfigChange('ai_enabled', e.target.checked)}
              />
              <label>Enable AI Optimization</label>
            </div>
            <div className="checkbox-container">
              <input 
                type="checkbox" 
                className="checkbox"
                checked={config.auto_optimize}
                onChange={(e) => handleConfigChange('auto_optimize', e.target.checked)}
              />
              <label>Enable Auto-Optimization</label>
            </div>
            <div className="checkbox-container">
              <input 
                type="checkbox" 
                className="checkbox"
                checked={config.auto_thread_detection}
                onChange={(e) => handleConfigChange('auto_thread_detection', e.target.checked)}
              />
              <label>Auto Thread Detection</label>
            </div>
          </div>
        </div>

        {/* Performance Recommendations */}
        {systemStats && (
          <div className="mt-4">
            <h4>Performance Recommendations</h4>
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3">
              <PerformanceRecommendations 
                systemStats={systemStats}
                currentConfig={config}
                cpuInfo={cpuInfo}
              />
            </div>
          </div>
        )}

        {/* Current Performance Metrics */}
        <div className="mt-4">
          <h4>Current Performance</h4>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-value">{config.threads}</div>
              <div className="metric-label">Active Threads</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{(config.intensity * 100).toFixed(0)}%</div>
              <div className="metric-label">Mining Intensity</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{systemStats?.cpu_usage?.toFixed(1) || '0.0'}%</div>
              <div className="metric-label">CPU Usage</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{systemStats?.memory_usage?.toFixed(1) || '0.0'}%</div>
              <div className="metric-label">Memory Usage</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Performance Recommendations Component
const PerformanceRecommendations = ({ systemStats, currentConfig, cpuInfo }) => {
  const generateRecommendations = () => {
    const recommendations = [];
    const cpuUsage = systemStats?.cpu_usage || 0;
    const memoryUsage = systemStats?.memory_usage || 0;

    // CPU recommendations
    if (cpuUsage > 95) {
      recommendations.push({
        type: 'warning',
        message: 'CPU usage is very high. Consider reducing thread count.'
      });
    } else if (cpuUsage < 50 && currentConfig.threads < (cpuInfo?.total_cores || 4)) {
      recommendations.push({
        type: 'suggestion',
        message: 'CPU usage is low. You can increase thread count for better performance.'
      });
    }

    // Memory recommendations
    if (memoryUsage > 90) {
      recommendations.push({
        type: 'warning',
        message: 'Memory usage is critical. Consider reducing mining intensity.'
      });
    }

    // Thread recommendations
    if (currentConfig.threads === 1 && (cpuInfo?.total_cores || 1) > 2) {
      recommendations.push({
        type: 'suggestion',
        message: 'Using only 1 thread. Consider using Standard or Maximum profile.'
      });
    }

    // AI recommendations
    if (!currentConfig.ai_enabled) {
      recommendations.push({
        type: 'info',
        message: 'AI optimization is disabled. Enable it for better performance tuning.'
      });
    }

    // Default recommendation if system is optimal
    if (recommendations.length === 0) {
      recommendations.push({
        type: 'success',
        message: 'System is performing optimally with current settings.'
      });
    }

    return recommendations;
  };

  const recommendations = generateRecommendations();

  const getRecommendationIcon = (type) => {
    switch (type) {
      case 'warning': return '⚠️';
      case 'suggestion': return '💡';
      case 'info': return 'ℹ️';
      case 'success': return '✅';
      default: return '📝';
    }
  };

  return (
    <div className="recommendations">
      {recommendations.map((rec, index) => (
        <div key={index} className="flex items-start gap-2 mb-2 last:mb-0">
          <span className="text-lg">{getRecommendationIcon(rec.type)}</span>
          <p className="text-sm">{rec.message}</p>
        </div>
      ))}
    </div>
  );
};

export default SystemComponents;