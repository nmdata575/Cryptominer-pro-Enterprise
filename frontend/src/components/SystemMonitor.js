import React, { useState, useEffect } from 'react';

const SystemMonitor = ({ stats }) => {
  const [cpuHistory, setCpuHistory] = useState([]);
  const [memoryHistory, setMemoryHistory] = useState([]);

  useEffect(() => {
    if (stats?.cpu?.usage_percent !== undefined) {
      setCpuHistory(prev => {
        const newHistory = [...prev, {
          timestamp: Date.now(),
          value: stats.cpu.usage_percent
        }];
        return newHistory.slice(-20); // Keep last 20 data points
      });
    }
  }, [stats?.cpu?.usage_percent]);

  useEffect(() => {
    if (stats?.memory?.percent !== undefined) {
      setMemoryHistory(prev => {
        const newHistory = [...prev, {
          timestamp: Date.now(),
          value: stats.memory.percent
        }];
        return newHistory.slice(-20); // Keep last 20 data points
      });
    }
  }, [stats?.memory?.percent]);

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getUsageColor = (percentage) => {
    if (percentage >= 90) return 'text-crypto-red';
    if (percentage >= 70) return 'text-crypto-gold';
    return 'text-crypto-green';
  };

  const getUsageBarColor = (percentage) => {
    if (percentage >= 90) return 'bg-crypto-red';
    if (percentage >= 70) return 'bg-crypto-gold';
    return 'bg-crypto-green';
  };

  const renderMiniChart = (data, color = 'crypto-gold') => {
    if (data.length < 2) return null;
    
    const maxValue = Math.max(...data.map(d => d.value), 1);
    
    return (
      <div className="flex items-end space-x-0.5 h-8">
        {data.map((point, index) => {
          const height = (point.value / maxValue) * 100;
          return (
            <div
              key={index}
              className={`flex-1 bg-${color} rounded-t opacity-70`}
              style={{ height: `${Math.max(2, height)}%` }}
            ></div>
          );
        })}
      </div>
    );
  };

  if (!stats) {
    return (
      <div className="mining-card">
        <h3 className="text-xl font-bold text-white mb-4">System Monitor</h3>
        <div className="text-center text-gray-400 py-8">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p>Loading system stats...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mining-card">
      <h3 className="text-xl font-bold text-white mb-4">System Monitor</h3>
      
      {/* CPU Usage */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-white">🔧 CPU Usage</span>
          <span className={`text-sm font-bold ${getUsageColor(stats.cpu?.usage_percent || 0)}`}>
            {(stats.cpu?.usage_percent || 0).toFixed(1)}%
          </span>
        </div>
        
        <div className="progress-bar mb-2">
          <div 
            className={`progress-fill ${getUsageBarColor(stats.cpu?.usage_percent || 0)}`}
            style={{ width: `${Math.min(100, stats.cpu?.usage_percent || 0)}%` }}
          ></div>
        </div>
        
        <div className="mb-2">
          {renderMiniChart(cpuHistory, 'crypto-blue')}
        </div>
        
        <div className="text-xs text-gray-400 space-y-1">
          {stats.cpu?.count && (
            <div>Cores: {stats.cpu.count}</div>
          )}
          {stats.cpu?.freq?.current && (
            <div>Frequency: {(stats.cpu.freq.current / 1000).toFixed(2)} GHz</div>
          )}
        </div>
      </div>

      {/* Memory Usage */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-white">💾 Memory Usage</span>
          <span className={`text-sm font-bold ${getUsageColor(stats.memory?.percent || 0)}`}>
            {(stats.memory?.percent || 0).toFixed(1)}%
          </span>
        </div>
        
        <div className="progress-bar mb-2">
          <div 
            className={`progress-fill ${getUsageBarColor(stats.memory?.percent || 0)}`}
            style={{ width: `${Math.min(100, stats.memory?.percent || 0)}%` }}
          ></div>
        </div>
        
        <div className="mb-2">
          {renderMiniChart(memoryHistory, 'crypto-accent')}
        </div>
        
        <div className="text-xs text-gray-400 space-y-1">
          <div className="flex justify-between">
            <span>Used:</span>
            <span>{formatBytes(stats.memory?.used)}</span>
          </div>
          <div className="flex justify-between">
            <span>Available:</span>
            <span>{formatBytes(stats.memory?.available)}</span>
          </div>
          <div className="flex justify-between">
            <span>Total:</span>
            <span>{formatBytes(stats.memory?.total)}</span>
          </div>
        </div>
      </div>

      {/* Disk Usage */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-white">💿 Disk Usage</span>
          <span className={`text-sm font-bold ${getUsageColor(stats.disk?.percent || 0)}`}>
            {(stats.disk?.percent || 0).toFixed(1)}%
          </span>
        </div>
        
        <div className="progress-bar mb-2">
          <div 
            className={`progress-fill ${getUsageBarColor(stats.disk?.percent || 0)}`}
            style={{ width: `${Math.min(100, stats.disk?.percent || 0)}%` }}
          ></div>
        </div>
        
        <div className="text-xs text-gray-400 space-y-1">
          <div className="flex justify-between">
            <span>Used:</span>
            <span>{formatBytes(stats.disk?.used)}</span>
          </div>
          <div className="flex justify-between">
            <span>Free:</span>
            <span>{formatBytes(stats.disk?.free)}</span>
          </div>
          <div className="flex justify-between">
            <span>Total:</span>
            <span>{formatBytes(stats.disk?.total)}</span>
          </div>
        </div>
      </div>

      {/* System Health Score */}
      <div className="bg-crypto-accent/20 rounded-lg p-3">
        <div className="text-sm font-medium text-white mb-2">
          🏥 System Health
        </div>
        
        <div className="space-y-2">
          {/* Overall Health Score */}
          {(() => {
            const cpuScore = Math.max(0, 100 - (stats.cpu?.usage_percent || 0));
            const memoryScore = Math.max(0, 100 - (stats.memory?.percent || 0));
            const diskScore = Math.max(0, 100 - (stats.disk?.percent || 0));
            const overallScore = (cpuScore + memoryScore + diskScore) / 3;
            
            return (
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-300">Overall:</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-crypto-accent/30 rounded-full h-1">
                    <div 
                      className={`h-full rounded-full ${
                        overallScore >= 70 ? 'bg-crypto-green' : 
                        overallScore >= 40 ? 'bg-crypto-gold' : 'bg-crypto-red'
                      }`}
                      style={{ width: `${overallScore}%` }}
                    ></div>
                  </div>
                  <span className={`text-xs font-medium ${
                    overallScore >= 70 ? 'text-crypto-green' : 
                    overallScore >= 40 ? 'text-crypto-gold' : 'text-crypto-red'
                  }`}>
                    {overallScore.toFixed(0)}%
                  </span>
                </div>
              </div>
            );
          })()}
          
          {/* Status Messages */}
          <div className="text-xs text-gray-400">
            {stats.cpu?.usage_percent > 90 && (
              <div className="text-crypto-red">⚠️ High CPU usage detected</div>
            )}
            {stats.memory?.percent > 90 && (
              <div className="text-crypto-red">⚠️ Low memory available</div>
            )}
            {stats.disk?.percent > 90 && (
              <div className="text-crypto-red">⚠️ Disk space running low</div>
            )}
            {stats.cpu?.usage_percent <= 50 && stats.memory?.percent <= 50 && (
              <div className="text-crypto-green">✅ System running optimally</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemMonitor;