import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SystemMonitoring = ({ systemMetrics }) => {
  const [cpuInfo, setCpuInfo] = useState(null);
  const [loadingCpuInfo, setLoadingCpuInfo] = useState(true);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchCpuInfo();
  }, []);

  const fetchCpuInfo = async () => {
    try {
      setLoadingCpuInfo(true);
      const response = await axios.get(`${BACKEND_URL}/api/system/cpu-info`);
      setCpuInfo(response.data);
    } catch (error) {
      console.error('Failed to fetch CPU info:', error);
    } finally {
      setLoadingCpuInfo(false);
    }
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  const getHealthStatus = (percentage) => {
    if (percentage < 50) return { color: 'text-crypto-green', bg: 'bg-crypto-green', status: 'Good' };
    if (percentage < 80) return { color: 'text-crypto-gold', bg: 'bg-crypto-gold', status: 'Moderate' };
    return { color: 'text-crypto-red', bg: 'bg-crypto-red', status: 'High' };
  };

  const ResourceMeter = ({ label, value, unit = '%', maxValue = 100 }) => {
    const health = getHealthStatus(value);
    const percentage = Math.min((value / maxValue) * 100, 100);

    return (
      <div className="resource-meter">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-300">{label}</span>
          <span className={`text-sm font-bold ${health.color}`}>
            {value.toFixed(1)}{unit}
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2.5">
          <div 
            className={`h-2.5 rounded-full transition-all duration-500 ${health.bg}`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>0{unit}</span>
          <span className={health.color}>{health.status}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* System Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* CPU Usage */}
        <div className="metric-card bg-gradient-to-br from-blue-500/10 to-blue-600/10 p-4 rounded-lg border border-blue-500/20">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
              </div>
              <span className="text-sm font-medium text-gray-300">CPU Usage</span>
            </div>
          </div>
          <div className="text-2xl font-bold text-blue-400 mb-1">
            {systemMetrics?.cpu?.usage_percent?.toFixed(1) || '0.0'}%
          </div>
          <div className="text-xs text-gray-400">
            {cpuInfo ? `${cpuInfo.cores.physical} cores` : 'Loading...'}
          </div>
        </div>

        {/* Memory Usage */}
        <div className="metric-card bg-gradient-to-br from-green-500/10 to-green-600/10 p-4 rounded-lg border border-green-500/20">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                </svg>
              </div>
              <span className="text-sm font-medium text-gray-300">Memory</span>
            </div>
          </div>
          <div className="text-2xl font-bold text-green-400 mb-1">
            {systemMetrics?.memory?.percent?.toFixed(1) || '0.0'}%
          </div>
          <div className="text-xs text-gray-400">
            {systemMetrics ? `${formatBytes(systemMetrics.memory.used)} / ${formatBytes(systemMetrics.memory.total)}` : 'Loading...'}
          </div>
        </div>

        {/* Disk Usage */}
        <div className="metric-card bg-gradient-to-br from-purple-500/10 to-purple-600/10 p-4 rounded-lg border border-purple-500/20">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <span className="text-sm font-medium text-gray-300">Disk</span>
            </div>
          </div>
          <div className="text-2xl font-bold text-purple-400 mb-1">
            {systemMetrics?.disk?.percent?.toFixed(1) || '0.0'}%
          </div>
          <div className="text-xs text-gray-400">
            {systemMetrics ? `${formatBytes(systemMetrics.disk.used)} / ${formatBytes(systemMetrics.disk.total)}` : 'Loading...'}
          </div>
        </div>

        {/* System Health */}
        <div className="metric-card bg-gradient-to-br from-orange-500/10 to-orange-600/10 p-4 rounded-lg border border-orange-500/20">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-orange-500/20 rounded-lg">
                <svg className="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-sm font-medium text-gray-300">Health</span>
            </div>
          </div>
          <div className="text-lg font-bold text-orange-400 mb-1">
            {systemMetrics?.cpu?.usage_percent < 90 && systemMetrics?.memory?.percent < 90 ? 'HEALTHY' : 'STRESSED'}
          </div>
          <div className="text-xs text-gray-400">System Status</div>
        </div>
      </div>

      {/* Detailed Resource Monitoring */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CPU Details */}
        <div className="resource-panel bg-gradient-to-br from-gray-800 to-gray-900 p-5 rounded-lg border border-gray-700">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">CPU Monitoring</h3>
              <p className="text-sm text-gray-400">Processor performance metrics</p>
            </div>
          </div>

          <div className="space-y-4">
            <ResourceMeter 
              label="CPU Usage" 
              value={systemMetrics?.cpu?.usage_percent || 0} 
            />
            
            {cpuInfo && (
              <>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Physical Cores:</span>
                    <span className="text-white font-medium ml-2">{cpuInfo.cores.physical}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Logical Cores:</span>
                    <span className="text-white font-medium ml-2">{cpuInfo.cores.logical}</span>
                  </div>
                  {cpuInfo.frequency?.max && (
                    <>
                      <div>
                        <span className="text-gray-400">Max Frequency:</span>
                        <span className="text-white font-medium ml-2">{Math.round(cpuInfo.frequency.max)} MHz</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Current:</span>
                        <span className="text-white font-medium ml-2">
                          {cpuInfo.frequency.current ? Math.round(cpuInfo.frequency.current) + ' MHz' : 'Variable'}
                        </span>
                      </div>
                    </>
                  )}
                </div>

                {/* Per-Core Usage */}
                {cpuInfo.load?.per_core && (
                  <div className="mt-4">
                    <div className="text-sm font-medium text-gray-300 mb-2">Per-Core Usage</div>
                    <div className="grid grid-cols-4 gap-2">
                      {cpuInfo.load.per_core.slice(0, 8).map((usage, index) => (
                        <div key={index} className="text-center">
                          <div className="text-xs text-gray-400 mb-1">Core {index + 1}</div>
                          <div className={`text-xs font-medium ${
                            usage < 50 ? 'text-crypto-green' : 
                            usage < 80 ? 'text-crypto-gold' : 'text-crypto-red'
                          }`}>
                            {usage.toFixed(0)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Memory Details */}
        <div className="resource-panel bg-gradient-to-br from-gray-800 to-gray-900 p-5 rounded-lg border border-gray-700">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Memory Monitoring</h3>
              <p className="text-sm text-gray-400">RAM usage and availability</p>
            </div>
          </div>

          <div className="space-y-4">
            <ResourceMeter 
              label="Memory Usage" 
              value={systemMetrics?.memory?.percent || 0} 
            />
            
            {systemMetrics?.memory && (
              <div className="grid grid-cols-1 gap-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total RAM:</span>
                  <span className="text-white font-medium">{formatBytes(systemMetrics.memory.total)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Used:</span>
                  <span className="text-crypto-red font-medium">{formatBytes(systemMetrics.memory.used)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Available:</span>
                  <span className="text-crypto-green font-medium">{formatBytes(systemMetrics.memory.available)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Free:</span>
                  <span className="text-white font-medium">{formatBytes(systemMetrics.memory.total - systemMetrics.memory.used)}</span>
                </div>
              </div>
            )}

            {/* Memory Health Indicator */}
            <div className="mt-4 p-3 rounded-lg bg-gray-700/50">
              <div className="flex items-center space-x-2 mb-2">
                <div className={`w-3 h-3 rounded-full ${
                  systemMetrics?.memory?.percent < 70 ? 'bg-crypto-green' : 
                  systemMetrics?.memory?.percent < 85 ? 'bg-crypto-gold' : 'bg-crypto-red'
                }`}></div>
                <span className="text-sm font-medium text-white">Memory Health</span>
              </div>
              <p className="text-xs text-gray-400">
                {systemMetrics?.memory?.percent < 70 ? 
                  'Memory usage is optimal for mining operations.' :
                  systemMetrics?.memory?.percent < 85 ?
                  'Memory usage is moderate. Monitor for optimal performance.' :
                  'High memory usage detected. Consider closing unnecessary applications.'
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Recommendations */}
      {cpuInfo?.recommendations && (
        <div className="recommendations bg-gradient-to-r from-purple-500/10 to-blue-500/10 p-5 rounded-lg border border-purple-500/20">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Performance Recommendations</h3>
              <p className="text-sm text-gray-400">System optimization suggestions</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {cpuInfo.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-gray-800/50 rounded-lg">
                <div className="w-2 h-2 bg-purple-400 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-sm text-gray-300">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemMonitoring;