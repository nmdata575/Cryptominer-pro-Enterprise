import React, { useState, useEffect } from 'react';

const MiningDashboard = ({ stats, isMining, config }) => {
  const [hashHistory, setHashHistory] = useState([]);

  useEffect(() => {
    if (stats.hashrate !== undefined) {
      setHashHistory(prev => {
        const newHistory = [...prev, {
          timestamp: Date.now(),
          hashrate: stats.hashrate,
          efficiency: stats.efficiency
        }];
        // Keep only last 50 data points
        return newHistory.slice(-50);
      });
    }
  }, [stats.hashrate]);

  const formatHashrate = (hashrate) => {
    if (hashrate >= 1000000000) return `${(hashrate / 1000000000).toFixed(2)} GH/s`;
    if (hashrate >= 1000000) return `${(hashrate / 1000000).toFixed(2)} MH/s`;
    if (hashrate >= 1000) return `${(hashrate / 1000).toFixed(2)} KH/s`;
    return `${hashrate.toFixed(2)} H/s`;
  };

  const formatUptime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getEfficiencyColor = (efficiency) => {
    if (efficiency >= 90) return 'text-crypto-green';
    if (efficiency >= 70) return 'text-crypto-gold';
    return 'text-crypto-red';
  };

  return (
    <div className="space-y-6">
      {/* Main Mining Status */}
      <div className="mining-card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Mining Dashboard</h2>
          <div className={`status-indicator ${isMining ? 'mining' : 'stopped'}`}>
            <div className={`w-3 h-3 rounded-full ${isMining ? 'bg-crypto-green animate-pulse' : 'bg-gray-400'}`}></div>
            <span>{isMining ? 'Mining Active' : 'Mining Stopped'}</span>
          </div>
        </div>

        {/* Current Hash Rate */}
        <div className="text-center mb-8">
          <div className="hashrate-display mb-2">
            {formatHashrate(stats.hashrate || 0)}
          </div>
          <p className="text-gray-300 text-sm">Current Hash Rate</p>
        </div>

        {/* Mining Statistics Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="stat-card text-center">
            <div className="text-2xl font-bold text-crypto-green mb-1">
              {stats.accepted_shares || 0}
            </div>
            <div className="text-xs text-gray-300">Accepted Shares</div>
          </div>
          
          <div className="stat-card text-center">
            <div className="text-2xl font-bold text-crypto-red mb-1">
              {stats.rejected_shares || 0}
            </div>
            <div className="text-xs text-gray-300">Rejected Shares</div>
          </div>
          
          <div className="stat-card text-center">
            <div className="text-2xl font-bold text-crypto-gold mb-1">
              {stats.blocks_found || 0}
            </div>
            <div className="text-xs text-gray-300">Blocks Found</div>
          </div>
          
          <div className="stat-card text-center">
            <div className={`text-2xl font-bold mb-1 ${getEfficiencyColor(stats.efficiency || 0)}`}>
              {(stats.efficiency || 0).toFixed(1)}%
            </div>
            <div className="text-xs text-gray-300">Efficiency</div>
          </div>
        </div>

        {/* Hash Rate Trend */}
        <div className="chart-container">
          <h3 className="text-lg font-semibold text-white mb-4">Hash Rate Trend</h3>
          <div className="h-32 flex items-end space-x-1">
            {hashHistory.map((point, index) => {
              const maxHashrate = Math.max(...hashHistory.map(p => p.hashrate), 1);
              const height = (point.hashrate / maxHashrate) * 100;
              
              return (
                <div
                  key={index}
                  className="flex-1 bg-gradient-to-t from-crypto-gold to-yellow-400 rounded-t transition-all duration-300"
                  style={{ height: `${height}%`, minHeight: '4px' }}
                  title={`${formatHashrate(point.hashrate)} at ${new Date(point.timestamp).toLocaleTimeString()}`}
                ></div>
              );
            })}
          </div>
        </div>

        {/* Mining Details */}
        {config && (
          <div className="mt-6 p-4 bg-crypto-accent/20 rounded-lg">
            <h3 className="text-lg font-semibold text-white mb-3">Current Configuration</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-300">Coin:</span>
                <span className="ml-2 text-white font-medium">{config.coin?.name || 'Not specified'}</span>
              </div>
              <div>
                <span className="text-gray-300">Mode:</span>
                <span className="ml-2 text-white font-medium capitalize">{config.mode || 'Solo'}</span>
              </div>
              <div>
                <span className="text-gray-300">Threads:</span>
                <span className="ml-2 text-white font-medium">{config.threads || 'N/A'}</span>
              </div>
              <div>
                <span className="text-gray-300">Intensity:</span>
                <span className="ml-2 text-white font-medium">{((config.intensity || 1) * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>
        )}

        {/* Uptime */}
        {isMining && (
          <div className="mt-4 text-center">
            <div className="text-crypto-gold font-mono text-lg">
              ⏱️ {formatUptime(stats.uptime || 0)}
            </div>
            <p className="text-gray-300 text-xs">Mining Uptime</p>
          </div>
        )}
      </div>

      {/* Share Statistics */}
      <div className="mining-card">
        <h3 className="text-xl font-bold text-white mb-4">Share Statistics</h3>
        
        <div className="space-y-4">
          {/* Accepted Shares Progress */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-300">Accepted Shares</span>
              <span className="text-sm font-medium text-crypto-green">
                {stats.accepted_shares || 0}
              </span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill bg-crypto-green"
                style={{ 
                  width: `${Math.min(100, ((stats.accepted_shares || 0) / Math.max(1, (stats.accepted_shares || 0) + (stats.rejected_shares || 0))) * 100)}%` 
                }}
              ></div>
            </div>
          </div>

          {/* Efficiency Meter */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-300">Mining Efficiency</span>
              <span className={`text-sm font-medium ${getEfficiencyColor(stats.efficiency || 0)}`}>
                {(stats.efficiency || 0).toFixed(1)}%
              </span>
            </div>
            <div className="progress-bar">
              <div 
                className={`progress-fill ${
                  (stats.efficiency || 0) >= 90 ? 'bg-crypto-green' : 
                  (stats.efficiency || 0) >= 70 ? 'bg-crypto-gold' : 'bg-crypto-red'
                }`}
                style={{ width: `${Math.min(100, stats.efficiency || 0)}%` }}
              ></div>
            </div>
          </div>

          {/* Blocks Found */}
          {stats.blocks_found > 0 && (
            <div className="bg-crypto-gold/20 border border-crypto-gold/30 rounded-lg p-3">
              <div className="flex items-center space-x-2">
                <span className="text-crypto-gold text-xl">🏆</span>
                <div>
                  <div className="text-crypto-gold font-semibold">
                    {stats.blocks_found} Block{stats.blocks_found !== 1 ? 's' : ''} Found!
                  </div>
                  <div className="text-crypto-gold/80 text-xs">
                    Congratulations on your mining success!
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MiningDashboard;