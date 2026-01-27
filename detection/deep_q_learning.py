# detection/deep_q_learning.py
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime
import os


class DQNNetwork(nn.Module):
    """Deep Q-Network for traffic light decision making"""
    
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super(DQNNetwork, self).__init__()
        
        # Neural network architecture
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size * 2)
        self.fc3 = nn.Linear(hidden_size * 2, hidden_size)
        self.fc4 = nn.Linear(hidden_size, output_size)
        
        # Activation functions
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        """Forward pass through the network"""
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x


class ReplayBuffer:
    """Experience replay buffer for DQN training"""
    
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """Add experience to buffer"""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int):
        """Sample a batch of experiences"""
        return random.sample(self.buffer, batch_size)
    
    def __len__(self):
        return len(self.buffer)


class TrafficLightDQN:
    """Deep Q-Learning for intelligent traffic light optimization
    
    This model takes YOLO detection data as input and outputs optimal
    traffic light timing decisions to minimize congestion and wait times.
    """
    
    def __init__(self, 
                 state_size: int = 12,  # Features from YOLO + traffic state
                 action_size: int = 6,   # Different green light durations
                 hidden_size: int = 128,
                 learning_rate: float = 0.001,
                 gamma: float = 0.95,
                 epsilon_start: float = 1.0,
                 epsilon_end: float = 0.01,
                 epsilon_decay: float = 0.995,
                 batch_size: int = 64,
                 buffer_capacity: int = 10000):
        
        self.logger = logging.getLogger(__name__)
        
        # State and action space
        self.state_size = state_size
        self.action_size = action_size
        
        # Device configuration
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.logger.info(f"Using device: {self.device}")
        
        # Neural networks
        self.policy_net = DQNNetwork(state_size, hidden_size, action_size).to(self.device)
        self.target_net = DQNNetwork(state_size, hidden_size, action_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Optimizer and loss
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
        
        # Hyperparameters
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        
        # Experience replay
        self.memory = ReplayBuffer(buffer_capacity)
        
        # Traffic light timing parameters (in seconds)
        self.min_green_time = 15
        self.max_green_time = 90
        self.yellow_time = 3
        self.all_red_time = 2
        
        # Training statistics
        self.training_step = 0
        self.episode_rewards = []
        self.losses = []
        
        self.logger.info(f"TrafficLightDQN initialized with state_size={state_size}, action_size={action_size}")
    
    def preprocess_yolo_data(self, yolo_detections: List[Dict], lane_id: int = 0) -> np.ndarray:
        """Convert YOLO detection data to state vector
        
        Args:
            yolo_detections: List of vehicle detections from YOLO
            lane_id: Current lane identifier (0-3 for 4-way intersection)
            
        Returns:
            State vector as numpy array
        """
        # Count vehicles by type
        cars = sum(1 for d in yolo_detections if d.get('class_name') == 'car')
        buses = sum(1 for d in yolo_detections if d.get('class_name') == 'bus')
        trucks = sum(1 for d in yolo_detections if d.get('class_name') == 'truck')
        motorcycles = sum(1 for d in yolo_detections if d.get('class_name') == 'motorcycle')
        bicycles = sum(1 for d in yolo_detections if d.get('class_name') == 'bicycle')
        
        total_vehicles = len(yolo_detections)
        
        # Calculate average confidence
        avg_confidence = np.mean([d.get('confidence', 0) for d in yolo_detections]) if yolo_detections else 0
        
        # Estimate queue length based on vehicle positions
        if yolo_detections:
            y_positions = [d.get('center', (0, 0))[1] for d in yolo_detections]
            queue_length = max(y_positions) - min(y_positions) if len(y_positions) > 1 else 0
        else:
            queue_length = 0
        
        # Normalize queue length (assuming max frame height of 1080)
        normalized_queue = queue_length / 1080.0
        
        # Create state vector (12 features)
        state = np.array([
            total_vehicles / 50.0,      # Normalized total vehicle count
            cars / 30.0,                 # Normalized car count
            buses / 5.0,                 # Normalized bus count
            trucks / 5.0,                # Normalized truck count
            motorcycles / 10.0,          # Normalized motorcycle count
            bicycles / 10.0,             # Normalized bicycle count
            avg_confidence,              # Average detection confidence
            normalized_queue,            # Normalized queue length
            lane_id / 3.0,              # Normalized lane ID
            0.0,                        # Current phase time (to be filled)
            0.0,                        # Time since last change (to be filled)
            0.0                         # Current signal state (to be filled)
        ], dtype=np.float32)
        
        return state
    
    def get_action(self, state: np.ndarray, training: bool = True) -> int:
        """Select action using epsilon-greedy policy
        
        Args:
            state: Current state vector
            training: Whether in training mode (uses exploration)
            
        Returns:
            Action index (0 to action_size-1)
        """
        # Exploration
        if training and random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        
        # Exploitation
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor)
            return q_values.argmax().item()
    
    def action_to_green_time(self, action: int) -> int:
        """Convert action index to green light duration
        
        Args:
            action: Action index (0 to action_size-1)
            
        Returns:
            Green light duration in seconds
        """
        # Map actions to green times
        time_range = self.max_green_time - self.min_green_time
        green_time = self.min_green_time + (action * time_range / (self.action_size - 1))
        return int(green_time)
    
    def calculate_reward(self, 
                        prev_vehicle_count: int,
                        curr_vehicle_count: int,
                        avg_wait_time: float,
                        throughput: int,
                        action: int) -> float:
        """Calculate reward for the taken action
        
        Reward components:
        - Negative reward for vehicles waiting
        - Positive reward for reducing queue
        - Positive reward for throughput
        - Penalty for very long or very short green times
        
        Args:
            prev_vehicle_count: Vehicle count before action
            curr_vehicle_count: Vehicle count after action
            avg_wait_time: Average waiting time in seconds
            throughput: Number of vehicles that passed
            action: Action taken
            
        Returns:
            Reward value
        """
        # Queue reduction reward
        queue_reduction = prev_vehicle_count - curr_vehicle_count
        queue_reward = queue_reduction * 2.0
        
        # Throughput reward
        throughput_reward = throughput * 1.5
        
        # Wait time penalty
        wait_penalty = -avg_wait_time * 0.5
        
        # Penalty for extreme green times
        green_time = self.action_to_green_time(action)
        if green_time < 20 or green_time > 80:
            time_penalty = -5.0
        else:
            time_penalty = 0.0
        
        # Total reward
        total_reward = queue_reward + throughput_reward + wait_penalty + time_penalty
        
        return total_reward
    
    def store_transition(self, state, action, reward, next_state, done):
        """Store transition in replay buffer"""
        self.memory.push(state, action, reward, next_state, done)
    
    def train_step(self):
        """Perform one training step"""
        if len(self.memory) < self.batch_size:
            return None
        
        # Sample batch from memory
        batch = self.memory.sample(self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # Convert to tensors
        states = torch.FloatTensor(np.array(states)).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(np.array(next_states)).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Current Q values
        current_q_values = self.policy_net(states).gather(1, actions.unsqueeze(1))
        
        # Next Q values from target network
        with torch.no_grad():
            next_q_values = self.target_net(next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        # Compute loss
        loss = self.criterion(current_q_values.squeeze(), target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()
        
        # Update statistics
        self.training_step += 1
        self.losses.append(loss.item())
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        
        return loss.item()
    
    def update_target_network(self):
        """Update target network with policy network weights"""
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.logger.info("Target network updated")
    
    def predict_signal_timing(self, yolo_detections: List[Dict], lane_id: int = 0) -> Dict:
        """Predict optimal signal timing based on YOLO detections
        
        Args:
            yolo_detections: List of vehicle detections from YOLO
            lane_id: Current lane identifier
            
        Returns:
            Dictionary with timing recommendations
        """
        # Preprocess YOLO data to state
        state = self.preprocess_yolo_data(yolo_detections, lane_id)
        
        # Get action (no exploration in prediction)
        action = self.get_action(state, training=False)
        
        # Convert action to timing
        green_time = self.action_to_green_time(action)
        
        # Calculate confidence based on Q-value
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor)
            max_q = q_values.max().item()
            confidence = min(1.0, max(0.0, (max_q + 10) / 20))  # Normalize Q-value to [0, 1]
        
        return {
            "lane_id": lane_id,
            "action": action,
            "green_time": green_time,
            "yellow_time": self.yellow_time,
            "all_red_time": self.all_red_time,
            "total_cycle_time": green_time + self.yellow_time + self.all_red_time,
            "vehicle_count": len(yolo_detections),
            "confidence": confidence,
            "epsilon": self.epsilon,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_model(self, filepath: str):
        """Save model to file"""
        try:
            import os
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            checkpoint = {
                'policy_net_state_dict': self.policy_net.state_dict(),
                'target_net_state_dict': self.target_net.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'epsilon': self.epsilon,
                'training_step': self.training_step,
                'episode_rewards': self.episode_rewards,
                'losses': self.losses[-1000:],  # Save last 1000 losses
                'hyperparameters': {
                    'state_size': self.state_size,
                    'action_size': self.action_size,
                    'gamma': self.gamma,
                    'batch_size': self.batch_size
                }
            }
            torch.save(checkpoint, filepath)
            self.logger.info(f"Model saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
    
    def load_model(self, filepath: str):
        """Load model from file"""
        try:
            checkpoint = torch.load(filepath, map_location=self.device)
            self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
            self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.epsilon = checkpoint.get('epsilon', self.epsilon_end)
            self.training_step = checkpoint.get('training_step', 0)
            self.episode_rewards = checkpoint.get('episode_rewards', [])
            self.losses = checkpoint.get('losses', [])
            self.logger.info(f"Model loaded from {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
    
    def get_training_stats(self) -> Dict:
        """Get training statistics"""
        return {
            "training_steps": self.training_step,
            "epsilon": self.epsilon,
            "avg_loss": np.mean(self.losses[-100:]) if self.losses else 0,
            "avg_reward": np.mean(self.episode_rewards[-100:]) if self.episode_rewards else 0,
            "memory_size": len(self.memory),
            "device": str(self.device)
        }
