import React from 'react';

const MiningControls = ({ config, onConfigChange, isMining, onStart, onStop }) => {
  const handleConfigChange = (key, value) => {
    onConfigChange(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const getThreadRecommendation = () => {
    if (typeof navigator !== 'undefined' && navigator.hardwareConcurrency) {
      return Math.max(1, navigator.hardwareConcurrency - 1);
    }
    return 4;
  };

  return (
    <div className="mining-card">
      <h3 className="text-xl font-bold text-white mb-4">⚙️ Mining Performance</h3>
      
      {/* Thread Count */}
      <div className="form-group mb-4">
        <label className="form-label">
          Thread Count 
          <span className="text-crypto-gold text-xs ml-2">
            (Recommended: {getThreadRecommendation()})
          </span>
        </label>
        <div className="flex items-center space-x-3">
          <input
            type="range"
            min="1"
            max="16"
            value={config.threads}
            onChange={(e) => handleConfigChange('threads', parseInt(e.target.value))}
            disabled={isMining}
            className="flex-1 h-2 bg-crypto-accent/30 rounded-lg appearance-none cursor-pointer slider"
          />
          <span className="text-white font-medium min-w-[2rem] text-center">
            {config.threads}
          </span>
        </div>
        <p className="text-xs text-gray-400 mt-1">
          Higher thread counts increase CPU usage but may improve hash rate
        </p>
      </div>

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