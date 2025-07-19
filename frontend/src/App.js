import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';

// Component imports
import MiningDashboard from './components/MiningDashboard';
import CoinSelector from './components/CoinSelector';
import AIInsights from './components/AIInsights';
import SystemMonitor from './components/SystemMonitor';
import MiningControls from './components/MiningControls';
import WalletConfig from './components/WalletConfig';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  // Core state
  const [miningStatus, setMiningStatus] = useState({
    is_mining: false,
    stats: {
      hashrate: 0.0,
      accepted_shares: 0,
      rejected_shares: 0,
      blocks_found: 0,
      cpu_usage: 0.0,
      memory_usage: 0.0,
      temperature: null,
      uptime: 0.0,
      efficiency: 0.0
    },
    config: null
  });
  
  const [systemStats, setSystemStats] = useState({
    cpu: { usage_percent: 0, count: 0 },
    memory: { total: 0, available: 0, percent: 0, used: 0 },
    disk: { total: 0, used: 0, free: 0, percent: 0 }
  });
  
  const [aiInsights, setAiInsights] = useState({
    insights: {
      hash_pattern_prediction: {},
      difficulty_forecast: {},
      coin_switching_recommendation: {},
      optimization_suggestions: []
    },
    predictions: {}
  });
  
  const [coinPresets, setCoinPresets] = useState({});
  const [selectedCoin, setSelectedCoin] = useState('litecoin');
  const [miningConfig, setMiningConfig] = useState({
    mode: 'solo',
    threads: 4,
    intensity: 1.0,
    auto_optimize: true,
    ai_enabled: true,
    wallet_address: '',
    pool_username: '',
    pool_password: 'x'
  });
  
  const [websocket, setWebsocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [errorMessage, setErrorMessage] = useState('');

  // WebSocket connection management
  const connectWebSocket = useCallback(() => {
    if (websocket) return;
    
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/api/ws`;
    
    try {
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
        setErrorMessage('');
        setWebsocket(ws);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'mining_update') {
            setMiningStatus(prev => ({
              ...prev,
              stats: data.stats,
              is_mining: data.is_mining
            }));
          } else if (data.type === 'system_update') {
            setSystemStats(data.data);
          }
        } catch (error) {
          console.error('WebSocket message parsing error:', error);
        }
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setConnectionStatus('disconnected');
        setWebsocket(null);
        
        // Reconnect after 3 seconds
        setTimeout(() => {
          if (connectionStatus !== 'connected') {
            connectWebSocket();
          }
        }, 3000);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
        setErrorMessage('WebSocket connection failed');
      };
      
    } catch (error) {
      console.error('WebSocket creation failed:', error);
      setConnectionStatus('error');
      setErrorMessage('Failed to create WebSocket connection');
    }
  }, [websocket, connectionStatus]);

  // API functions
  const fetchMiningStatus = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/mining/status`);
      setMiningStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch mining status:', error);
      setErrorMessage('Failed to fetch mining status');
    }
  };

  const fetchAIInsights = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/mining/ai-insights`);
      if (!response.data.error) {
        setAiInsights(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch AI insights:', error);
    }
  };

  const fetchCoinPresets = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/coins/presets`);
      setCoinPresets(response.data.presets);
    } catch (error) {
      console.error('Failed to fetch coin presets:', error);
      setErrorMessage('Failed to fetch coin presets');
    }
  };

  const fetchSystemStats = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/system/stats`);
      if (!response.data.error) {
        setSystemStats(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch system stats:', error);
    }
  };

  const startMining = async () => {
    try {
      const coinConfig = coinPresets[selectedCoin];
      if (!coinConfig) {
        setErrorMessage('Please select a valid coin');
        return;
      }

      // Validate wallet address for solo mining
      if (miningConfig.mode === 'solo' && !miningConfig.wallet_address.trim()) {
        setErrorMessage('Wallet address is required for solo mining');
        return;
      }

      // Validate pool credentials for pool mining
      if (miningConfig.mode === 'pool' && !miningConfig.pool_username.trim()) {
        setErrorMessage('Pool username is required for pool mining');
        return;
      }

      const fullConfig = {
        coin: coinConfig,
        mode: miningConfig.mode,
        threads: miningConfig.threads,
        intensity: miningConfig.intensity,
        auto_optimize: miningConfig.auto_optimize,
        ai_enabled: miningConfig.ai_enabled,
        wallet_address: miningConfig.wallet_address.trim(),
        pool_username: miningConfig.pool_username.trim(),
        pool_password: miningConfig.pool_password || 'x'
      };

      const response = await axios.post(`${BACKEND_URL}/api/mining/start`, fullConfig);
      
      if (response.data.success) {
        setErrorMessage('');
        await fetchMiningStatus();
      } else {
        setErrorMessage('Failed to start mining');
      }
    } catch (error) {
      console.error('Failed to start mining:', error);
      setErrorMessage('Failed to start mining: ' + (error.response?.data?.detail || error.message));
    }
  };

  const stopMining = async () => {
    try {
      const response = await axios.post(`${BACKEND_URL}/api/mining/stop`);
      
      if (response.data.success) {
        setErrorMessage('');
        await fetchMiningStatus();
      } else {
        setErrorMessage('Failed to stop mining');
      }
    } catch (error) {
      console.error('Failed to stop mining:', error);
      setErrorMessage('Failed to stop mining: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Effects
  useEffect(() => {
    // Initial data loading
    fetchCoinPresets();
    fetchMiningStatus();
    fetchSystemStats();
    fetchAIInsights();
    
    // Connect WebSocket
    connectWebSocket();
    
    // Cleanup on unmount
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [connectWebSocket]);

  // Periodic updates for non-WebSocket data
  useEffect(() => {
    const interval = setInterval(() => {
      if (connectionStatus !== 'connected') {
        fetchMiningStatus();
        fetchSystemStats();
      }
      fetchAIInsights();
    }, 5000);

    return () => clearInterval(interval);
  }, [connectionStatus]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-crypto-dark via-crypto-blue to-crypto-accent">
      {/* Header */}
      <header className="bg-crypto-dark/90 backdrop-blur-sm border-b border-crypto-accent/30 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-crypto-gold to-yellow-600 rounded-xl flex items-center justify-center">
                <span className="text-2xl font-bold text-crypto-dark">₿</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">CryptoMiner Pro</h1>
                <p className="text-crypto-gold text-sm">AI-Powered Mining Dashboard</p>
              </div>
            </div>
            
            {/* Connection Status */}
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
                connectionStatus === 'connected' 
                  ? 'bg-crypto-green/20 text-crypto-green' 
                  : connectionStatus === 'error'
                  ? 'bg-crypto-red/20 text-crypto-red'
                  : 'bg-yellow-500/20 text-yellow-500'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  connectionStatus === 'connected' 
                    ? 'bg-crypto-green animate-pulse' 
                    : connectionStatus === 'error'
                    ? 'bg-crypto-red'
                    : 'bg-yellow-500 animate-pulse'
                }`}></div>
                <span className="capitalize">{connectionStatus}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Error Message */}
      {errorMessage && (
        <div className="container mx-auto px-6 py-4">
          <div className="bg-crypto-red/20 border border-crypto-red/30 rounded-lg p-4 text-crypto-red">
            <p className="font-medium">⚠️ {errorMessage}</p>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
          
          {/* Left Sidebar - Controls */}
          <div className="xl:col-span-3 space-y-6">
            <CoinSelector
              coinPresets={coinPresets}
              selectedCoin={selectedCoin}
              onCoinChange={setSelectedCoin}
            />
            
            <WalletConfig
              config={miningConfig}
              onConfigChange={setMiningConfig}
              selectedCoin={selectedCoin}
              coinPresets={coinPresets}
              isMining={miningStatus.is_mining}
            />
            
            <MiningControls
              config={miningConfig}
              onConfigChange={setMiningConfig}
              isMining={miningStatus.is_mining}
              onStart={startMining}
              onStop={stopMining}
            />
          </div>

          {/* Center - Main Dashboard */}
          <div className="xl:col-span-6 space-y-6">
            <MiningDashboard
              stats={miningStatus.stats}
              isMining={miningStatus.is_mining}
              config={miningStatus.config}
            />
          </div>

          {/* Right Sidebar - AI Insights & System Monitor */}
          <div className="xl:col-span-3 space-y-6">
            <AIInsights 
              insights={aiInsights.insights}
              predictions={aiInsights.predictions}
            />
            
            <SystemMonitor stats={systemStats} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-crypto-dark/50 border-t border-crypto-accent/30 mt-12">
        <div className="container mx-auto px-6 py-6">
          <div className="text-center text-gray-400">
            <p>&copy; 2025 CryptoMiner Pro - Advanced AI-Powered Mining System</p>
            <p className="text-sm mt-2">
              Featuring complete scrypt implementation with multi-coin support
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;