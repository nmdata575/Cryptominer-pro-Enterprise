import React, { useState } from 'react';
import axios from 'axios';

const WalletConfig = ({ config, onConfigChange, selectedCoin, coinPresets, isMining }) => {
  const [validationStatus, setValidationStatus] = useState({ valid: null, message: '' });
  const [isValidating, setIsValidating] = useState(false);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  const handleConfigChange = (key, value) => {
    onConfigChange(prev => ({
      ...prev,
      [key]: value
    }));

    // Clear validation when address changes
    if (key === 'wallet_address') {
      setValidationStatus({ valid: null, message: '' });
    }
  };

  const validateWalletAddress = async () => {
    if (!config.wallet_address.trim()) {
      setValidationStatus({ valid: false, message: 'Address cannot be empty' });
      return;
    }

    if (!selectedCoin || !coinPresets[selectedCoin]) {
      setValidationStatus({ valid: false, message: 'Please select a coin first' });
      return;
    }

    setIsValidating(true);
    
    try {
      const response = await axios.post(`${BACKEND_URL}/api/wallet/validate`, {
        address: config.wallet_address.trim(),
        coin_symbol: coinPresets[selectedCoin].symbol
      });

      if (response.data.valid) {
        setValidationStatus({ 
          valid: true, 
          message: `Valid ${response.data.format || 'address'} (${response.data.type || 'standard'})` 
        });
      } else {
        setValidationStatus({ 
          valid: false, 
          message: response.data.error || 'Invalid address' 
        });
      }
    } catch (error) {
      setValidationStatus({ 
        valid: false, 
        message: 'Validation failed: ' + (error.response?.data?.detail || error.message)
      });
    }
    
    setIsValidating(false);
  };

  const getAddressExample = () => {
    if (!selectedCoin || !coinPresets[selectedCoin]) return '';
    
    const coin = coinPresets[selectedCoin];
    const examples = {
      'LTC': 'LTC1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4 (or legacy: LhK1Nk..)',
      'DOGE': 'DQVpNjNVHjTgHaE4Y1oqRxCLe6...',
      'FTC': '6nsHHMiUexBgE8GZzw5EBVL...'
    };
    
    return examples[coin.symbol] || 'Enter valid wallet address';
  };

  const getAddressFormat = () => {
    if (!selectedCoin || !coinPresets[selectedCoin]) return '';
    
    const coin = coinPresets[selectedCoin];
    const formats = {
      'LTC': 'Legacy (L...), Segwit (ltc1...), or Multisig (M.../3...)',
      'DOGE': 'Standard (D...) or Multisig (A.../9...)',
      'FTC': 'Legacy format (6...)'
    };
    
    return formats[coin.symbol] || 'Standard wallet address format';
  };

  return (
    <div className="mining-card">
      <h3 className="text-xl font-bold text-white mb-4">💰 Wallet Configuration</h3>
      
      {/* Mining Mode Selection */}
      <div className="form-group mb-4">
        <label className="form-label">Mining Mode</label>
        <select
          className="form-select"
          value={config.mode}
          onChange={(e) => handleConfigChange('mode', e.target.value)}
          disabled={isMining}
        >
          <option value="solo">Solo Mining</option>
          <option value="pool">Pool Mining</option>
        </select>
        <p className="text-xs text-gray-400 mt-1">
          {config.mode === 'solo' 
            ? 'Mine directly - rewards sent to your wallet' 
            : 'Mine through a pool - share rewards with other miners'
          }
        </p>
      </div>

      {/* Wallet Address for Solo Mining */}
      {config.mode === 'solo' && (
        <div className="form-group mb-4">
          <label className="form-label">
            Wallet Address
            <span className="text-crypto-red ml-1">*</span>
          </label>
          
          <div className="relative">
            <input
              type="text"
              className={`form-input pr-20 ${
                validationStatus.valid === true ? 'border-crypto-green' :
                validationStatus.valid === false ? 'border-crypto-red' : ''
              }`}
              placeholder={getAddressExample()}
              value={config.wallet_address}
              onChange={(e) => handleConfigChange('wallet_address', e.target.value)}
              disabled={isMining}
            />
            
            <button
              type="button"
              onClick={validateWalletAddress}
              disabled={isValidating || isMining || !config.wallet_address.trim()}
              className={`absolute right-2 top-2 px-3 py-1 text-xs rounded ${
                isValidating 
                  ? 'bg-gray-500 text-white cursor-not-allowed' 
                  : validationStatus.valid === true
                  ? 'bg-crypto-green text-white'
                  : validationStatus.valid === false
                  ? 'bg-crypto-red text-white'
                  : 'bg-crypto-blue text-crypto-gold hover:bg-crypto-accent'
              }`}
            >
              {isValidating ? '...' : validationStatus.valid === true ? '✓' : validationStatus.valid === false ? '✗' : 'Check'}
            </button>
          </div>

          {/* Validation Status */}
          {validationStatus.message && (
            <div className={`mt-2 text-xs ${
              validationStatus.valid === true ? 'text-crypto-green' : 'text-crypto-red'
            }`}>
              {validationStatus.valid === true ? '✅' : '❌'} {validationStatus.message}
            </div>
          )}

          <p className="text-xs text-gray-400 mt-1">
            Format: {getAddressFormat()}
          </p>
        </div>
      )}

      {/* Pool Configuration */}
      {config.mode === 'pool' && (
        <div className="space-y-4">
          <div className="form-group">
            <label className="form-label">
              Pool Username
              <span className="text-crypto-red ml-1">*</span>
            </label>
            <input
              type="text"
              className="form-input"
              placeholder="your_wallet_address.worker_name"
              value={config.pool_username}
              onChange={(e) => handleConfigChange('pool_username', e.target.value)}
              disabled={isMining}
            />
            <p className="text-xs text-gray-400 mt-1">
              Usually your wallet address followed by a worker name
            </p>
          </div>

          <div className="form-group">
            <label className="form-label">Pool Password</label>
            <input
              type="text"
              className="form-input"
              placeholder="x (default)"
              value={config.pool_password}
              onChange={(e) => handleConfigChange('pool_password', e.target.value)}
              disabled={isMining}
            />
            <p className="text-xs text-gray-400 mt-1">
              Most pools use "x" as password, some may require specific values
            </p>
          </div>

          {/* Pool Info */}
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
            <div className="flex items-start space-x-2">
              <span className="text-blue-400 text-sm">ℹ️</span>
              <div className="text-blue-400 text-xs">
                <p className="font-medium mb-1">Pool Mining:</p>
                <p>Configure your pool URL in the coin settings or connect to popular pools. 
                   Your earnings will be distributed by the pool based on your contribution.</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Security Warning */}
      <div className="mt-4 p-3 bg-crypto-gold/10 border border-crypto-gold/20 rounded-lg">
        <div className="flex items-start space-x-2">
          <span className="text-crypto-gold text-sm">🔒</span>
          <div className="text-crypto-gold text-xs">
            <p className="font-medium mb-1">Security Notice:</p>
            <p>Never share your private keys. Only enter wallet addresses (public keys) here. 
               Always double-check addresses before mining to avoid loss of rewards.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WalletConfig;