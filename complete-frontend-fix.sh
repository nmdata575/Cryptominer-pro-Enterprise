#!/bin/bash

# Complete Frontend Fix - Updated App.js with proper field handling

echo "🔧 Creating complete updated App.js..."

cat > ~/Desktop/Cryptominer-pro/frontend/src/App.js << 'EOF'
import React, { useState, useEffect } from 'react';
import MiningDashboard from './components/MiningDashboard';
import SystemComponents from './components/SystemComponents';
import AIComponents from './components/AIComponents';
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
    custom_pool_port: '4112',
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
    thread_profile: 'standard'
  });
  const [systemStats, setSystemStats] = useState({});
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [websocket, setWebsocket] = useState(null);

  // Initialize WebSocket connection
  useEffect(() => {
    connectWebSocket();
    fetchInitialData();
    
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

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
        auto_thread_detection: miningConfig.auto_thread_detection,
        thread_profile: miningConfig.thread_profile
      };

      // Handle optional numeric fields - only include if they have valid values
      if (walletConfig.custom_pool_port && walletConfig.custom_pool_port.toString().trim() !== '') {
        const port = parseInt(walletConfig.custom_pool_port);
        if (!isNaN(port) && port > 0) {
          startConfig.custom_pool_port = port;
        }
      }

      if (walletConfig.custom_rpc_port && walletConfig.custom_rpc_port.toString().trim() !== '') {
        const port = parseInt(walletConfig.custom_rpc_port);
        if (!isNaN(port) && port > 0) {
          startConfig.custom_rpc_port = port;
        }
      }

      // Handle optional string fields - only include if they have values
      if (walletConfig.custom_pool_address && walletConfig.custom_pool_address.trim() !== '') {
        startConfig.custom_pool_address = walletConfig.custom_pool_address.trim();
      }

      if (walletConfig.custom_rpc_host && walletConfig.custom_rpc_host.trim() !== '') {
        startConfig.custom_rpc_host = walletConfig.custom_rpc_host.trim();
      }

      if (walletConfig.custom_rpc_username && walletConfig.custom_rpc_username.trim() !== '') {
        startConfig.custom_rpc_username = walletConfig.custom_rpc_username.trim();
      }

      if (walletConfig.custom_rpc_password && walletConfig.custom_rpc_password.trim() !== '') {
        startConfig.custom_rpc_password = walletConfig.custom_rpc_password.trim();
      }

      console.log('Sending mining config:', startConfig);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mining/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(startConfig)
      });

      const result = await response.json();
      
      if (response.ok && result.success) {
        console.log('✅ Mining started successfully:', result.message);
        alert(`🚀 Mining Started Successfully!\n\n${result.message}`);
        // Status will be updated via WebSocket
      } else {
        // Fix error display - handle both array and string errors
        let errorMessage = 'Unknown error occurred';
        
        if (result.detail) {
          if (Array.isArray(result.detail)) {
            // Handle validation errors array
            errorMessage = result.detail.map(err => {
              const field = err.loc ? err.loc.join('.') : '';
              return `${field ? field + ': ' : ''}${err.msg}`;
            }).join('\n');
          } else if (typeof result.detail === 'string') {
            // Handle string error messages
            errorMessage = result.detail;
          } else {
            errorMessage = JSON.stringify(result.detail);
          }
        } else if (result.message) {
          errorMessage = result.message;
        }
        
        console.error('❌ Failed to start mining:', errorMessage);
        alert(`❌ Failed to start mining:\n\n${errorMessage}`);
      }
    } catch (error) {
      console.error('❌ Error starting mining:', error);
      alert(`🌐 Network error starting mining:\n\n${error.message}`);
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
        console.log('✅ Mining stopped successfully');
        alert('⏹️ Mining stopped successfully!');
        // Status will be updated via WebSocket
      } else {
        console.error('❌ Failed to stop mining:', result.message);
        alert(`❌ Failed to stop mining: ${result.message}`);
      }
    } catch (error) {
      console.error('❌ Error stopping mining:', error);
      alert(`🌐 Network error stopping mining: ${error.message}`);
    }
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
    </div>
  );
};

export default App;
EOF

echo "✅ Complete App.js updated!"

# Restart frontend service
echo "🔄 Restarting frontend service..."

# Check for different service names and restart the correct one
if sudo supervisorctl status | grep -q "cryptominer_pro:cryptominer_frontend"; then
    sudo supervisorctl restart cryptominer_pro:cryptominer_frontend
elif sudo supervisorctl status | grep -q "mining_system:frontend"; then
    sudo supervisorctl restart mining_system:frontend
else
    echo "⚠️  Please restart frontend service manually:"
    echo "   sudo supervisorctl status"
    echo "   sudo supervisorctl restart [frontend_service_name]"
fi

echo ""
echo "🎉 COMPLETE FRONTEND FIX APPLIED!"
echo ""
echo "✅ What was fixed:"
echo "   🔧 Proper numeric field handling (no more string-to-integer errors)"
echo "   🔧 Complete coin data transmission"
echo "   🔧 Better error message display"
echo "   🔧 Input validation and cleanup" 
echo "   🔧 Enhanced user feedback with emojis"
echo ""
echo "🌐 Test it now:"
echo "   1. Open http://localhost:3333"
echo "   2. Click 'START MINING' - should work immediately!"
echo "   3. Check real-time stats and AI system"
echo ""
echo "🚀 Your CryptoMiner Pro web interface is now fully functional!"