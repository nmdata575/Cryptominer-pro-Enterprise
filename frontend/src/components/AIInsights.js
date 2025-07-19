import React, { useState, useEffect } from 'react';

const AIInsights = ({ insights, predictions }) => {
  const [activeTab, setActiveTab] = useState('predictions');
  const [analysisHistory, setAnalysisHistory] = useState([]);

  useEffect(() => {
    if (predictions && Object.keys(predictions).length > 0) {
      setAnalysisHistory(prev => {
        const newEntry = {
          timestamp: Date.now(),
          ...predictions
        };
        return [...prev.slice(-10), newEntry]; // Keep last 10 entries
      });
    }
  }, [predictions]);

  const formatConfidence = (confidence) => {
    const level = confidence || 0;
    if (level >= 0.8) return { text: 'High', color: 'text-crypto-green' };
    if (level >= 0.6) return { text: 'Medium', color: 'text-crypto-gold' };
    return { text: 'Low', color: 'text-crypto-red' };
  };

  const getTrendIcon = (trend) => {
    switch (trend?.toLowerCase()) {
      case 'increasing': return '📈';
      case 'decreasing': return '📉';
      case 'stable': return '➡️';
      default: return '🔄';
    }
  };

  const tabs = [
    { id: 'predictions', name: 'AI Predictions', icon: '🤖' },
    { id: 'insights', name: 'Market Insights', icon: '📊' },
    { id: 'optimization', name: 'Optimization', icon: '⚡' }
  ];

  return (
    <div className="space-y-6">
      {/* AI Status Card */}
      <div className="mining-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-white">AI Assistant</h3>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
            <span className="text-purple-400 text-sm">Active</span>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-2 mb-4">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-crypto-accent/20'
              }`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="mr-1">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="min-h-[200px]">
          {activeTab === 'predictions' && (
            <div className="space-y-4">
              {predictions && Object.keys(predictions).length > 0 ? (
                <>
                  {/* Hashrate Prediction */}
                  {predictions.predicted_hashrate && (
                    <div className="ai-prediction">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-white">
                          📈 Predicted Hashrate
                        </span>
                        <span className="text-crypto-gold font-bold">
                          {predictions.predicted_hashrate > 1000000 
                            ? `${(predictions.predicted_hashrate / 1000000).toFixed(2)} MH/s`
                            : `${(predictions.predicted_hashrate / 1000).toFixed(2)} KH/s`
                          }
                        </span>
                      </div>
                      {predictions.confidence && (
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-300">Confidence</span>
                          <span className={formatConfidence(predictions.confidence).color}>
                            {formatConfidence(predictions.confidence).text}
                          </span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Recommended Settings */}
                  {predictions.recommended_threads && (
                    <div className="ai-prediction">
                      <div className="text-sm font-medium text-white mb-2">
                        ⚙️ Recommended Settings
                      </div>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between">
                          <span className="text-gray-300">Threads:</span>
                          <span className="text-white">{predictions.recommended_threads}</span>
                        </div>
                        {predictions.recommended_intensity && (
                          <div className="flex justify-between">
                            <span className="text-gray-300">Intensity:</span>
                            <span className="text-white">
                              {(predictions.recommended_intensity * 100).toFixed(0)}%
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Learning Status */}
                  <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-3">
                    <div className="text-sm text-purple-400">
                      🧠 AI Learning Progress
                    </div>
                    <div className="mt-2">
                      <div className="progress-bar">
                        <div 
                          className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full"
                          style={{ width: `${Math.min(100, analysisHistory.length * 10)}%` }}
                        ></div>
                      </div>
                      <div className="text-xs text-purple-400 mt-1">
                        {analysisHistory.length} data points collected
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center text-gray-400 py-8">
                  <div className="text-4xl mb-2">🤖</div>
                  <p>AI is warming up...</p>
                  <p className="text-xs mt-2">Start mining to begin AI learning</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'insights' && (
            <div className="space-y-4">
              {/* Hash Pattern Analysis */}
              {insights?.hash_pattern_prediction && (
                <div className="ai-insight">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-white">
                      {getTrendIcon(insights.hash_pattern_prediction.trend)} Hash Pattern
                    </span>
                    <span className={`text-xs ${formatConfidence(insights.hash_pattern_prediction.confidence).color}`}>
                      {formatConfidence(insights.hash_pattern_prediction.confidence).text} Confidence
                    </span>
                  </div>
                  <p className="text-xs text-gray-300">
                    Trend: <span className="text-white capitalize">
                      {insights.hash_pattern_prediction.trend || 'Analyzing...'}
                    </span>
                  </p>
                </div>
              )}

              {/* Difficulty Forecast */}
              {insights?.difficulty_forecast && Object.keys(insights.difficulty_forecast).length > 0 && (
                <div className="ai-insight">
                  <div className="text-sm font-medium text-white mb-2">
                    📊 Difficulty Forecast
                  </div>
                  <p className="text-xs text-gray-300">
                    Network difficulty analysis and predictions will appear here as data is collected.
                  </p>
                </div>
              )}

              {/* Coin Switching Recommendations */}
              {insights?.coin_switching_recommendation && Object.keys(insights.coin_switching_recommendation).length > 0 && (
                <div className="ai-insight">
                  <div className="text-sm font-medium text-white mb-2">
                    💱 Coin Switching Advice
                  </div>
                  <p className="text-xs text-gray-300">
                    AI-powered coin switching recommendations based on profitability analysis.
                  </p>
                </div>
              )}

              {(!insights || Object.keys(insights).length === 0) && (
                <div className="text-center text-gray-400 py-8">
                  <div className="text-4xl mb-2">📊</div>
                  <p>Gathering market insights...</p>
                  <p className="text-xs mt-2">Insights will appear as AI analyzes mining data</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'optimization' && (
            <div className="space-y-4">
              {/* Optimization Suggestions */}
              {insights?.optimization_suggestions && insights.optimization_suggestions.length > 0 ? (
                <div className="space-y-3">
                  {insights.optimization_suggestions.map((suggestion, index) => (
                    <div key={index} className="ai-prediction">
                      <div className="flex items-start space-x-2">
                        <span className="text-crypto-gold">💡</span>
                        <div className="text-xs text-gray-300">
                          {suggestion}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-400 py-8">
                  <div className="text-4xl mb-2">⚡</div>
                  <p>Analyzing performance...</p>
                  <p className="text-xs mt-2">Optimization suggestions will appear based on your mining patterns</p>
                </div>
              )}

              {/* Performance Score */}
              <div className="bg-crypto-gold/10 border border-crypto-gold/20 rounded-lg p-3">
                <div className="text-sm text-crypto-gold mb-2">
                  🎯 Performance Score
                </div>
                <div className="flex items-center space-x-3">
                  <div className="flex-1">
                    <div className="progress-bar">
                      <div 
                        className="h-full bg-gradient-to-r from-crypto-gold to-yellow-500 rounded-full"
                        style={{ width: `${Math.min(100, (predictions?.confidence || 0) * 100)}%` }}
                      ></div>
                    </div>
                  </div>
                  <span className="text-crypto-gold font-bold">
                    {((predictions?.confidence || 0) * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-xs text-crypto-gold/80 mt-1">
                  Based on current configuration and AI analysis
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick AI Actions */}
      <div className="mining-card">
        <h4 className="text-lg font-semibold text-white mb-3">Quick AI Actions</h4>
        
        <div className="grid grid-cols-1 gap-3">
          <button className="flex items-center justify-between p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg text-sm text-purple-400 hover:bg-purple-500/20 transition-colors">
            <span>🎯 Auto-optimize Settings</span>
            <span className="text-xs opacity-60">Coming Soon</span>
          </button>
          
          <button className="flex items-center justify-between p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-sm text-blue-400 hover:bg-blue-500/20 transition-colors">
            <span>📈 Profit Calculator</span>
            <span className="text-xs opacity-60">Beta</span>
          </button>
          
          <button className="flex items-center justify-between p-3 bg-crypto-gold/10 border border-crypto-gold/20 rounded-lg text-sm text-crypto-gold hover:bg-crypto-gold/20 transition-colors">
            <span>💱 Coin Comparison</span>
            <span className="text-xs opacity-60">AI Powered</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIInsights;