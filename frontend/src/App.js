import React, { useState, useEffect } from 'react';
import MiningDashboard from './components/MiningDashboard';
import SystemComponents from './components/SystemComponents';
import AIComponents from './components/AIComponents';
import { SavedPoolsManager, CustomCoinsManager, EnterpriseThreadManager, EnterpriseDBConfig } from './components/AdvancedComponents';
import './styles.css';

const App = () => {
  const [miningStatus, setMiningStatus] = useState({
    is_mining: false,
    stats: {}
  });
  const [selectedCoin, setSelectedCoin] = useState(null);
  const [walletConfig, setWalletConfig] = useState({
    mode: 'pool',
    wallet_address: 'ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl',
    pool_username: 'ltc1qqvz2zw9hqd804a03xg95m4594p7v7thk25sztl',
    pool_password: 'd=24000',
    custom_pool_address: 'stratum+tcp://ltc.luckymonster.pro',
    custom_pool_port: 4112,
    custom_rpc_host: '',
    custom_rpc_port: '',
    custom_rpc_username: '',
    custom_rpc_password: ''
  });
  const [miningConfig, setMiningConfig] = useState({
    threads: 4,
    intensity: 1.0,
    ai_enabled: true,
    auto_optimize: true,
    auto_thread_detection: true,
    thread_profile: 'standard',
    // Enterprise configurations
    enterprise_mode: false,
    target_cpu_utilization: 1.0,
    thread_scaling_enabled: true
  });
  const [systemStats, setSystemStats] = useState({});
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [websocket, setWebsocket] = useState(null);
  const [enterpriseConfig, setEnterpriseConfig] = useState({
    remote_db_enabled: false,
    remote_mongo_url: ''
  });
  const [showSavedPools, setShowSavedPools] = useState(false);
  const [showCustomCoins, setShowCustomCoins] = useState(false);

  // Initialize WebSocket connection
  const connectWebSocket = useCallback(() => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
    const wsUrl = backendUrl.replace('http', 'ws') + '/ws';
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnectionStatus('Connected');
      setWebsocket(ws);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'mining_update') {
        setMiningStatus({
          is_mining: data.is_mining,
          stats: data.stats
        });
      } else if (data.type === 'system_update') {
        setSystemStats(data.data);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnectionStatus('Disconnected');
      
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        console.log('Attempting to reconnect WebSocket...');
        connectWebSocket();
      }, 5000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('Error');
    };
  }, []);

  const fetchInitialData = useCallback(async () => {
    try {
      // Fetch coin presets
      const coinsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/coins/presets`);
      if (coinsResponse.ok) {
        const coinsData = await coinsResponse.json();
        const coins = Object.values(coinsData.presets);
        if (coins.length > 0 && !selectedCoin) {
          setSelectedCoin(coins[0]); // Default to first coin (Litecoin)
        }
      }

      // Fetch initial mining status
      const statusResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mining/status`);
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setMiningStatus(statusData);
      }

      // Fetch system stats
      const systemResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/system/stats`);
      if (systemResponse.ok) {
        const systemData = await systemResponse.json();
        setSystemStats(systemData);
      }
    } catch (error) {
      console.error('Failed to fetch initial data:', error);
    }
  }, [selectedCoin]);

  useEffect(() => {
    // Try a simple backend connection test
    const testConnection = async () => {
      try {
        console.log('Testing backend connection...');
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/health`);
        if (response.ok) {
          const data = await response.json();
          console.log('Backend connection successful:', data);
          setConnectionStatus('Connected');
          
          // Only connect WebSocket after successful health check
          connectWebSocket();
          fetchInitialData();
        } else {
          console.error('Backend health check failed');
          setConnectionStatus('Error');
        }
      } catch (error) {
        console.error('Backend connection failed:', error);
        setConnectionStatus('Error');
      }
    };
    
    testConnection();
    
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [connectWebSocket, fetchInitialData, websocket]);

  const connectWebSocket = () => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
    const wsUrl = backendUrl.replace('http', 'ws') + '/ws';
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnectionStatus('Connected');
      setWebsocket(ws);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'mining_update') {
        setMiningStatus({
          is_mining: data.is_mining,
          stats: data.stats
        });
      } else if (data.type === 'system_update') {
        setSystemStats(data.data);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnectionStatus('Disconnected');
      
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        console.log('Attempting to reconnect WebSocket...');
        connectWebSocket();
      }, 5000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('Error');
    };
  };

  const fetchInitialData = async () => {
    try {
      // Fetch coin presets
      const coinsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/coins/presets`);
      if (coinsResponse.ok) {
        const coinsData = await coinsResponse.json();
        const coins = Object.values(coinsData.presets);
        if (coins.length > 0 && !selectedCoin) {
          setSelectedCoin(coins[0]); // Default to first coin (Litecoin)
        }
      }

      // Fetch initial mining status
      const statusResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mining/status`);
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setMiningStatus(statusData);
      }

      // Fetch system stats
      const systemResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/system/stats`);
      if (systemResponse.ok) {
        const systemData = await systemResponse.json();
        setSystemStats(systemData);
      }
    } catch (error) {
      console.error('Failed to fetch initial data:', error);
    }
  };

  const handleCoinSelect = (coin) => {
    setSelectedCoin(coin);
  };

  const handleWalletConfigChange = (newConfig) => {
    setWalletConfig(newConfig);
  };

  const handleMiningConfigChange = (newConfig) => {
    setMiningConfig(newConfig);
  };

  const handleEnterpriseConfigChange = (newConfig) => {
    setEnterpriseConfig(newConfig);
    // Note: In a production environment, this would trigger a backend configuration update
    console.log('Enterprise config updated:', newConfig);
  };

  const handleMiningStart = async () => {
    try {
      // Ensure we have a selected coin with all required fields
      if (!selectedCoin) {
        alert('Please select a cryptocurrency first');
        return;
      }

      // Validate required fields for pool mining
      if (walletConfig.mode === 'pool' && !walletConfig.pool_username) {
        alert('Please enter pool username for pool mining');
        return;
      }

      // Build complete mining configuration with all required fields
      const startConfig = {
        coin: {
          name: selectedCoin.name,
          symbol: selectedCoin.symbol,
          algorithm: selectedCoin.algorithm,
          block_reward: selectedCoin.block_reward,
          block_time: selectedCoin.block_time,
          difficulty: selectedCoin.difficulty,
          scrypt_params: selectedCoin.scrypt_params,
          network_hashrate: selectedCoin.network_hashrate,
          wallet_format: selectedCoin.wallet_format
        },
        mode: walletConfig.mode,
        threads: miningConfig.threads,
        intensity: miningConfig.intensity,
        auto_optimize: miningConfig.auto_optimize,
        ai_enabled: miningConfig.ai_enabled,
        wallet_address: walletConfig.wallet_address,
        pool_username: walletConfig.pool_username,
        pool_password: walletConfig.pool_password,
        custom_pool_address: walletConfig.custom_pool_address,
        // Convert port to integer or omit if empty
        ...(walletConfig.custom_pool_port && walletConfig.custom_pool_port !== '' ? 
          { custom_pool_port: parseInt(walletConfig.custom_pool_port) || undefined } : {}),
        custom_rpc_host: walletConfig.custom_rpc_host,
        // Convert RPC port to integer or omit if empty
        ...(walletConfig.custom_rpc_port && walletConfig.custom_rpc_port !== '' ? 
          { custom_rpc_port: parseInt(walletConfig.custom_rpc_port) || undefined } : {}),
        custom_rpc_username: walletConfig.custom_rpc_username,
        custom_rpc_password: walletConfig.custom_rpc_password,
        auto_thread_detection: miningConfig.auto_thread_detection,
        thread_profile: miningConfig.thread_profile,
        // Enterprise configurations
        enterprise_mode: miningConfig.enterprise_mode,
        target_cpu_utilization: miningConfig.target_cpu_utilization,
        thread_scaling_enabled: miningConfig.thread_scaling_enabled
      };

      console.log('Sending mining config:', startConfig);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mining/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(startConfig)
      });

      const result = await response.json();
      
      if (response.ok && result.success) {
        console.log('Mining started successfully:', result.message);
        // Status will be updated via WebSocket
      } else {
        // Fix error display - handle both array and string errors
        let errorMessage = 'Unknown error occurred';
        
        if (result.detail) {
          if (Array.isArray(result.detail)) {
            // Handle validation errors array
            errorMessage = result.detail.map(err => `${err.loc ? err.loc.join('.') + ': ' : ''}${err.msg}`).join('; ');
          } else if (typeof result.detail === 'string') {
            // Handle string error messages
            errorMessage = result.detail;
          } else {
            errorMessage = JSON.stringify(result.detail);
          }
        } else if (result.message) {
          errorMessage = result.message;
        }
        
        console.error('Failed to start mining:', errorMessage);
        alert(`Failed to start mining:\n${errorMessage}`);
      }
    } catch (error) {
      console.error('Error starting mining:', error);
      alert(`Network error starting mining:\n${error.message}`);
    }
  };

  const handleMiningStop = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mining/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const result = await response.json();
      
      if (response.ok && result.success) {
        console.log('Mining stopped successfully');
        // Status will be updated via WebSocket
      } else {
        console.error('Failed to stop mining:', result.message);
      }
    } catch (error) {
      console.error('Error stopping mining:', error);
    }
  };

  // Pool Management Functions
  const handleUsePool = (miningConfig, poolInfo) => {
    // Update wallet config with pool information
    setWalletConfig(prev => ({
      ...prev,
      mode: 'pool',
      wallet_address: miningConfig.wallet_address,
      pool_username: miningConfig.pool_username,
      pool_password: miningConfig.pool_password,
      custom_pool_address: poolInfo.pool_address,
      custom_pool_port: poolInfo.pool_port
    }));

    // Update selected coin if it exists
    if (miningConfig.coin && miningConfig.coin.symbol) {
      // Find the coin from presets or create a simple one
      const coinConfig = {
        name: poolInfo.coin_symbol,
        symbol: poolInfo.coin_symbol,
        algorithm: 'Scrypt',
        custom_pool_address: poolInfo.pool_address,
        custom_pool_port: poolInfo.pool_port
      };
      setSelectedCoin(coinConfig);
    }

    console.log('Pool configuration loaded:', poolInfo.name);
  };

  const handleSelectCustomCoin = (coinConfig) => {
    setSelectedCoin(coinConfig);
    console.log('Custom coin selected:', coinConfig.name);
  };

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="connection-status">
          <div className={`status-indicator ${connectionStatus === 'Connected' ? 'status-connected' : 'status-disconnected'}`}></div>
          <span>{connectionStatus}</span>
        </div>
        <h1 className="app-title">⛏️ CryptoMiner Pro</h1>
        <p className="app-subtitle">AI-Powered Mining Dashboard</p>
        
        {/* Quick Access Buttons */}
        <div className="header-actions">
          <button
            onClick={() => setShowSavedPools(true)}
            className="btn btn-secondary"
            title="Manage saved pool configurations"
          >
            💾 Saved Pools
          </button>
          <button
            onClick={() => setShowCustomCoins(true)}
            className="btn btn-secondary"
            title="Manage custom coins"
          >
            🪙 Custom Coins
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Mining Dashboard */}
        <MiningDashboard
          miningStatus={miningStatus}
          selectedCoin={selectedCoin}
          walletConfig={walletConfig}
          miningConfig={miningConfig}
          systemStats={systemStats}
          onCoinSelect={handleCoinSelect}
          onWalletConfigChange={handleWalletConfigChange}
          onMiningStart={handleMiningStart}
          onMiningStop={handleMiningStop}
          onConfigChange={handleMiningConfigChange}
        />

        {/* Additional Components Grid */}
        <div className="dashboard-grid">
          {/* Enterprise Database Configuration */}
          <EnterpriseDBConfig
            onConfigChange={handleEnterpriseConfigChange}
          />

          {/* Enterprise Thread Manager */}
          <EnterpriseThreadManager
            miningConfig={miningConfig}
            onConfigChange={handleMiningConfigChange}
            systemStats={systemStats}
          />

          {/* System Components */}
          <SystemComponents
            miningConfig={miningConfig}
            onConfigChange={handleMiningConfigChange}
            systemStats={systemStats}
          />

          {/* AI Components */}
          <AIComponents
            miningStatus={miningStatus}
            systemStats={systemStats}
          />
        </div>
      </div>

      {/* Saved Pools Manager Modal */}
      {showSavedPools && (
        <SavedPoolsManager
          onUsePool={handleUsePool}
          onClose={() => setShowSavedPools(false)}
          currentConfig={{
            coin: selectedCoin,
            wallet_address: walletConfig.wallet_address,
            pool_username: walletConfig.pool_username,
            pool_password: walletConfig.pool_password,
            mode: walletConfig.mode
          }}
        />
      )}

      {/* Custom Coins Manager Modal */}
      {showCustomCoins && (
        <CustomCoinsManager
          onSelectCoin={handleSelectCustomCoin}
          onClose={() => setShowCustomCoins(false)}
        />
      )}
    </div>
  );
};

export default App;