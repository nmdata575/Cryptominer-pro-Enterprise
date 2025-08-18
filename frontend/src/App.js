import { useEffect, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MiningDashboard = () => {
  const [stats, setStats] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMiningStats = async () => {
    try {
      const [statsResponse, configResponse] = await Promise.all([
        axios.get(`${API}/mining/stats`),
        axios.get(`${API}/mining/config`)
      ]);
      
      setStats(statsResponse.data);
      setConfig(configResponse.data);
      setError(null);
    } catch (e) {
      console.error("Error fetching mining data:", e);
      setError("Failed to connect to mining API");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMiningStats();
    const interval = setInterval(fetchMiningStats, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const formatUptime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatHashrate = (hashrate) => {
    if (hashrate >= 1000000000) {
      return `${(hashrate / 1000000000).toFixed(2)} GH/s`;
    } else if (hashrate >= 1000000) {
      return `${(hashrate / 1000000).toFixed(2)} MH/s`;
    } else if (hashrate >= 1000) {
      return `${(hashrate / 1000).toFixed(2)} KH/s`;
    } else {
      return `${hashrate.toFixed(2)} H/s`;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-xl">Loading Mining Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl mb-2">Connection Error</h1>
          <p className="text-gray-400">{error}</p>
          <button 
            onClick={fetchMiningStats}
            className="mt-4 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">🚀 CryptoMiner Pro V30</h1>
              <p className="text-gray-300">Enterprise Mining Dashboard</p>
            </div>
            <div className={`flex items-center px-3 py-1 rounded-full text-sm ${
              stats?.pool_connected ? 'bg-green-600' : 'bg-red-600'
            }`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${
                stats?.pool_connected ? 'bg-green-300' : 'bg-red-300'
              }`}></div>
              {stats?.pool_connected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Hashrate Card */}
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">Hashrate</p>
                <p className="text-2xl font-bold text-blue-400">{formatHashrate(stats?.hashrate || 0)}</p>
              </div>
              <div className="text-3xl">⚡</div>
            </div>
          </div>

          {/* Threads Card */}
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">Active Threads</p>
                <p className="text-2xl font-bold text-green-400">{stats?.threads || 0}</p>
              </div>
              <div className="text-3xl">🧵</div>
            </div>
          </div>

          {/* Shares Card */}
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">Shares</p>
                <div className="flex space-x-4">
                  <span className="text-green-400">✅ {stats?.accepted_shares || 0}</span>
                  <span className="text-red-400">❌ {stats?.rejected_shares || 0}</span>
                </div>
              </div>
              <div className="text-3xl">📊</div>
            </div>
          </div>

          {/* Uptime Card */}
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">Uptime</p>
                <p className="text-2xl font-bold text-purple-400">{formatUptime(stats?.uptime || 0)}</p>
              </div>
              <div className="text-3xl">⏱️</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Mining Configuration */}
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <h2 className="text-xl font-bold mb-4 flex items-center">
              ⚙️ Mining Configuration
            </h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Coin:</span>
                <span className="font-semibold text-yellow-400">{config?.coin || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Intensity:</span>
                <span className="font-semibold text-blue-400">{config?.intensity || 0}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Difficulty:</span>
                <span className="font-semibold text-orange-400">{stats?.difficulty || 1}</span>
              </div>
            </div>
          </div>

          {/* AI Optimization */}
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <h2 className="text-xl font-bold mb-4 flex items-center">
              🤖 AI Optimization
            </h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">Learning Progress:</span>
                  <span className="font-semibold text-green-400">{(stats?.ai_learning || 0).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full" 
                    style={{ width: `${stats?.ai_learning || 0}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">Optimization:</span>
                  <span className="font-semibold text-purple-400">{(stats?.ai_optimization || 0).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-purple-500 h-2 rounded-full" 
                    style={{ width: `${stats?.ai_optimization || 0}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Status Information */}
        <div className="mt-8 bg-gray-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            📈 Mining Status
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl mb-2">
                {stats?.pool_connected ? '🟢' : '🔴'}
              </div>
              <p className="font-semibold">{stats?.pool_connected ? 'Pool Connected' : 'Pool Disconnected'}</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">
                {(stats?.threads || 0) > 0 ? '⚡' : '⏸️'}
              </div>
              <p className="font-semibold">{(stats?.threads || 0) > 0 ? 'Mining Active' : 'Mining Paused'}</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">🧠</div>
              <p className="font-semibold">AI {(stats?.ai_learning || 0) > 50 ? 'Optimized' : 'Learning'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <p className="text-gray-400">
              CryptoMiner Pro V30 - Enterprise Mining Platform
            </p>
            <p className="text-gray-500 text-sm">
              Last updated: {stats?.last_update ? new Date(stats.last_update).toLocaleTimeString() : 'Never'}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

const Home = () => {
  return <MiningDashboard />;
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />}>
            <Route index element={<Home />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
