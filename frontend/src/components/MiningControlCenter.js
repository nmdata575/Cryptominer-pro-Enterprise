import React from 'react';

const MiningControlCenter = ({ 
  miningStatus, 
  selectedCoin, 
  coinPresets, 
  miningConfig,
  onStart, 
  onStop, 
  errorMessage,
  systemMetrics 
}) => {
  const isHealthy = systemMetrics && systemMetrics.cpu?.usage_percent < 90;
  const currentCoin = coinPresets && selectedCoin ? coinPresets[selectedCoin] : null;

  return (
    <div className="space-y-4">
      {/* Quick Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Mining Status */}
        <div className="status-card bg-gradient-to-br from-gray-800 to-gray-900 p-4 rounded-lg border border-gray-700">
          <div className="flex items-center space-x-3">
            <div className={`w-4 h-4 rounded-full ${
              miningStatus.is_mining ? 'bg-crypto-green animate-pulse' : 'bg-gray-500'
            }`}></div>
            <div>
              <div className="text-sm text-gray-400">Mining Status</div>
              <div className={`font-bold ${miningStatus.is_mining ? 'text-crypto-green' : 'text-gray-400'}`}>
                {miningStatus.is_mining ? 'ACTIVE' : 'STOPPED'}
              </div>
            </div>
          </div>
        </div>

        {/* Current Coin */}
        <div className="status-card bg-gradient-to-br from-gray-800 to-gray-900 p-4 rounded-lg border border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-4 h-4 bg-crypto-gold rounded-full"></div>
            <div>
              <div className="text-sm text-gray-400">Selected Coin</div>
              <div className="font-bold text-crypto-gold">
                {currentCoin ? `${currentCoin.name} (${currentCoin.symbol})` : 'None'}
              </div>
            </div>
          </div>
        </div>

        {/* System Health */}
        <div className="status-card bg-gradient-to-br from-gray-800 to-gray-900 p-4 rounded-lg border border-gray-700">
          <div className="flex items-center space-x-3">
            <div className={`w-4 h-4 rounded-full ${isHealthy ? 'bg-crypto-green' : 'bg-crypto-red'}`}></div>
            <div>
              <div className="text-sm text-gray-400">System Health</div>
              <div className={`font-bold ${isHealthy ? 'text-crypto-green' : 'text-crypto-red'}`}>
                {isHealthy ? 'HEALTHY' : 'HIGH LOAD'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mining Performance Summary */}
      {miningStatus.is_mining && (
        <div className="performance-summary bg-gradient-to-r from-crypto-blue/20 to-crypto-accent/20 p-4 rounded-lg border border-crypto-blue/30">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-crypto-blue">{miningStatus.stats?.hashrate?.toFixed(2) || '0.00'}</div>
              <div className="text-xs text-gray-400">Hash Rate (H/s)</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-crypto-green">{miningStatus.stats?.accepted_shares || 0}</div>
              <div className="text-xs text-gray-400">Accepted Shares</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-crypto-red">{miningStatus.stats?.rejected_shares || 0}</div>
              <div className="text-xs text-gray-400">Rejected Shares</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-crypto-gold">{miningStatus.stats?.blocks_found || 0}</div>
              <div className="text-xs text-gray-400">Blocks Found</div>
            </div>
          </div>
        </div>
      )}

      {/* Main Control Buttons */}
      <div className="control-buttons flex flex-col sm:flex-row gap-3">
        {!miningStatus.is_mining ? (
          <button
            onClick={onStart}
            disabled={!selectedCoin || !currentCoin}
            className="flex-1 bg-gradient-to-r from-crypto-green to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-4 px-6 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m-6-8h12a2 2 0 012 2v8a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2z" />
            </svg>
            <span>START MINING</span>
          </button>
        ) : (
          <button
            onClick={onStop}
            className="flex-1 bg-gradient-to-r from-crypto-red to-red-600 hover:from-red-600 hover:to-red-700 text-white font-bold py-4 px-6 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10h6v4H9z" />
            </svg>
            <span>STOP MINING</span>
          </button>
        )}

        {/* Quick Settings Button */}
        <button className="px-6 py-4 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors flex items-center justify-center space-x-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span>QUICK SETTINGS</span>
        </button>
      </div>

      {/* Error Message */}
      {errorMessage && (
        <div className="error-message bg-crypto-red/20 border border-crypto-red/40 text-crypto-red p-4 rounded-lg">
          <div className="flex items-start space-x-3">
            <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <div className="font-medium">Mining Error</div>
              <div className="text-sm mt-1 opacity-90">{errorMessage}</div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Tips */}
      {!miningStatus.is_mining && (
        <div className="quick-tips bg-crypto-gold/10 border border-crypto-gold/30 p-4 rounded-lg">
          <div className="flex items-start space-x-3">
            <svg className="w-5 h-5 mt-0.5 text-crypto-gold flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-crypto-gold">
              <div className="font-medium text-sm">Quick Start Tips:</div>
              <ul className="text-xs mt-2 space-y-1 opacity-90">
                <li>• Select a cryptocurrency from the Miner Setup section</li>
                <li>• Configure your wallet address for rewards</li>
                <li>• Choose mining mode (Solo or Pool) based on your preference</li>
                <li>• System will auto-detect optimal thread count for your hardware</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MiningControlCenter;