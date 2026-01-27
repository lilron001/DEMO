# detection/traffic_controller.py
"""
Integrated Traffic Light Controller
Combines YOLO detection with Deep Q-Learning for intelligent traffic management
"""

import logging
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import threading
import time

from .yolo_detector import YOLODetector
from .deep_q_learning import TrafficLightDQN


class TrafficLightController:
    """Intelligent traffic light controller using YOLO + DQN
    
    This class integrates:
    1. YOLO object detection for vehicle counting and tracking
    2. Deep Q-Learning for optimal signal timing decisions
    3. Real-time traffic light control logic
    """
    
    def __init__(self, 
                 num_lanes: int = 4,
                 model_path: Optional[str] = None,
                 use_pretrained: bool = True):
        """
        Args:
            num_lanes: Number of lanes/directions at intersection
            model_path: Path to pre-trained DQN model
            use_pretrained: Whether to load pre-trained model
        """
        self.logger = logging.getLogger(__name__)
        self.num_lanes = num_lanes
        
        # Initialize YOLO detector
        self.yolo = YOLODetector()
        
        # Initialize DQN model
        self.dqn = TrafficLightDQN(
            state_size=12,
            action_size=6,
            hidden_size=128
        )
        
        # Load pre-trained model if available
        if use_pretrained and model_path:
            try:
                self.dqn.load_model(model_path)
                self.logger.info(f"Loaded pre-trained model from {model_path}")
            except Exception as e:
                self.logger.warning(f"Could not load model: {e}. Using untrained model.")
        
        # Traffic state
        self.current_lane = 0
        self.current_phase = 'red'  # red, green, yellow
        self.phase_start_time = datetime.now()
        self.phase_duration = 30  # seconds
        self.green_check_done = False  # Flag for 15s observation check
        
        # Lane statistics
        self.lane_stats = {
            i: {
                'vehicle_count': 0,
                'wait_time': 0.0,
                'throughput': 0,
                'last_detection': None,
                'detections_history': []
            }
            for i in range(num_lanes)
        }
        
        # Control parameters
        self.min_cycle_time = 60  # Minimum total cycle time
        self.max_cycle_time = 240  # Maximum total cycle time
        self.emergency_threshold = 40  # Vehicle count for emergency override
        
        # Performance tracking
        self.decisions_made = 0
        self.total_vehicles_processed = 0
        self.avg_wait_time = 0.0
        
        self.logger.info(f"TrafficLightController initialized with {num_lanes} lanes")
    
    def process_camera_frame(self, frame: np.ndarray, lane_id: int) -> Dict:
        """Process camera frame for a specific lane
        
        Args:
            frame: Camera frame (numpy array)
            lane_id: Lane identifier (0 to num_lanes-1)
            
        Returns:
            Processing results including detections and recommendations
        """
        # Detect vehicles using YOLO
        detections = self.yolo.detect_vehicles(frame)
        
        # Update lane statistics
        self.lane_stats[lane_id]['vehicle_count'] = len(detections)
        self.lane_stats[lane_id]['last_detection'] = datetime.now()
        self.lane_stats[lane_id]['detections_history'].append({
            'timestamp': datetime.now().isoformat(),
            'count': len(detections),
            'detections': detections
        })
        
        # Keep only last 100 detections
        if len(self.lane_stats[lane_id]['detections_history']) > 100:
            self.lane_stats[lane_id]['detections_history'].pop(0)
        
        # Get DQN recommendation
        timing_recommendation = self.dqn.predict_signal_timing(detections, lane_id)
        
        return {
            'lane_id': lane_id,
            'detections': detections,
            'vehicle_count': len(detections),
            'timing_recommendation': timing_recommendation,
            'timestamp': datetime.now().isoformat()
        }
    
    def make_decision(self) -> Dict:
        """Make traffic light decision based on all lanes
        
        Returns:
            Decision dictionary with next phase and timing
        """
        # Collect current state from all lanes
        lane_vehicle_counts = [
            self.lane_stats[i]['vehicle_count'] 
            for i in range(self.num_lanes)
        ]
        
        # Find lane with most vehicles
        max_queue_lane = np.argmax(lane_vehicle_counts)
        max_queue_count = lane_vehicle_counts[max_queue_lane]
        
        # Emergency override for very long queues
        if max_queue_count >= self.emergency_threshold:
            self.logger.warning(f"Emergency override: Lane {max_queue_lane} has {max_queue_count} vehicles")
            next_lane = max_queue_lane
            green_time = self.dqn.max_green_time  # Use max time for emergency
            self.green_check_done = True  # Skip observation for emergency
        else:
            # Normal operation: use round-robin
            next_lane = (self.current_lane + 1) % self.num_lanes
            
            # Get current detections for next lane
            if self.lane_stats[next_lane]['detections_history']:
                last_detection = self.lane_stats[next_lane]['detections_history'][-1]
                detections = last_detection['detections']
                vehicle_count = last_detection['count']
            else:
                detections = []
                vehicle_count = 0
            
            # Call DQN just for logging/stats, but ignore its timing recommendation
            timing = self.dqn.predict_signal_timing(detections, next_lane)
            
            # RULE-BASED LOGIC (User Override)
            # High congestion (>20): 40s (30 + 10)
            # Low congestion (<=5): 15s
            # Normal: 30s
            if vehicle_count > 20: 
                green_time = 40
            elif vehicle_count <= 5:
                green_time = 15
            else:
                green_time = 30
                
            self.green_check_done = True # checking done upfront
        
        # Calculate full cycle timing
        yellow_time = self.dqn.yellow_time
        all_red_time = self.dqn.all_red_time
        total_time = green_time + yellow_time + all_red_time
        
        # Update state
        self.current_lane = next_lane
        self.current_phase = 'green'
        self.phase_start_time = datetime.now()
        self.phase_duration = green_time
        self.decisions_made += 1
        
        decision = {
            'decision_id': self.decisions_made,
            'lane_id': next_lane,
            'phase': 'green',
            'green_time': green_time,
            'yellow_time': yellow_time,
            'all_red_time': all_red_time,
            'total_cycle_time': total_time,
            'vehicle_count': lane_vehicle_counts[next_lane],
            'all_lane_counts': lane_vehicle_counts,
            'is_emergency': max_queue_count >= self.emergency_threshold,
            'timestamp': datetime.now().isoformat(),
            'dqn_confidence': timing.get('confidence', 0.5) if 'timing' in locals() else 0.5
        }
        
        self.logger.info(
            f"Decision #{self.decisions_made}: Lane {next_lane} GREEN for {green_time}s "
            f"({lane_vehicle_counts[next_lane]} vehicles)"
        )
        
        return decision
    
    def update_phase(self) -> Optional[Dict]:
        """Update current traffic light phase based on time
        
        Returns:
            Phase update dictionary if phase changed, None otherwise
        """
        elapsed = (datetime.now() - self.phase_start_time).total_seconds()
        
        # DQN Dynamic adjustment logic DISABLED as per user request to use fixed rule-based times
        # if self.current_phase == 'green' and not self.green_check_done and elapsed >= 15:
        #    ... (logic commented out)
        
        if elapsed >= self.phase_duration:
            # Phase transition
            if self.current_phase == 'green':
                # Green -> Yellow
                self.current_phase = 'yellow'
                self.phase_start_time = datetime.now()
                self.phase_duration = self.dqn.yellow_time
                
                return {
                    'lane_id': self.current_lane,
                    'phase': 'yellow',
                    'duration': self.phase_duration,
                    'timestamp': datetime.now().isoformat()
                }
            
            elif self.current_phase == 'yellow':
                # Yellow -> All Red
                self.current_phase = 'all_red'
                self.phase_start_time = datetime.now()
                self.phase_duration = self.dqn.all_red_time
                
                return {
                    'lane_id': self.current_lane,
                    'phase': 'all_red',
                    'duration': self.phase_duration,
                    'vehicle_count': self.lane_stats[self.current_lane]['vehicle_count'],
                    'timestamp': datetime.now().isoformat()
                }
            
            elif self.current_phase == 'all_red':
                # All Red -> Make new decision
                return self.make_decision()
        
        return None
    
    def get_current_status(self) -> Dict:
        """Get current traffic light status
        
        Returns:
            Status dictionary
        """
        elapsed = (datetime.now() - self.phase_start_time).total_seconds()
        remaining = max(0, self.phase_duration - elapsed)
        
        return {
            'current_lane': self.current_lane,
            'current_phase': self.current_phase,
            'phase_elapsed': elapsed,
            'phase_remaining': remaining,
            'lane_stats': self.lane_stats,
            'decisions_made': self.decisions_made,
            'total_vehicles_processed': self.total_vehicles_processed,
            'dqn_stats': self.dqn.get_training_stats(),
            'timestamp': datetime.now().isoformat()
        }
    
    def train_from_experience(self, 
                             state: np.ndarray,
                             action: int,
                             reward: float,
                             next_state: np.ndarray,
                             done: bool = False):
        """Store experience and train DQN model
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
        """
        self.dqn.store_transition(state, action, reward, next_state, done)
        loss = self.dqn.train_step()
        
        if loss is not None:
            self.logger.debug(f"DQN training step: loss={loss:.4f}")
    
    def calculate_performance_metrics(self) -> Dict:
        """Calculate overall performance metrics
        
        Returns:
            Performance metrics dictionary
        """
        total_vehicles = sum(
            self.lane_stats[i]['vehicle_count'] 
            for i in range(self.num_lanes)
        )
        
        total_throughput = sum(
            self.lane_stats[i]['throughput'] 
            for i in range(self.num_lanes)
        )
        
        avg_queue_length = total_vehicles / self.num_lanes if self.num_lanes > 0 else 0
        
        # Calculate efficiency (throughput / decisions)
        efficiency = total_throughput / self.decisions_made if self.decisions_made > 0 else 0
        
        return {
            'total_vehicles_waiting': total_vehicles,
            'total_throughput': total_throughput,
            'avg_queue_length': avg_queue_length,
            'efficiency': efficiency,
            'decisions_made': self.decisions_made,
            'dqn_epsilon': self.dqn.epsilon,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_model(self, filepath: str):
        """Save DQN model"""
        import os
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.dqn.save_model(filepath)
        self.logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load DQN model"""
        self.dqn.load_model(filepath)
        self.logger.info(f"Model loaded from {filepath}")
