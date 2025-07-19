import React from 'react';

const CoinSelector = ({ coinPresets, selectedCoin, onCoinChange }) => {
  const getCoinIcon = (symbol) => {
    const icons = {
      'LTC': '₿',
      'DOGE': '🐕', 
      'FTC': '🪶',
    };
    return icons[symbol] || '💰';
  };

  const getCoinColor = (symbol) => {
    const colors = {
      'LTC': 'from-gray-400 to-gray-600',
      'DOGE': 'from-yellow-400 to-yellow-600',
      'FTC': 'from-blue-400 to-blue-600',
    };
    return colors[symbol] || 'from-crypto-gold to-yellow-600';
  };

  if (!coinPresets || Object.keys(coinPresets).length === 0) {
    return (
      <div className="mining-card">
        <h3 className="text-xl font-bold text-white mb-4">Select Cryptocurrency</h3>
        <div className="text-center text-gray-400 py-8">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p>Loading available coins...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mining-card">
      <h3 className="text-xl font-bold text-white mb-4">Select Cryptocurrency</h3>
      
      <div className="space-y-3">
        {Object.entries(coinPresets).map(([key, coin]) => (
          <div
            key={key}
            className={`coin-option ${selectedCoin === key ? 'selected' : ''}`}
            onClick={() => onCoinChange(key)}
          >
            <div className={`coin-icon bg-gradient-to-br ${getCoinColor(coin.symbol)}`}>
              {getCoinIcon(coin.symbol)}
            </div>
            
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold text-white">{coin.name}</div>
                  <div className="text-sm text-gray-300">{coin.symbol}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-crypto-gold">
                    {coin.block_reward} {coin.symbol}
                  </div>
                  <div className="text-xs text-gray-400">Block Reward</div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Coin Details */}
      {selectedCoin && coinPresets[selectedCoin] && (
        <div className="mt-6 p-4 bg-crypto-accent/20 rounded-lg">
          <h4 className="font-semibold text-white mb-3">
            {coinPresets[selectedCoin].name} Details
          </h4>
          
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-300">Algorithm:</span>
              <span className="text-white font-medium">
                {coinPresets[selectedCoin].algorithm.toUpperCase()}
              </span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-300">Block Time:</span>
              <span className="text-white font-medium">
                {coinPresets[selectedCoin].block_time_target}s
              </span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-300">Network Difficulty:</span>
              <span className="text-white font-medium">
                {coinPresets[selectedCoin].network_difficulty.toLocaleString()}
              </span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-300">Scrypt N:</span>
              <span className="text-white font-medium">
                {coinPresets[selectedCoin].scrypt_params?.N || 1024}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Performance Hint */}
      <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
        <div className="flex items-start space-x-2">
          <span className="text-blue-400 text-sm">💡</span>
          <div className="text-blue-400 text-xs">
            <p className="font-medium mb-1">Mining Tip:</p>
            <p>Different coins have varying difficulty levels and profitability. 
               The AI system will help optimize your selection based on current market conditions.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoinSelector;