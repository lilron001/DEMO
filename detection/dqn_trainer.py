# detection/dqn_trainer.py
"""
Training script for Deep Q-Learning traffic light optimization
This module handles the training loop and simulation environment
"""

import logging
import numpy as np
from typing import Dict, List
from datetime import datetime
import json
import os

from .deep_q_learning import TrafficLightDQN
from .yolo_detector import YOLODetector


class TrafficSimulator:
    """Simulates traffic environment for DQN training"""
    
    def __init__(self, num_lanes: int = 4):
        self.logger = logging.getLogger(__name__)
        self.num_lanes = num_lanes
        self.reset()
    
    def reset(self):
        """Reset simulation state"""
        self.lane_queues = [np.random.randint(0, 30) for _ in range(self.num_lanes)]
        self.wait_times = [0.0 for _ in range(self.num_lanes)]
        self.current_lane = 0
        self.time_step = 0
        return self.get_state()
    
    def get_state(self) -> Dict:
        """Get current simulation state"""
        return {
            'lane_queues': self.lane_queues.copy(),
            'wait_times': self.wait_times.copy(),
            'current_lane': self.current_lane,
            'time_step': self.time_step
        }
    
    def step(self, action: int, green_time: int) -> tuple:
        """Execute action and return next state, reward, done
        
        Args:
            action: Action index
            green_time: Green light duration in seconds
            
        Returns:
            (next_state, reward, done, info)
        """
        prev_queue = self.lane_queues[self.current_lane]
        
        # Vehicles pass through during green time
        # Assume 1 vehicle per 3 seconds can pass
        vehicles_passed = min(self.lane_queues[self.current_lane], green_time // 3)
        self.lane_queues[self.current_lane] -= vehicles_passed
        
        # New vehicles arrive at other lanes
        for i in range(self.num_lanes):
            if i != self.current_lane:
                # Random arrivals (0-3 vehicles)
                arrivals = np.random.poisson(1.5)
                self.lane_queues[i] = min(50, self.lane_queues[i] + arrivals)
                self.wait_times[i] += green_time
        
        # Reset wait time for current lane
        self.wait_times[self.current_lane] = 0
        
        # Calculate reward
        avg_wait = np.mean(self.wait_times)
        total_queue = sum(self.lane_queues)
        
        reward = (
            vehicles_passed * 2.0  # Reward for throughput
            - avg_wait * 0.1       # Penalty for wait time
            - total_queue * 0.5    # Penalty for queue length
        )
        
        # Move to next lane
        self.current_lane = (self.current_lane + 1) % self.num_lanes
        self.time_step += 1
        
        # Episode ends after full cycle through all lanes
        done = (self.time_step % (self.num_lanes * 4) == 0)
        
        info = {
            'vehicles_passed': vehicles_passed,
            'prev_queue': prev_queue,
            'curr_queue': self.lane_queues[self.current_lane],
            'avg_wait': avg_wait,
            'total_queue': total_queue
        }
        
        return self.get_state(), reward, done, info


class DQNTrainer:
    """Trainer for Deep Q-Learning traffic light optimization"""
    
    def __init__(self, 
                 model: TrafficLightDQN,
                 save_dir: str = "models/dqn"):
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.save_dir = save_dir
        self.simulator = TrafficSimulator()
        
        # Create save directory
        os.makedirs(save_dir, exist_ok=True)
        
        self.logger.info("DQN Trainer initialized")
    
    def train(self, 
              num_episodes: int = 1000,
              target_update_freq: int = 10,
              save_freq: int = 100,
              verbose: bool = True):
        """Train the DQN model
        
        Args:
            num_episodes: Number of training episodes
            target_update_freq: Frequency of target network updates
            save_freq: Frequency of model saves
            verbose: Whether to print progress
        """
        self.logger.info(f"Starting training for {num_episodes} episodes")
        
        episode_rewards = []
        episode_lengths = []
        
        for episode in range(num_episodes):
            state_dict = self.simulator.reset()
            episode_reward = 0
            episode_length = 0
            done = False
            
            while not done:
                # Create mock YOLO detections based on queue
                mock_detections = self._create_mock_detections(
                    state_dict['lane_queues'][state_dict['current_lane']]
                )
                
                # Get state from YOLO data
                state = self.model.preprocess_yolo_data(
                    mock_detections,
                    state_dict['current_lane']
                )
                
                # Select action
                action = self.model.get_action(state, training=True)
                green_time = self.model.action_to_green_time(action)
                
                # Execute action
                next_state_dict, reward, done, info = self.simulator.step(action, green_time)
                
                # Get next state
                next_mock_detections = self._create_mock_detections(
                    next_state_dict['lane_queues'][next_state_dict['current_lane']]
                )
                next_state = self.model.preprocess_yolo_data(
                    next_mock_detections,
                    next_state_dict['current_lane']
                )
                
                # Store transition
                self.model.store_transition(state, action, reward, next_state, done)
                
                # Train
                loss = self.model.train_step()
                
                episode_reward += reward
                episode_length += 1
                state_dict = next_state_dict
            
            # Update target network
            if (episode + 1) % target_update_freq == 0:
                self.model.update_target_network()
            
            # Save model
            if (episode + 1) % save_freq == 0:
                model_path = os.path.join(self.save_dir, f"dqn_episode_{episode+1}.pth")
                self.model.save_model(model_path)
            
            # Track statistics
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
            self.model.episode_rewards.append(episode_reward)
            
            # Print progress
            if verbose and (episode + 1) % 10 == 0:
                avg_reward = np.mean(episode_rewards[-10:])
                avg_length = np.mean(episode_lengths[-10:])
                stats = self.model.get_training_stats()
                
                self.logger.info(
                    f"Episode {episode+1}/{num_episodes} | "
                    f"Avg Reward: {avg_reward:.2f} | "
                    f"Avg Length: {avg_length:.1f} | "
                    f"Epsilon: {stats['epsilon']:.3f} | "
                    f"Loss: {stats['avg_loss']:.4f}"
                )
        
        # Save final model
        final_path = os.path.join(self.save_dir, "dqn_final.pth")
        self.model.save_model(final_path)
        
        # Save training history
        history = {
            'episode_rewards': episode_rewards,
            'episode_lengths': episode_lengths,
            'final_stats': self.model.get_training_stats(),
            'timestamp': datetime.now().isoformat()
        }
        
        history_path = os.path.join(self.save_dir, "training_history.json")
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=2)
        
        self.logger.info(f"Training completed. Model saved to {final_path}")
        
        return history
    
    def _create_mock_detections(self, num_vehicles: int) -> List[Dict]:
        """Create mock YOLO detections for simulation
        
        Args:
            num_vehicles: Number of vehicles to simulate
            
        Returns:
            List of mock detection dictionaries
        """
        detections = []
        
        for i in range(num_vehicles):
            # Randomly assign vehicle types
            vehicle_types = ['car', 'bus', 'truck', 'motorcycle', 'bicycle']
            weights = [0.7, 0.1, 0.1, 0.05, 0.05]
            vehicle_type = np.random.choice(vehicle_types, p=weights)
            
            # Mock bounding box (simulating queue formation)
            y_pos = 500 + i * 30  # Vehicles stack vertically
            detection = {
                'class_name': vehicle_type,
                'confidence': 0.85 + np.random.random() * 0.15,
                'bbox': (400, y_pos, 600, y_pos + 100),
                'center': (500, y_pos + 50)
            }
            detections.append(detection)
        
        return detections
    
    def evaluate(self, num_episodes: int = 10) -> Dict:
        """Evaluate trained model
        
        Args:
            num_episodes: Number of evaluation episodes
            
        Returns:
            Evaluation statistics
        """
        self.logger.info(f"Evaluating model for {num_episodes} episodes")
        
        episode_rewards = []
        episode_lengths = []
        total_throughput = []
        
        for episode in range(num_episodes):
            state_dict = self.simulator.reset()
            episode_reward = 0
            episode_length = 0
            throughput = 0
            done = False
            
            while not done:
                mock_detections = self._create_mock_detections(
                    state_dict['lane_queues'][state_dict['current_lane']]
                )
                
                state = self.model.preprocess_yolo_data(
                    mock_detections,
                    state_dict['current_lane']
                )
                
                # Use greedy policy (no exploration)
                action = self.model.get_action(state, training=False)
                green_time = self.model.action_to_green_time(action)
                
                next_state_dict, reward, done, info = self.simulator.step(action, green_time)
                
                episode_reward += reward
                episode_length += 1
                throughput += info['vehicles_passed']
                state_dict = next_state_dict
            
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
            total_throughput.append(throughput)
        
        eval_stats = {
            'avg_reward': float(np.mean(episode_rewards)),
            'std_reward': float(np.std(episode_rewards)),
            'avg_length': float(np.mean(episode_lengths)),
            'avg_throughput': float(np.mean(total_throughput)),
            'num_episodes': num_episodes
        }
        
        self.logger.info(f"Evaluation complete: Avg Reward = {eval_stats['avg_reward']:.2f}")
        
        return eval_stats


def train_dqn_model(num_episodes: int = 1000, save_dir: str = "models/dqn"):
    """Convenience function to train a new DQN model
    
    Args:
        num_episodes: Number of training episodes
        save_dir: Directory to save models
        
    Returns:
        Trained model and training history
    """
    # Initialize model
    model = TrafficLightDQN(
        state_size=12,
        action_size=6,
        hidden_size=128,
        learning_rate=0.001
    )
    
    # Initialize trainer
    trainer = DQNTrainer(model, save_dir=save_dir)
    
    # Train
    history = trainer.train(num_episodes=num_episodes, verbose=True)
    
    # Evaluate
    eval_stats = trainer.evaluate(num_episodes=20)
    
    return model, history, eval_stats
