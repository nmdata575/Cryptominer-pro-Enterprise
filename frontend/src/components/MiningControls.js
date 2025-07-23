import React, { useState, useEffect } from 'react';
import axios from 'axios';

const MiningControls = ({ config, onConfigChange, isMining, onStart, onStop }) => {
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
      // Fallback to browser detection
      if (typeof navigator !== 'undefined' && navigator.hardwareConcurrency) {
        setCpuInfo({
          cores: {
            physical: navigator.hardwareConcurrency,
            logical: navigator.hardwareConcurrency,
            hyperthreading: false
          },
          recommended_threads: {
            conservative: Math.max(1, navigator.hardwareConcurrency - 1),
            balanced: navigator.hardwareConcurrency,
            aggressive: navigator.hardwareConcurrency
          },
          mining_profiles: {
            light: { threads: Math.max(1, Math.floor(navigator.hardwareConcurrency / 2)), description: "Light mining" },
            standard: { threads: Math.max(1, navigator.hardwareConcurrency - 1), description: "Standard mining" },
            maximum: { threads: navigator.hardwareConcurrency, description: "Maximum mining" }
          }
        });
      }
    } finally {
      setLoadingCpuInfo(false);
    }
  };

  const handleConfigChange = (key, value) => {
    onConfigChange(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleThreadProfileChange = (profile) => {
    if (cpuInfo && cpuInfo.mining_profiles[profile]) {
      const profileConfig = cpuInfo.mining_profiles[profile];
      handleConfigChange('thread_profile', profile);
      handleConfigChange('threads', profileConfig.threads);
      handleConfigChange('auto_thread_detection', true);
    }
  };

  const getMaxThreads = () => {
    if (cpuInfo) {
      return cpuInfo.cores.logical || cpuInfo.cores.physical || 16;
    }
    return navigator.hardwareConcurrency || 16;
  };

  const getThreadRecommendation = () => {
    if (cpuInfo && cpuInfo.recommended_threads) {
      return cpuInfo.recommended_threads.balanced;
    }
    if (typeof navigator !== 'undefined' && navigator.hardwareConcurrency) {
      return Math.max(1, navigator.hardwareConcurrency - 1);
    }
    return 4;
  };

  return (
    <div className="mining-card">
      <h3 className="text-xl font-bold text-white mb-4">⚙️ Mining Performance</h3>
      
      {/* System Information */}
      {loadingCpuInfo ? (
        <div className="mb-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
          <div className="flex items-center space-x-2">
            <div className="animate-spin h-4 w-4 border-2 border-blue-400 border-t-transparent rounded-full"></div>
            <span className="text-blue-400 text-sm">Detecting system capabilities...</span>
          </div>
        </div>
      ) : cpuInfo && (
        <div className="mb-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
          <div className="text-green-400 text-sm">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">🖥️ System Detected:</span>
              <span className="text-xs bg-green-500/20 px-2 py-1 rounded">Auto-Optimized</span>
            </div>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-gray-400">Physical Cores:</span>
                <span className="text-green-400 ml-2 font-medium">{cpuInfo.cores.physical}</span>
              </div>
              <div>
                <span className="text-gray-400">Logical Cores:</span>
                <span className="text-green-400 ml-2 font-medium">{cpuInfo.cores.logical}</span>
              </div>
              {cpuInfo.frequency?.max && (
                <div>
                  <span className="text-gray-400">Max Frequency:</span>
                  <span className="text-green-400 ml-2 font-medium">{Math.round(cpuInfo.frequency.max)} MHz</span>
                </div>
              )}
              <div>
                <span className="text-gray-400">Hyperthreading:</span>
                <span className="text-green-400 ml-2 font-medium">{cpuInfo.cores.hyperthreading ? 'Yes' : 'No'}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mining Profiles */}
      {cpuInfo && cpuInfo.mining_profiles && (
        <div className="form-group mb-4">
          <label className="form-label">Mining Profile</label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
            {Object.entries(cpuInfo.mining_profiles).map(([key, profile]) => (
              <button
                key={key}
                type="button"
                onClick={() => handleThreadProfileChange(key)}
                disabled={isMining}
                className={`p-3 rounded-lg text-sm transition-all ${
                  config.thread_profile === key
                    ? 'bg-crypto-accent text-crypto-gold border-2 border-crypto-gold'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600 border-2 border-transparent'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                <div className="font-medium capitalize">{key}</div>
                <div className="text-xs opacity-75 mt-1">{profile.threads} threads</div>
                <div className="text-xs opacity-60 mt-1">{profile.description}</div>
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-2">
            Choose a profile based on your usage needs. Higher profiles use more CPU resources.
          </p>
        </div>
      )}

      {/* Thread Control */}
      <div className="form-group mb-4">
        <div className="flex items-center justify-between mb-2">
          <label className="form-label">
            Thread Count 
            <span className="text-crypto-gold text-xs ml-2">
              (Recommended: {getThreadRecommendation()})
            </span>
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="auto-threads"
              checked={config.auto_thread_detection}
              onChange={(e) => handleConfigChange('auto_thread_detection', e.target.checked)}
              disabled={isMining}
              className="text-crypto-accent focus:ring-crypto-accent"
            />
            <label htmlFor="auto-threads" className="text-xs text-gray-400">Auto-detect</label>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <input
            type="range"
            min="1"
            max={getMaxThreads()}
            value={config.threads}
            onChange={(e) => {
              handleConfigChange('threads', parseInt(e.target.value));
              handleConfigChange('auto_thread_detection', false); // Disable auto when manually adjusted
            }}
            disabled={isMining || config.auto_thread_detection}
            className="flex-1 h-2 bg-crypto-accent/30 rounded-lg appearance-none cursor-pointer slider disabled:opacity-50"
          />
          <span className="text-white font-medium min-w-[3rem] text-center">
            {config.auto_thread_detection && cpuInfo && cpuInfo.mining_profiles[config.thread_profile] 
              ? cpuInfo.mining_profiles[config.thread_profile].threads 
              : config.threads}
          </span>
          <span className="text-xs text-gray-400 min-w-[4rem]">
            / {getMaxThreads()}
          </span>
        </div>
        
        {/* Thread Usage Indicator */}
        <div className="mt-2">
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>Thread Usage</span>
            <span>{Math.round((config.threads / getMaxThreads()) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-1.5">
            <div 
              className={`h-1.5 rounded-full transition-all duration-300 ${
                (config.threads / getMaxThreads()) > 0.8 ? 'bg-crypto-red' :
                (config.threads / getMaxThreads()) > 0.6 ? 'bg-crypto-gold' : 'bg-crypto-green'
              }`}
              style={{ width: `${(config.threads / getMaxThreads()) * 100}%` }}
            ></div>
          </div>
        </div>
        
        <p className="text-xs text-gray-400 mt-2">
          {config.auto_thread_detection 
            ? `Auto-detection enabled: Using ${config.thread_profile} profile for optimal performance`
            : `Manual control: Using ${config.threads} of ${getMaxThreads()} available threads`
          }
        </p>
      </div>

      {/* Performance Recommendations */}
      {cpuInfo && cpuInfo.recommendations && (
        <div className="mb-4 p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg">
          <div className="text-purple-400 text-sm">
            <div className="font-medium mb-2">💡 Performance Recommendations:</div>
            <ul className="space-y-1 text-xs opacity-90">
              {cpuInfo.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <span className="text-purple-400 mt-0.5">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Mining Intensity */}
      <div className="form-group mb-4">
        <label className="form-label">
          Mining Intensity ({(config.intensity * 100).toFixed(0)}%)
        </label>
        <div className="flex items-center space-x-3">
          <input
            type="range"
            min="0.1"
            max="1.0"
            step="0.1"
            value={config.intensity}
            onChange={(e) => handleConfigChange('intensity', parseFloat(e.target.value))}
            disabled={isMining}
            className="flex-1 h-2 bg-crypto-accent/30 rounded-lg appearance-none cursor-pointer slider"
          />
          <span className="text-white font-medium min-w-[3rem] text-center">
            {(config.intensity * 100).toFixed(0)}%
          </span>
        </div>
        <div className="mt-2">
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${config.intensity * 100}%` }}
            ></div>
          </div>
        </div>
        <p className="text-xs text-gray-400 mt-1">
          Lower intensity reduces system impact, higher intensity maximizes performance
        </p>
      </div>

      {/* AI Features */}
      <div className="space-y-3 mb-6">
        <div className="flex items-center space-x-3">
          <input
            type="checkbox"
            id="ai-enabled"
            className="form-checkbox"
            checked={config.ai_enabled}
            onChange={(e) => handleConfigChange('ai_enabled', e.target.checked)}
            disabled={isMining}
          />
          <label htmlFor="ai-enabled" className="form-label mb-0">
            Enable AI Optimization
          </label>
        </div>
        
        <div className="flex items-center space-x-3">
          <input
            type="checkbox"
            id="auto-optimize"
            className="form-checkbox"
            checked={config.auto_optimize}
            onChange={(e) => handleConfigChange('auto_optimize', e.target.checked)}
            disabled={isMining || !config.ai_enabled}
          />
          <label htmlFor="auto-optimize" className="form-label mb-0">
            Auto-Optimization
          </label>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="space-y-3">
        {!isMining ? (
          <button
            className="mining-button start w-full"
            onClick={onStart}
          >
            <span className="flex items-center justify-center space-x-2">
              <span>🚀</span>
              <span>Start Mining</span>
            </span>
          </button>
        ) : (
          <button
            className="mining-button stop w-full"
            onClick={onStop}
          >
            <span className="flex items-center justify-center space-x-2">
              <span>🛑</span>
              <span>Stop Mining</span>
            </span>
          </button>
        )}
        
        {isMining && (
          <div className="text-center">
            <div className="mining-effect bg-crypto-gold/10 border border-crypto-gold/30 rounded-lg p-3">
              <div className="flex items-center justify-center space-x-2">
                <div className="w-2 h-2 bg-crypto-gold rounded-full animate-pulse"></div>
                <span className="text-crypto-gold font-medium">Mining in progress...</span>
                <div className="w-2 h-2 bg-crypto-gold rounded-full animate-pulse"></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Performance Warnings */}
      {config.threads > getThreadRecommendation() && (
        <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
          <div className="flex items-start space-x-2">
            <span className="text-yellow-500 text-sm">⚠️</span>
            <div className="text-yellow-500 text-xs">
              <p className="font-medium mb-1">Performance Warning:</p>
              <p>High thread count may cause system instability. 
                 Consider reducing if you experience slowdowns.</p>
            </div>
          </div>
        </div>
      )}

      {config.intensity === 1.0 && (
        <div className="mt-4 p-3 bg-crypto-red/10 border border-crypto-red/20 rounded-lg">
          <div className="flex items-start space-x-2">
            <span className="text-crypto-red text-sm">🔥</span>
            <div className="text-crypto-red text-xs">
              <p className="font-medium mb-1">Maximum Intensity:</p>
              <p>System will use maximum resources. Monitor temperature 
                 and ensure adequate cooling.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MiningControls;