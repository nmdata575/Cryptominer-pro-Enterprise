import React, { useState, useEffect } from 'react';

// Consolidated AI Components
const AIComponents = ({ miningStatus, systemStats }) => {
  return (
    <div className="ai-components">
      <AIInsights miningStatus={miningStatus} systemStats={systemStats} />
    </div>
  );
};

// AI Insights Component
const AIInsights = ({ miningStatus, systemStats }) => {
  const [activeTab, setActiveTab] = useState('predictions');
  const [aiInsights, setAiInsights] = useState(null);
  const [aiStatus, setAiStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAIData();
    const interval = setInterval(fetchAIData, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, [miningStatus]);

  const fetchAIData = async () => {
    try {
      // Fetch AI insights
      const insightsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/mining/ai-insights`);
      if (insightsResponse.ok) {
        const insights = await insightsResponse.json();
        setAiInsights(insights);
      }

      // Fetch AI system status
      const statusResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai/status`);
      if (statusResponse.ok) {
        const status = await statusResponse.json();
        setAiStatus(status);
      }
    } catch (error) {
      console.error('Failed to fetch AI data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">🤖 AI Assistant</h3>
        </div>
        <div className="card-content">
          <p>Loading AI data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">🤖 AI Mining Assistant</h3>
        <div className="status-badge status-success">
          AI {aiStatus?.is_active ? 'Active' : 'Inactive'}
        </div>
      </div>
      <div className="card-content">
        {/* AI Status Overview */}
        <AIStatusOverview aiStatus={aiStatus} />

        {/* AI Tabs */}
        <div className="tab-container">
          <div className="tab-list">
            <button 
              className={`tab-button ${activeTab === 'predictions' ? 'active' : ''}`}
              onClick={() => setActiveTab('predictions')}
            >
              🔮 AI Predictions
            </button>
            <button 
              className={`tab-button ${activeTab === 'insights' ? 'active' : ''}`}
              onClick={() => setActiveTab('insights')}
            >
              📊 Market Insights
            </button>
            <button 
              className={`tab-button ${activeTab === 'optimization' ? 'active' : ''}`}
              onClick={() => setActiveTab('optimization')}
            >
              ⚡ Optimization
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'predictions' && (
              <AIPredictionsTab aiInsights={aiInsights} miningStatus={miningStatus} />
            )}
            {activeTab === 'insights' && (
              <AIInsightsTab aiInsights={aiInsights} />
            )}
            {activeTab === 'optimization' && (
              <AIOptimizationTab aiInsights={aiInsights} systemStats={systemStats} />
            )}
          </div>
        </div>

        {/* Quick AI Actions */}
        <QuickAIActions aiInsights={aiInsights} />
      </div>
    </div>
  );
};

// AI Status Overview Component
const AIStatusOverview = ({ aiStatus }) => {
  if (!aiStatus) {
    return (
      <div className="ai-status-placeholder">
        <p>AI system status unavailable</p>
      </div>
    );
  }

  return (
    <div className="metrics-grid mb-4">
      <div className="metric-card">
        <div className="metric-value">{aiStatus.learning_progress?.toFixed(1) || '0.0'}%</div>
        <div className="metric-label">Learning Progress</div>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${aiStatus.learning_progress || 0}%` }}
          ></div>
        </div>
      </div>
      <div className="metric-card">
        <div className="metric-value">{aiStatus.data_points_collected || 0}</div>
        <div className="metric-label">Data Points</div>
      </div>
      <div className="metric-card">
        <div className="metric-value">{(aiStatus.optimization_score || 0).toFixed(0)}%</div>
        <div className="metric-label">Optimization Score</div>
      </div>
      <div className="metric-card">
        <div className="metric-value">{aiStatus.is_active ? 'RUNNING' : 'IDLE'}</div>
        <div className="metric-label">AI Status</div>
      </div>
    </div>
  );
};

// AI Predictions Tab Component
const AIPredictionsTab = ({ aiInsights, miningStatus }) => {
  const predictions = aiInsights?.insights?.hash_pattern_prediction || {};
  const currentHashrate = miningStatus?.stats?.hashrate || 0;

  return (
    <div className="ai-predictions">
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-value">{(predictions.predicted_hashrate || 0).toFixed(2)} H/s</div>
          <div className="metric-label">Predicted Hashrate</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{(currentHashrate).toFixed(2)} H/s</div>
          <div className="metric-label">Current Hashrate</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{((predictions.confidence || 0) * 100).toFixed(0)}%</div>
          <div className="metric-label">Prediction Confidence</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{predictions.trend || 'stable'}</div>
          <div className="metric-label">Trend Direction</div>
        </div>
      </div>

      <div className="mt-4">
        <h4>Hash Pattern Analysis</h4>
        <div className="bg-gray-800/30 rounded-lg p-4">
          <p>
            🔮 <strong>Prediction:</strong> The AI predicts a hashrate of {(predictions.predicted_hashrate || 0).toFixed(2)} H/s 
            based on current system conditions and mining patterns.
          </p>
          <p className="mt-2">
            📈 <strong>Trend:</strong> The hashrate trend is currently {predictions.trend || 'stable'} 
            with {((predictions.confidence || 0) * 100).toFixed(0)}% confidence.
          </p>
          <p className="mt-2">
            💡 <strong>Recommendation:</strong> {
              predictions.predicted_hashrate > currentHashrate 
                ? 'System has potential for improved performance with optimization.'
                : 'Current performance is meeting AI predictions.'
            }
          </p>
        </div>
      </div>
    </div>
  );
};

// AI Market Insights Tab Component
const AIInsightsTab = ({ aiInsights }) => {
  const difficulty = aiInsights?.insights?.network_difficulty_forecast || {};
  const poolAnalysis = aiInsights?.insights?.pool_performance_analysis || {};

  return (
    <div className="ai-market-insights">
      <div className="space-y-4">
        <div>
          <h4>Network Difficulty Forecast</h4>
          <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-value">{difficulty.current_difficulty || 'N/A'}</div>
                <div className="metric-label">Current Difficulty</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{difficulty.predicted_change || 'N/A'}</div>
                <div className="metric-label">Predicted Change</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{difficulty.time_horizon || 'N/A'}</div>
                <div className="metric-label">Time Horizon</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{((difficulty.confidence || 0) * 100).toFixed(0)}%</div>
                <div className="metric-label">Confidence</div>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h4>Pool Performance Analysis</h4>
          <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-value">{poolAnalysis.connection_quality || 'N/A'}</div>
                <div className="metric-label">Connection Quality</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{poolAnalysis.latency || 'N/A'}</div>
                <div className="metric-label">Average Latency</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{poolAnalysis.share_acceptance_rate || 'N/A'}</div>
                <div className="metric-label">Share Acceptance</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">optimal</div>
                <div className="metric-label">Pool Status</div>
              </div>
            </div>
            <p className="mt-3 text-sm">
              📊 <strong>Analysis:</strong> {poolAnalysis.recommended_pool || 'Current pool performance is optimal for mining operations.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// AI Optimization Tab Component
const AIOptimizationTab = ({ aiInsights, systemStats }) => {
  const suggestions = aiInsights?.insights?.optimization_suggestions || [];
  const efficiency = aiInsights?.insights?.efficiency_recommendations || [];

  return (
    <div className="ai-optimization">
      <div className="space-y-4">
        <div>
          <h4>Optimization Suggestions</h4>
          <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4">
            {suggestions.length > 0 ? (
              <ul className="space-y-2">
                {suggestions.map((suggestion, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-purple-400">💡</span>
                    <span className="text-sm">{suggestion}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-400">No optimization suggestions available yet.</p>
            )}
          </div>
        </div>

        <div>
          <h4>Efficiency Recommendations</h4>
          <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4">
            {efficiency.length > 0 ? (
              <ul className="space-y-2">
                {efficiency.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-yellow-400">⚡</span>
                    <span className="text-sm">{rec}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div>
                <p className="text-sm text-gray-400 mb-3">Generating efficiency recommendations...</p>
                <div className="space-y-2">
                  <div className="flex items-start gap-2">
                    <span className="text-yellow-400">⚡</span>
                    <span className="text-sm">
                      Current system efficiency: {((systemStats?.cpu_usage || 0) < 80 ? 'Good' : 'High Load')}
                    </span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-yellow-400">⚡</span>
                    <span className="text-sm">
                      Memory usage: {((systemStats?.memory_usage || 0) < 85 ? 'Optimal' : 'Consider reducing intensity')}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Quick AI Actions Component
const QuickAIActions = ({ aiInsights }) => {
  const handleAutoOptimize = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai/auto-optimize`, {
        method: 'POST'
      });
      if (response.ok) {
        alert('Auto-optimization activated!');
      }
    } catch (error) {
      console.error('Auto-optimize failed:', error);
    }
  };

  const handleProfitCalculator = () => {
    alert('Profit calculator coming soon!');
  };

  const handleCoinComparison = () => {
    alert('Coin comparison analysis coming soon!');
  };

  return (
    <div className="mt-6">
      <h4>Quick AI Actions</h4>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
        <button 
          className="btn btn-primary"
          onClick={handleAutoOptimize}
        >
          🎯 Auto-Optimize
        </button>
        <button 
          className="btn btn-secondary"
          onClick={handleProfitCalculator}
        >
          💰 Profit Calculator
        </button>
        <button 
          className="btn btn-secondary"
          onClick={handleCoinComparison}
        >
          🔍 Coin Comparison
        </button>
      </div>
    </div>
  );
};

export default AIComponents;