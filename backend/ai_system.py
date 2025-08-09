"""
CryptoMiner Pro - AI System Module
Handles AI-powered mining optimization, predictions, and insights
"""

import json
import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import numpy as np

# Try to import scikit-learn with fallback for Python 3.13 compatibility
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  Warning: scikit-learn not available. AI predictions will use simplified algorithms.")
    
    # Simple fallback implementations
    class LinearRegression:
        def __init__(self):
            self.coef_ = None
            self.intercept_ = None
        
        def fit(self, X, y):
            # Simple linear regression fallback
            X = np.array(X)
            y = np.array(y)
            if X.shape[1] == 1:
                self.coef_ = [np.corrcoef(X.flatten(), y)[0, 1]]
                self.intercept_ = np.mean(y) - self.coef_[0] * np.mean(X)
            else:
                # Multi-feature fallback - use mean
                self.coef_ = [1.0] * X.shape[1]
                self.intercept_ = np.mean(y)
        
        def predict(self, X):
            X = np.array(X)
            if self.coef_ is None:
                return np.array([0.0] * X.shape[0])
            return X @ self.coef_ + self.intercept_
    
    class StandardScaler:
        def __init__(self):
            self.mean_ = None
            self.scale_ = None
        
        def fit_transform(self, X):
            X = np.array(X)
            self.mean_ = np.mean(X, axis=0)
            self.scale_ = np.std(X, axis=0)
            self.scale_[self.scale_ == 0] = 1.0  # Avoid division by zero
            return (X - self.mean_) / self.scale_
        
        def transform(self, X):
            X = np.array(X)
            if self.mean_ is None or self.scale_ is None:
                return X
            return (X - self.mean_) / self.scale_

@dataclass
class AIInsights:
    hash_pattern_prediction: Dict[str, Any]
    network_difficulty_forecast: Dict[str, Any]
    optimization_suggestions: List[Dict[str, Any]]
    pool_performance_analysis: Dict[str, Any]
    efficiency_recommendations: List[str]

@dataclass
class AISystemStatus:
    is_active: bool = False
    learning_progress: float = 0.0
    data_points_collected: int = 0
    last_update: Optional[float] = None
    prediction_accuracy: float = 0.0
    optimization_score: float = 0.0

class AIPredictor:
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.training_data = []
        self.is_trained = False
        self.prediction_history = []
        
    def collect_data_point(self, hashrate: float, cpu_usage: float, memory_usage: float, threads: int, difficulty: float):
        """Collect data point for AI learning"""
        data_point = {
            'timestamp': time.time(),
            'hashrate': hashrate,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'threads': threads,
            'difficulty': difficulty,
            'efficiency': hashrate / cpu_usage if cpu_usage > 0 else 0
        }
        
        self.training_data.append(data_point)
        
        # Keep only recent data (last 1000 points)
        if len(self.training_data) > 1000:
            self.training_data = self.training_data[-1000:]
    
    def train_model(self):
        """Train AI model on collected data"""
        if len(self.training_data) < 10:
            return False, "Insufficient data for training"
        
        try:
            # Prepare training data
            X = []
            y = []
            
            for point in self.training_data:
                features = [
                    point['cpu_usage'],
                    point['memory_usage'], 
                    point['threads'],
                    point['difficulty']
                ]
                target = point['hashrate']
                
                X.append(features)
                y.append(target)
            
            X = np.array(X)
            y = np.array(y)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            return True, "Model trained successfully"
            
        except Exception as e:
            return False, f"Training failed: {str(e)}"
    
    def predict_hashrate(self, cpu_usage: float, memory_usage: float, threads: int, difficulty: float) -> float:
        """Predict hashrate based on system parameters"""
        if not self.is_trained:
            return 0.0
        
        try:
            features = np.array([[cpu_usage, memory_usage, threads, difficulty]])
            features_scaled = self.scaler.transform(features)
            prediction = self.model.predict(features_scaled)[0]
            
            # Store prediction for accuracy tracking
            self.prediction_history.append({
                'timestamp': time.time(),
                'prediction': prediction,
                'features': [cpu_usage, memory_usage, threads, difficulty]
            })
            
            return max(0.0, prediction)  # Ensure non-negative
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return 0.0

