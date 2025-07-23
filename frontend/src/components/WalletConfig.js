import React, { useState } from 'react';
import axios from 'axios';

const WalletConfig = ({ config, onConfigChange, selectedCoin, coinPresets, isMining }) => {
  const [validationStatus, setValidationStatus] = useState({ valid: null, message: '' });
  const [isValidating, setIsValidating] = useState(false);
  const [poolTestStatus, setPoolTestStatus] = useState({ testing: false, result: null });

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
    
    // Clear pool test when pool settings change
    if (key.includes('pool') || key.includes('rpc')) {
      setPoolTestStatus({ testing: false, result: null });
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

  const testPoolConnection = async () => {
    const address = config.mode === 'pool' ? config.custom_pool_address : config.custom_rpc_host;
    const port = config.mode === 'pool' ? config.custom_pool_port : config.custom_rpc_port;

    if (!address || !port) {
      setPoolTestStatus({
        testing: false,
        result: { success: false, message: 'Please enter both address and port' }
      });
      return;
    }

    setPoolTestStatus({ testing: true, result: null });

    try {
      const response = await axios.post(`${BACKEND_URL}/api/pool/test-connection`, {
        pool_address: address,
        pool_port: parseInt(port),
        type: config.mode === 'pool' ? 'pool' : 'rpc'
      });

      setPoolTestStatus({
        testing: false,
        result: response.data
      });
    } catch (error) {
      setPoolTestStatus({
        testing: false,
        result: {
          success: false,
          message: error.response?.data?.detail || error.message
        }
      });
    }
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
            ? 'Mine directly to your node - full block rewards' 
            : 'Mine through a pool - share rewards with other miners'
          }
        </p>
      </div>

      {/* Solo Mining Configuration */}
      {config.mode === 'solo' && (
        <div className="space-y-4">
          {/* Wallet Address */}
          <div className="form-group">
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

          {/* Custom RPC Configuration */}
          <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-purple-400 mb-3">🔧 Custom RPC Node (Optional)</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="form-group">
                <label className="form-label text-xs">RPC Host/IP</label>
                <input
                  type="text"
                  className="form-input text-sm"
                  placeholder="127.0.0.1 or your.node.com"
                  value={config.custom_rpc_host || ''}
                  onChange={(e) => handleConfigChange('custom_rpc_host', e.target.value)}
                  disabled={isMining}
                />
              </div>

              <div className="form-group">
                <label className="form-label text-xs">RPC Port</label>
                <input
                  type="number"
                  className="form-input text-sm"
                  placeholder="9332 (LTC), 22555 (DOGE)"
                  value={config.custom_rpc_port || ''}
                  onChange={(e) => handleConfigChange('custom_rpc_port', e.target.value)}
                  disabled={isMining}
                />
              </div>

              <div className="form-group">
                <label className="form-label text-xs">RPC Username</label>
                <input
                  type="text"
                  className="form-input text-sm"
                  placeholder="rpcuser"
                  value={config.custom_rpc_username || ''}
                  onChange={(e) => handleConfigChange('custom_rpc_username', e.target.value)}
                  disabled={isMining}
                />
              </div>

              <div className="form-group">
                <label className="form-label text-xs">RPC Password</label>
                <input
                  type="password"
                  className="form-input text-sm"
                  placeholder="rpcpassword"
                  value={config.custom_rpc_password || ''}
                  onChange={(e) => handleConfigChange('custom_rpc_password', e.target.value)}
                  disabled={isMining}
                />
              </div>
            </div>

            {(config.custom_rpc_host || config.custom_rpc_port) && (
              <div className="mt-3 flex items-center space-x-2">
                <button
                  type="button"
                  onClick={testPoolConnection}
                  disabled={poolTestStatus.testing || isMining}
                  className="px-3 py-1 text-xs bg-purple-600 hover:bg-purple-700 text-white rounded disabled:opacity-50"
                >
                  {poolTestStatus.testing ? '🔄 Testing...' : '🔍 Test Connection'}
                </button>

                {poolTestStatus.result && (
                  <div className={`text-xs ${
                    poolTestStatus.result.success ? 'text-crypto-green' : 'text-crypto-red'
                  }`}>
                    {poolTestStatus.result.success ? '✅' : '❌'} {poolTestStatus.result.message}
                  </div>
                )}
              </div>
            )}

            <p className="text-xs text-gray-400 mt-2">
              Leave empty to use default settings. Connect to your own node for maximum decentralization.
            </p>
          </div>
        </div>
      )}

      {/* Pool Mining Configuration */}
      {config.mode === 'pool' && (
        <div className="space-y-4">
          {/* Pool Username */}
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

          {/* Pool Password */}
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

          {/* Custom Pool Configuration */}
          <div className="bg-cyan-500/10 border border-cyan-500/20 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-cyan-400 mb-3">🏊 Custom Pool Server (Optional)</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="form-group">
                <label className="form-label text-xs">Pool Address</label>
                <input
                  type="text"
                  className="form-input text-sm"
                  placeholder="stratum.pool.com"
                  value={config.custom_pool_address || ''}
                  onChange={(e) => handleConfigChange('custom_pool_address', e.target.value)}
                  disabled={isMining}
                />
              </div>

              <div className="form-group">
                <label className="form-label text-xs">Pool Port</label>
                <input
                  type="number"
                  className="form-input text-sm"
                  placeholder="3333, 4444, 9999"
                  value={config.custom_pool_port || ''}
                  onChange={(e) => handleConfigChange('custom_pool_port', e.target.value)}
                  disabled={isMining}
                />
              </div>
            </div>

            {(config.custom_pool_address || config.custom_pool_port) && (
              <div className="mt-3 flex items-center space-x-2">
                <button
                  type="button"
                  onClick={testPoolConnection}
                  disabled={poolTestStatus.testing || isMining}
                  className="px-3 py-1 text-xs bg-cyan-600 hover:bg-cyan-700 text-white rounded disabled:opacity-50"
                >
                  {poolTestStatus.testing ? '🔄 Testing...' : '🔍 Test Pool'}
                </button>

                {poolTestStatus.result && (
                  <div className={`text-xs ${
                    poolTestStatus.result.success ? 'text-crypto-green' : 'text-crypto-red'
                  }`}>
                    {poolTestStatus.result.success ? '✅' : '❌'} {poolTestStatus.result.message}
                  </div>
                )}
              </div>
            )}

            <p className="text-xs text-gray-400 mt-2">
              Leave empty to use coin's default pool. Enter your preferred pool's stratum address and port.
            </p>
          </div>

          {/* Pool Info */}
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
            <div className="flex items-start space-x-2">
              <span className="text-blue-400 text-sm">ℹ️</span>
              <div className="text-blue-400 text-xs">
                <p className="font-medium mb-1">Pool Mining Benefits:</p>
                <p>More consistent payouts, shared rewards based on contribution, 
                   lower variance compared to solo mining. Great for smaller miners.</p>
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
            <p>Never share private keys or RPC passwords publicly. Only enter wallet addresses (public keys) 
               and ensure RPC connections are secure. Always verify addresses before mining.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WalletConfig;