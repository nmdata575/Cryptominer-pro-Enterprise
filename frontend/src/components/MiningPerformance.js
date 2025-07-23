import React from 'react';

const MiningPerformance = ({ miningStatus, selectedCoin, coinPresets }) => {
  const currentCoin = coinPresets && selectedCoin ? coinPresets[selectedCoin] : null;
  const stats = miningStatus?.stats || {};

  const formatHashRate = (hashRate) => {
    if (!hashRate) return '0.00 H/s';
    if (hashRate >= 1000000) return `${(hashRate / 1000000).toFixed(2)} MH/s`;
    if (hashRate >= 1000) return `${(hashRate / 1000).toFixed(2)} KH/s`;
    return `${hashRate.toFixed(2)} H/s`;
  };

  const calculateEfficiency = () => {
    if (!stats.hashrate || !stats.power_consumption) return 0;
    return (stats.hashrate / stats.power_consumption).toFixed(2);
  };

  const getPerformanceGrade = () => {
    if (!miningStatus.is_mining) return { grade: 'N/A', color: 'text-gray-400' };
    
    const hashRate = stats.hashrate || 0;
    const rejectionRate = stats.rejected_shares / (stats.accepted_shares + stats.rejected_shares + 1) * 100;
    
    if (hashRate > 100 && rejectionRate < 5) return { grade: 'A+', color: 'text-crypto-green' };
    if (hashRate > 50 && rejectionRate < 10) return { grade: 'A', color: 'text-crypto-green' };
    if (hashRate > 20 && rejectionRate < 15) return { grade: 'B+', color: 'text-crypto-gold' };
    if (hashRate > 10 && rejectionRate < 20) return { grade: 'B', color: 'text-crypto-gold' };
    return { grade: 'C', color: 'text-crypto-red' };
  };

  const MetricCard = ({ title, value, unit, icon, color = 'text-white', bgColor = 'from-gray-800 to-gray-900' }) => (
    <div className={`metric-card bg-gradient-to-br ${bgColor} p-4 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className={`p-2 ${color.replace('text-', 'bg-').replace('-400', '-500/20')} rounded-lg`}>
            {icon}
          </div>
          <span className="text-sm font-medium text-gray-300">{title}</span>
        </div>
      </div>
      <div className={`text-2xl font-bold ${color} mb-1`}>
        {value}
      </div>
      {unit && <div className="text-xs text-gray-400">{unit}</div>}
    </div>
  );

  const performance = getPerformanceGrade();

  return (
    <div className="space-y-6">
      {/* Mining Status Banner */}
      {miningStatus.is_mining ? (
        <div className="status-banner bg-gradient-to-r from-crypto-green/20 to-green-600/20 p-4 rounded-lg border border-crypto-green/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-crypto-green rounded-full animate-pulse"></div>
                <span className="font-bold text-crypto-green">MINING ACTIVE</span>
              </div>
              {currentCoin && (
                <div className="flex items-center space-x-2">
                  <span className="text-gray-400">Mining:</span>
                  <span className="font-medium text-crypto-gold">{currentCoin.name}</span>
                </div>
              )}
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400">Performance Grade</div>
              <div className={`text-xl font-bold ${performance.color}`}>{performance.grade}</div>
            </div>
          </div>
        </div>
      ) : (
        <div className="status-banner bg-gradient-to-r from-gray-700/20 to-gray-800/20 p-4 rounded-lg border border-gray-600/30">
          <div className="flex items-center justify-center space-x-2">
            <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
            <span className="font-bold text-gray-400">MINING STOPPED</span>
          </div>
        </div>
      )}

      {/* Primary Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Hash Rate"
          value={formatHashRate(stats.hashrate)}
          icon={
            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          }
          color="text-blue-400"
          bgColor="from-blue-500/10 to-blue-600/10"
        />

        <MetricCard
          title="Accepted Shares"
          value={stats.accepted_shares || 0}
          unit="shares"
          icon={
            <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          color="text-green-400"
          bgColor="from-green-500/10 to-green-600/10"
        />

        <MetricCard
          title="Rejected Shares"
          value={stats.rejected_shares || 0}
          unit="shares"
          icon={
            <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          color="text-red-400"
          bgColor="from-red-500/10 to-red-600/10"
        />

        <MetricCard
          title="Blocks Found"
          value={stats.blocks_found || 0}
          unit="blocks"
          icon={
            <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          }
          color="text-yellow-400"
          bgColor="from-yellow-500/10 to-yellow-600/10"
        />
      </div>

      {/* Detailed Performance Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mining Statistics */}
        <div className="performance-panel bg-gradient-to-br from-gray-800 to-gray-900 p-5 rounded-lg border border-gray-700">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-crypto-blue/20 rounded-lg">
              <svg className="w-6 h-6 text-crypto-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Mining Statistics</h3>
              <p className="text-sm text-gray-400">Performance metrics and ratios</p>
            </div>
          </div>

          <div className="space-y-4">
            {miningStatus.is_mining ? (
              <>
                <div className="stat-row flex justify-between items-center py-2 border-b border-gray-700">
                  <span className="text-gray-400">Share Acceptance Rate</span>
                  <span className="text-crypto-green font-medium">
                    {stats.accepted_shares || stats.rejected_shares ? 
                      ((stats.accepted_shares / (stats.accepted_shares + stats.rejected_shares)) * 100).toFixed(1) : 0}%
                  </span>
                </div>
                
                <div className="stat-row flex justify-between items-center py-2 border-b border-gray-700">
                  <span className="text-gray-400">Average Hash Rate</span>
                  <span className="text-crypto-blue font-medium">{formatHashRate(stats.avg_hashrate || stats.hashrate)}</span>
                </div>
                
                <div className="stat-row flex justify-between items-center py-2 border-b border-gray-700">
                  <span className="text-gray-400">Mining Efficiency</span>
                  <span className="text-crypto-gold font-medium">{stats.efficiency?.toFixed(1) || '0.0'}%</span>
                </div>
                
                <div className="stat-row flex justify-between items-center py-2 border-b border-gray-700">
                  <span className="text-gray-400">Uptime</span>
                  <span className="text-white font-medium">{stats.uptime || 'N/A'}</span>
                </div>

                <div className="stat-row flex justify-between items-center py-2">
                  <span className="text-gray-400">Total Shares</span>
                  <span className="text-white font-medium">{(stats.accepted_shares || 0) + (stats.rejected_shares || 0)}</span>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <div className="text-gray-500 mb-2">
                  <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2-2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <p className="text-gray-400">No mining statistics available</p>
                <p className="text-sm text-gray-500 mt-1">Start mining to see performance data</p>
              </div>
            )}
          </div>
        </div>

        {/* Performance Trends */}
        <div className="performance-panel bg-gradient-to-br from-gray-800 to-gray-900 p-5 rounded-lg border border-gray-700">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Performance Analysis</h3>
              <p className="text-sm text-gray-400">Mining efficiency insights</p>
            </div>
          </div>

          <div className="space-y-4">
            {miningStatus.is_mining ? (
              <>
                {/* Performance Grade */}
                <div className="performance-grade bg-gray-700/50 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-400">Overall Grade</span>
                    <span className={`text-2xl font-bold ${performance.color}`}>{performance.grade}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    Based on hash rate performance and share acceptance
                  </div>
                </div>

                {/* Efficiency Indicators */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="efficiency-metric bg-gray-700/30 p-3 rounded-lg text-center">
                    <div className="text-lg font-bold text-crypto-gold">
                      {stats.efficiency ? `${stats.efficiency.toFixed(1)}%` : 'N/A'}
                    </div>
                    <div className="text-xs text-gray-400">Hash Efficiency</div>
                  </div>
                  <div className="efficiency-metric bg-gray-700/30 p-3 rounded-lg text-center">
                    <div className="text-lg font-bold text-crypto-blue">
                      {stats.hashrate ? `${(stats.hashrate * 3600).toFixed(0)}` : '0'}
                    </div>
                    <div className="text-xs text-gray-400">Hashes/Hour</div>
                  </div>
                </div>

                {/* Performance Tips */}
                <div className="performance-tips bg-crypto-gold/10 p-3 rounded-lg border border-crypto-gold/20">
                  <div className="text-sm font-medium text-crypto-gold mb-2">💡 Performance Tips</div>
                  <ul className="text-xs text-crypto-gold/80 space-y-1">
                    {stats.accepted_shares < 10 && <li>• Keep mining to build share statistics</li>}
                    {(stats.rejected_shares / (stats.accepted_shares + 1)) > 0.1 && <li>• High rejection rate - check network connection</li>}
                    {stats.hashrate && stats.hashrate < 1 && <li>• Low hash rate - consider increasing thread count</li>}
                    <li>• Monitor system temperature during extended mining</li>
                  </ul>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <div className="text-gray-500 mb-2">
                  <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                  </svg>
                </div>
                <p className="text-gray-400">No performance data available</p>
                <p className="text-sm text-gray-500 mt-1">Start mining to see analysis</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mining History Summary */}
      {miningStatus.is_mining && (
        <div className="mining-history bg-gradient-to-r from-crypto-accent/10 to-crypto-blue/10 p-5 rounded-lg border border-crypto-accent/20">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-crypto-accent/20 rounded-lg">
              <svg className="w-6 h-6 text-crypto-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Session Summary</h3>
              <p className="text-sm text-gray-400">Current mining session overview</p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-xl font-bold text-crypto-blue">{formatHashRate(stats.hashrate)}</div>
              <div className="text-xs text-gray-400">Current Rate</div>
            </div>
            <div>
              <div className="text-xl font-bold text-crypto-green">{stats.accepted_shares || 0}</div>
              <div className="text-xs text-gray-400">Valid Shares</div>
            </div>
            <div>
              <div className="text-xl font-bold text-crypto-gold">{stats.blocks_found || 0}</div>
              <div className="text-xs text-gray-400">Blocks Found</div>
            </div>
            <div>
              <div className="text-xl font-bold text-crypto-accent">{performance.grade}</div>
              <div className="text-xs text-gray-400">Grade</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MiningPerformance;