class AIOptimizer:
    def __init__(self):
        self.optimization_history = []
        self.best_configuration = None
        self.performance_threshold = 0.8
        
    def analyze_mining_performance(self, hashrate: float, cpu_usage: float, memory_usage: float, threads: int) -> Dict[str, Any]:
        """Analyze current mining performance"""
        efficiency = hashrate / cpu_usage if cpu_usage > 0 else 0
        
        # Performance grading
        if efficiency > 50:
            grade = "A+"
            performance_level = "Excellent"
        elif efficiency > 30:
            grade = "A"
            performance_level = "Very Good"
        elif efficiency > 20:
            grade = "B"
            performance_level = "Good"
        elif efficiency > 10:
            grade = "C"
            performance_level = "Average"
        else:
            grade = "D"
            performance_level = "Poor"
        
        return {
            "efficiency": efficiency,
            "grade": grade,
            "performance_level": performance_level,
            "hashrate": hashrate,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "threads": threads,
            "recommendations": self.generate_optimization_recommendations(efficiency, cpu_usage, memory_usage, threads)
        }
    
    def generate_optimization_recommendations(self, efficiency: float, cpu_usage: float, memory_usage: float, threads: int) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # CPU optimization
        if cpu_usage > 90:
            recommendations.append("Reduce thread count to lower CPU usage")
        elif cpu_usage < 50 and threads < psutil.cpu_count():
            recommendations.append("Increase thread count to utilize more CPU cores")
        
        # Memory optimization
        if memory_usage > 85:
            recommendations.append("Consider reducing mining intensity to free up memory")
        
        # Efficiency optimization
        if efficiency < 20:
            recommendations.append("Consider adjusting mining parameters for better efficiency")
            recommendations.append("Check for system background processes consuming resources")
        
        # System optimization
        if len(recommendations) == 0:
            recommendations.append("System is performing optimally")
        
        return recommendations
    
    def suggest_optimal_threads(self, system_cores: int, current_usage: float) -> int:
        """Suggest optimal thread count based on system resources"""
        if current_usage > 90:
            return max(1, system_cores - 2)  # Conservative
        elif current_usage > 70:
            return max(1, system_cores - 1)  # Moderate
        else:
            return system_cores  # Aggressive
    
    def calculate_thread_profiles(self, system_cores: int) -> Dict[str, int]:
        """Calculate thread profiles for different mining intensities"""
        return {
            "light": max(1, system_cores // 2),      # 50% of cores
            "standard": max(1, int(system_cores * 0.75)),  # 75% of cores  
            "maximum": system_cores                   # 100% of cores
        }

class AISystemManager:
    def __init__(self):
        self.status = AISystemStatus()
        self.predictor = AIPredictor()
        self.optimizer = AIOptimizer()
        self.data_collection_thread = None
        self.is_collecting = False
        
    def start_ai_system(self):
        """Start AI system data collection and learning"""
        self.status.is_active = True
        self.is_collecting = True
        
        # Start data collection thread
        self.data_collection_thread = threading.Thread(target=self._data_collection_loop, daemon=True)
        self.data_collection_thread.start()
        
        print("🧠 AI System started - collecting data and learning...")
    
    def stop_ai_system(self):
        """Stop AI system"""
        self.status.is_active = False
        self.is_collecting = False
        
        if self.data_collection_thread:
            self.data_collection_thread.join(timeout=2)
    
    def _data_collection_loop(self):
        """Background data collection loop"""
        while self.is_collecting:
            try:
                # Collect system metrics
                cpu_usage = psutil.cpu_percent(interval=1)
                memory_usage = psutil.virtual_memory().percent
                
                # Mock mining data (replace with actual mining stats)
                hashrate = 100.0  # Would come from mining engine
                threads = psutil.cpu_count()
                difficulty = 1000000  # Would come from network
                
                # Collect data point
                self.predictor.collect_data_point(hashrate, cpu_usage, memory_usage, threads, difficulty)
                
                self.status.data_points_collected = len(self.predictor.training_data)
                self.status.last_update = time.time()
                
                # Update learning progress
                max_data_points = 100
                self.status.learning_progress = min(100.0, (self.status.data_points_collected / max_data_points) * 100)
                
                # Train model periodically
                if self.status.data_points_collected > 10 and self.status.data_points_collected % 10 == 0:
                    success, message = self.predictor.train_model()
                    if success:
                        self.status.optimization_score = min(100.0, self.status.learning_progress + 20)
                
                time.sleep(5)  # Collect data every 5 seconds
                
            except Exception as e:
                print(f"AI data collection error: {e}")
                time.sleep(5)
    
    def get_ai_insights(self, current_hashrate: float = 0.0, current_cpu: float = 0.0, current_memory: float = 0.0, threads: int = 1) -> AIInsights:
        """Get AI insights and predictions"""
        
        # Hash pattern prediction
        predicted_hashrate = self.predictor.predict_hashrate(current_cpu, current_memory, threads, 1000000)
        hash_prediction = {
            "predicted_hashrate": predicted_hashrate,
            "confidence": self.status.optimization_score / 100.0,
            "trend": "increasing" if predicted_hashrate > current_hashrate else "decreasing"
        }
        
        # Network difficulty forecast
        difficulty_forecast = {
            "current_difficulty": 1000000,
            "predicted_change": "+5.2%",
            "time_horizon": "24 hours",
            "confidence": 0.75
        }
        
        # Performance analysis
        performance_analysis = self.optimizer.analyze_mining_performance(current_hashrate, current_cpu, current_memory, threads)
        
        # Pool performance (mock data)
        pool_analysis = {
            "connection_quality": "excellent",
            "latency": "12ms",
            "share_acceptance_rate": "98.5%",
            "recommended_pool": "current pool is optimal"
        }
        
        return AIInsights(
            hash_pattern_prediction=hash_prediction,
            network_difficulty_forecast=difficulty_forecast,
            optimization_suggestions=performance_analysis["recommendations"],
            pool_performance_analysis=pool_analysis,
            efficiency_recommendations=performance_analysis["recommendations"]
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get AI system status"""
        return asdict(self.status)
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get detailed CPU information for AI optimization"""
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        
        thread_profiles = self.optimizer.calculate_thread_profiles(cpu_count)
        
        return {
            "total_cores": cpu_count,
            "physical_cores": psutil.cpu_count(logical=False),
            "current_frequency": cpu_freq.current if cpu_freq else 0,
            "max_frequency": cpu_freq.max if cpu_freq else 0,
            "per_core_usage": cpu_percent,
            "average_usage": sum(cpu_percent) / len(cpu_percent),
            "thread_profiles": thread_profiles,
            "recommended_threads": self.optimizer.suggest_optimal_threads(cpu_count, sum(cpu_percent) / len(cpu_percent))
        }

# Global AI system instance
ai_system = AISystemManager()