"""
AI Optimizer - AI-driven optimization and learning for mining performance
Implements machine learning algorithms to optimize mining parameters
"""

import asyncio
import logging
import numpy as np
import time
from typing import Dict, Any, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os

logger = logging.getLogger(__name__)

class AIOptimizer:
    def __init__(self):
        self.running = False
        self.learning_progress = 0.0
        self.optimization_progress = 0.0
        
        # ML components
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.trained = False
        
        # Training data
        self.training_data = []
        self.performance_history = []
        
        # Optimization parameters
        self.current_params = {
            'thread_count': 0,
            'intensity': 80,
            'difficulty': 1,
            'hashrate': 0
        }
        
        # Load existing model if available
        self._load_model()
        
        logger.info("AI Optimizer initialized")

    def _load_model(self):
        """Load pre-trained model if it exists"""
        try:
            model_path = 'ai_mining_model.pkl'
            scaler_path = 'ai_scaler.pkl'
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                
                self.trained = True
                self.learning_progress = 100.0
                logger.info("Loaded pre-trained AI model")
            else:
                logger.info("No pre-trained model found, will train from scratch")
                
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")

    def _save_model(self):
        """Save trained model to disk"""
        try:
            with open('ai_mining_model.pkl', 'wb') as f:
                pickle.dump(self.model, f)
            with open('ai_scaler.pkl', 'wb') as f:
                pickle.dump(self.scaler, f)
                
            logger.info("AI model saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save AI model: {e}")

    async def start_optimization(self, mining_engine):
        """Start AI optimization process"""
        if self.running:
            return
            
        self.running = True
        self.mining_engine = mining_engine
        
        logger.info("🤖 AI Optimizer started")
        
        try:
            # Run optimization loop
            await self._optimization_loop()
            
        except Exception as e:
            logger.error(f"AI optimization error: {e}")
        finally:
            self.running = False

    def stop(self):
        """Stop AI optimization"""
        self.running = False
        logger.info("AI Optimizer stopped")

    async def _optimization_loop(self):
        """Main AI optimization loop"""
        iteration = 0
        
        while self.running:
            try:
                # Collect current performance data
                stats = self.mining_engine.get_stats()
                self._collect_performance_data(stats)
                
                # Train model periodically
                if iteration % 10 == 0 and len(self.training_data) >= 10:
                    await self._train_model()
                
                # Make optimization predictions
                if self.trained and iteration % 5 == 0:
                    await self._optimize_parameters()
                
                # Update progress
                self._update_progress(iteration)
                
                iteration += 1
                await asyncio.sleep(30)  # Optimize every 30 seconds
                
            except Exception as e:
                logger.error(f"AI optimization loop error: {e}")
                await asyncio.sleep(10)

    def _collect_performance_data(self, stats: Dict[str, Any]):
        """Collect performance data for training"""
        try:
            # Extract relevant features
            features = [
                stats.get('thread_count', 0),
                stats.get('intensity', 80),
                stats.get('difficulty', 1),
                stats.get('hashrate', 0),
                len(self.performance_history),  # Experience factor
                time.time() % 86400,  # Time of day factor
            ]
            
            # Performance score (combination of hashrate and acceptance rate)
            accepted = stats.get('accepted_shares', 0)
            rejected = stats.get('rejected_shares', 0)
            total_shares = accepted + rejected
            
            if total_shares > 0:
                acceptance_rate = accepted / total_shares
                performance_score = stats.get('hashrate', 0) * acceptance_rate
            else:
                performance_score = stats.get('hashrate', 0)
            
            # Store data
            self.training_data.append(features)
            self.performance_history.append(performance_score)
            
            # Keep only recent data (last 1000 samples)
            if len(self.training_data) > 1000:
                self.training_data = self.training_data[-1000:]
                self.performance_history = self.performance_history[-1000:]
                
            # Update current parameters
            self.current_params.update({
                'thread_count': stats.get('thread_count', 0),
                'intensity': stats.get('intensity', 80),
                'difficulty': stats.get('difficulty', 1),
                'hashrate': stats.get('hashrate', 0)
            })
            
        except Exception as e:
            logger.error(f"Data collection error: {e}")

    async def _train_model(self):
        """Train the AI model with collected data"""
        if len(self.training_data) < 10:
            return
            
        try:
            logger.info("🧠 Training AI model...")
            
            # Prepare training data
            X = np.array(self.training_data)
            y = np.array(self.performance_history)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.trained = True
            
            # Calculate training score
            score = self.model.score(X_scaled, y)
            logger.info(f"AI model trained - Score: {score:.3f}")
            
            # Save model
            self._save_model()
            
            # Update learning progress
            self.learning_progress = min(100.0, len(self.training_data) / 100 * 100)
            
        except Exception as e:
            logger.error(f"AI training error: {e}")

    async def _optimize_parameters(self):
        """Use AI to optimize mining parameters"""
        if not self.trained:
            return
            
        try:
            # Current parameters
            current_threads = self.current_params['thread_count']
            current_intensity = self.current_params['intensity']
            
            best_score = -1
            best_params = None
            
            # Test different parameter combinations
            thread_options = [
                max(1, current_threads - 2),
                current_threads,
                min(current_threads + 2, self.mining_engine.max_threads)
            ]
            
            intensity_options = [
                max(1, current_intensity - 10),
                current_intensity,
                min(100, current_intensity + 10)
            ]
            
            for threads in thread_options:
                for intensity in intensity_options:
                    # Predict performance for this combination
                    features = [
                        threads,
                        intensity,
                        self.current_params['difficulty'],
                        self.current_params['hashrate'],
                        len(self.performance_history),
                        time.time() % 86400
                    ]
                    
                    features_scaled = self.scaler.transform([features])
                    predicted_score = self.model.predict(features_scaled)[0]
                    
                    if predicted_score > best_score:
                        best_score = predicted_score
                        best_params = {'threads': threads, 'intensity': intensity}
            
            # Apply optimization if significant improvement predicted
            if (best_params and 
                (best_params['threads'] != current_threads or 
                 best_params['intensity'] != current_intensity)):
                
                improvement = (best_score - self.performance_history[-1]) / max(1, self.performance_history[-1]) * 100
                
                if improvement > 5:  # 5% improvement threshold
                    logger.info(f"🎯 AI Optimization: threads={best_params['threads']}, "
                              f"intensity={best_params['intensity']} "
                              f"(predicted {improvement:.1f}% improvement)")
                    
                    # Apply optimizations
                    if best_params['threads'] != current_threads:
                        self.mining_engine.adjust_threads(best_params['threads'])
                    
                    if best_params['intensity'] != current_intensity:
                        await self.mining_engine.adjust_intensity(best_params['intensity'])
            
            # Update optimization progress
            self.optimization_progress = min(100.0, len(self.performance_history) / 50 * 100)
            
        except Exception as e:
            logger.error(f"AI optimization error: {e}")

    def _update_progress(self, iteration: int):
        """Update AI progress indicators"""
        # Learning progress based on data collected
        data_progress = min(100.0, len(self.training_data) / 100 * 100)
        
        # Model quality progress
        model_progress = 100.0 if self.trained else 0.0
        
        # Combined learning progress
        self.learning_progress = (data_progress + model_progress) / 2
        
        # Optimization progress based on iterations and performance
        opt_iterations = min(100, iteration)
        performance_trend = self._calculate_performance_trend()
        
        self.optimization_progress = (opt_iterations + performance_trend) / 2

    def _calculate_performance_trend(self) -> float:
        """Calculate performance improvement trend"""
        if len(self.performance_history) < 10:
            return 0.0
            
        try:
            # Compare recent performance to initial performance
            recent_avg = np.mean(self.performance_history[-10:])
            initial_avg = np.mean(self.performance_history[:10])
            
            if initial_avg > 0:
                improvement = (recent_avg - initial_avg) / initial_avg * 100
                return max(0, min(100, improvement))
            else:
                return 0.0
                
        except:
            return 0.0

    def get_stats(self) -> Dict[str, Any]:
        """Get AI optimizer statistics"""
        return {
            'learning_progress': self.learning_progress,
            'optimization_progress': self.optimization_progress,
            'trained': self.trained,
            'data_samples': len(self.training_data),
            'performance_samples': len(self.performance_history),
            'current_params': self.current_params.copy()
        }

    def predict_optimal_threads(self, intensity: int, difficulty: float) -> int:
        """Predict optimal thread count for given parameters"""
        if not self.trained:
            return self.current_params.get('thread_count', 4)
            
        try:
            features = [
                0,  # Will be replaced by different thread counts
                intensity,
                difficulty,
                self.current_params.get('hashrate', 0),
                len(self.performance_history),
                time.time() % 86400
            ]
            
            best_threads = 1
            best_score = -1
            
            for threads in range(1, min(17, self.mining_engine.max_threads + 1)):
                test_features = features.copy()
                test_features[0] = threads
                
                features_scaled = self.scaler.transform([test_features])
                score = self.model.predict(features_scaled)[0]
                
                if score > best_score:
                    best_score = score
                    best_threads = threads
            
            return best_threads
            
        except Exception as e:
            logger.error(f"Thread prediction error: {e}")
            return self.current_params.get('thread_count', 4)

    def get_learning_metrics(self) -> Dict[str, float]:
        """Get detailed learning metrics for web interface"""
        return {
            'learning_progress': self.learning_progress,
            'optimization_progress': self.optimization_progress,
            'data_quality': min(100.0, len(self.training_data) / 100 * 100),
            'model_accuracy': 100.0 if self.trained else 0.0,
            'performance_trend': self._calculate_performance_trend()
        }