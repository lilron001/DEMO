# controllers/main_controller.py
import tkinter as tk
import threading
import time
import cv2
import numpy as np
import logging
from datetime import datetime
from detection.camera_manager import CameraManager
from detection.traffic_controller import TrafficLightController
from detection.yolo_detector import YOLODetector
from views.pages import (
    DashboardPage, TrafficReportsPage, IncidentHistoryPage,
    ViolationLogsPage, AnalyticsPage, SettingsPage, IssueReportsPage, AdminUsersPage
)

class MainController:
    """Main application controller with 4-way camera and AI integration"""
    
    def __init__(self, root, view, db=None, current_user=None, auth_controller=None, on_logout_callback=None):
        self.root = root
        self.view = view
        self.db = db
        self.current_user = current_user
        self.auth_controller = auth_controller
        self.on_logout_callback = on_logout_callback
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Navigation tracking
        self.current_page = None
        self.pages = {}
        
        # Directions configuration (map to lane IDs)
        self.directions = ['north', 'south', 'east', 'west']
        self.direction_to_lane = {
            'north': 0,
            'south': 1,
            'east': 2,
            'west': 3
        }
        
        # Camera Managers (0, 1, 2, 3)
        self.camera_managers = {}
        for i, direction in enumerate(self.directions):
            self.camera_managers[direction] = CameraManager(camera_index=i)
            
        # Initialize YOLO and DQN-based Traffic Controller
        self.yolo_detector = YOLODetector("yolov8n.pt")
        self.traffic_controller = TrafficLightController(
            num_lanes=4,
            model_path=None,  # Will use untrained model initially
            use_pretrained=False
        )
        
        # Traffic States for each direction
        self.states = {}
        for direction in self.directions:
            self.states[direction] = {
                'signal_state': 'RED',
                'time_remaining': 0,
                'last_update_time': time.time(),
                'vehicle_count': 0,
                'detections': [],
                'phase_start_time': time.time()
            }
        
        # North starts green (will be managed by camera_loop state machine)
        self.states['north']['signal_state'] = 'GREEN'
        self.states['north']['time_remaining'] = 30
        
        self.logger.info("Initial traffic state: NORTH → GREEN (30s)")
        
        # Threading
        self.camera_thread = None
        self.is_running = True
        
        self.logger.info("MainController initialized with DQN traffic control")
    
    def initialize_pages(self):
        """Initialize all application pages"""
        if self.view and hasattr(self.view, 'content_area'):
            self.pages['dashboard'] = DashboardPage(self.view.content_area)
            self.pages['issue_reports'] = IssueReportsPage(self.view.content_area, self.db, self.current_user)
            self.pages['traffic_reports'] = TrafficReportsPage(self.view.content_area)
            self.pages['incident_history'] = IncidentHistoryPage(self.view.content_area)
            self.pages['violation_logs'] = ViolationLogsPage(self.view.content_area)
            self.pages['analytics'] = AnalyticsPage(self.view.content_area)
            self.pages['settings'] = SettingsPage(self.view.content_area)
            
            # Admin Pages
            if self.current_user and self.current_user.get('role') == 'admin':
                if self.auth_controller:
                    self.pages['admin_users'] = AdminUsersPage(self.view.content_area, self.auth_controller)
    
    def update_sidebar_navigation(self):
        """Update sidebar with proper navigation callback after view is ready"""
        if self.view and hasattr(self.view, 'sidebar'):
            self.view.sidebar.on_nav_click = self.handle_navigation
    
    def handle_navigation(self, page_name):
        """Handle page navigation"""
        try:
            if page_name in self.pages:
                if self.current_page:
                    try:
                        self.current_page.get_widget().pack_forget()
                    except:
                        pass
                
                page = self.pages[page_name]
                page.get_widget().pack(fill=tk.BOTH, expand=True)
                self.current_page = page
        except Exception as e:
            print(f"Navigation error: {e}")
    
    def start_camera_feed(self):
        """Start camera feeds in background thread"""
        # Initialize all cameras
        for i, direction in enumerate(self.directions):
            self.camera_managers[direction].initialize_camera(i)
            
        self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
        self.camera_thread.start()
        
        self.logger.info("Camera feed started with DQN traffic control")
    
    def camera_loop(self):
        """Background thread for camera processing with DQN decision making"""
        
        self.logger.info("🚀 CAMERA LOOP STARTED!")
        
        # Simple state machine for traffic lights
        cycle_state = {
            'current_lane': 0,  # 0=north, 1=south, 2=east, 3=west
            'phase': 'green',   # green, yellow, all_red
            'phase_start': time.time(),
            'phase_start': time.time(),
            'phase_duration': 15,  # Start with 15s green (observation period)
            'green_check_done': False, # Flag for observation check
        }
        
        self.logger.info(f"🟢 Initial: {self.directions[0].upper()} → GREEN ({cycle_state['phase_duration']}s) [Observing]")
        
        loop_count = 0
        last_status_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            loop_count += 1
            
            # Status update every 5 seconds
            if current_time - last_status_time >= 5.0:
                elapsed = current_time - cycle_state['phase_start']
                remaining = cycle_state['phase_duration'] - elapsed
                self.logger.info(
                    f"📊 Loop #{loop_count} | Phase: {cycle_state['phase'].upper()} | "
                    f"Lane: {self.directions[cycle_state['current_lane']].upper()} | "
                    f"Remaining: {remaining:.1f}s"
                )
                last_status_time = current_time

            
            # Step 1: Process all cameras and collect YOLO detections
            all_lane_counts = []
            for direction in self.directions:
                try:
                    state = self.states[direction]
                    lane_id = self.direction_to_lane[direction]
                    
                    # Get Frame
                    frame = self.camera_managers[direction].get_frame()
                    if frame is None:
                        # Create blank frame for demo
                        frame = np.zeros((480, 640, 3), dtype=np.uint8)
                        
                        # SIMULATOR: Generate fake traffic for 3 cameras (North, South, East)
                        detections = []
                        if direction in ['north', 'south', 'east']:
                            # Generate random count using stable random to avoid flickering
                            import random
                            base_count = {'north': 15, 'south': 8, 'east': 12}.get(direction, 0)
                            count = max(0, base_count + random.randint(-2, 2))
                            
                            # Create fake detections
                            for _ in range(count):
                                detections.append({
                                    'class_name': 'car', 
                                    'confidence': 0.95,
                                    'box': [0, 0, 50, 50],
                                    'center': (random.randint(100, 500), random.randint(100, 400))
                                })
                            
                            cv2.putText(frame, f"SIMULATION: {count} vehicles", (50, 240), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        else:
                             cv2.putText(frame, "No Signal - No Traffic", (150, 240), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        
                        annotated_frame = frame
                    else:
                        # Run YOLO detection ONCE
                        detection_result = self.yolo_detector.detect(frame)
                        detections = detection_result.get("detections", [])
                        annotated_frame = detection_result.get('annotated_frame', frame)
                    
                    # Store detections
                    state['detections'] = detections
                    state['vehicle_count'] = len(detections)
                    all_lane_counts.append(len(detections))
                    
                    # Log vehicle detections (only if count > 0 to avoid spam)
                    if len(detections) > 0:
                        self.logger.info(f"📹 {direction.upper()}: Detected {len(detections)} vehicles")
                    
                    # Update traffic controller lane stats
                    self.traffic_controller.lane_stats[lane_id]['vehicle_count'] = len(detections)
                    self.traffic_controller.lane_stats[lane_id]['last_detection'] = datetime.now()
                    
                    # Update dashboard display safely on main thread
                    if self.current_page and hasattr(self.current_page, 'update_camera_feed'):
                        dash_data = {
                            'vehicle_count': state['vehicle_count'],
                            'signal_state': state['signal_state'],
                            'time_remaining': max(0, state['time_remaining'])
                        }
                        
                        # Create a copy of the frame to avoid race conditions
                        frame_copy = annotated_frame.copy() if annotated_frame is not None else None
                        
                        # Schedule UI update on main thread
                        self.root.after(0, lambda f=frame_copy, d=dash_data, dir=direction: 
                            self.current_page.update_camera_feed(f, d, dir) 
                            if self.current_page and hasattr(self.current_page, 'update_camera_feed') else None
                        )
                        
                except Exception as e:
                    self.logger.error(f"Error processing camera ({direction}): {e}", exc_info=True)
                    all_lane_counts.append(0)
            
            # Update Analytics Page (if active)
            # We do this once per cycle to keep graph time-aligned
            if self.current_page and hasattr(self.current_page, 'update_analytics'):
                analytics_data = {
                    d: self.states[d]['vehicle_count'] for d in self.directions
                }
                self.root.after(0, lambda d=analytics_data: 
                    self.current_page.update_analytics(d) 
                    if self.current_page and hasattr(self.current_page, 'update_analytics') else None
                )

            # Step 2: Simple traffic light state machine
            try:
                elapsed = current_time - cycle_state['phase_start']
                
                # Dynamic adjustment removed - Using strict High/Low logic instead
                # (Block removed)

                # Check if phase should change
                if elapsed >= cycle_state['phase_duration']:
                    current_lane = cycle_state['current_lane']
                    current_phase = cycle_state['phase']
                    
                    if current_phase == 'green':
                        # Green → Yellow
                        cycle_state['phase'] = 'yellow'
                        cycle_state['phase_start'] = current_time
                        cycle_state['phase_duration'] = 3  # 3 seconds yellow
                        
                        self.logger.info(f"🟡 {self.directions[current_lane].upper()} → YELLOW (3s)")
                        
                        # Update states
                        self.states[self.directions[current_lane]]['signal_state'] = 'YELLOW'
                        self.states[self.directions[current_lane]]['time_remaining'] = 3
                        
                    elif current_phase == 'yellow':
                        # Yellow → All Red
                        cycle_state['phase'] = 'all_red'
                        cycle_state['phase_start'] = current_time
                        cycle_state['phase_duration'] = 2  # 2 seconds all red
                        
                        self.logger.info(f"🔴 ALL LANES → RED (clearance 2s)")
                        
                        # All lanes red
                        for direction in self.directions:
                            self.states[direction]['signal_state'] = 'RED'
                            self.states[direction]['time_remaining'] = 2
                            
                    elif current_phase == 'all_red':
                        # All Red → Pick next lane (Strict Sequential Round Robin)
                        next_lane = (current_lane + 1) % 4
                        
                        # Determine Duration based on Congestion (Simulate DQN High/Low decision)
                        # Threshold: 20 vehicles considered "High Congestion"
                        # High Congestion = 60s
                        # Low Congestion = 30s
                        # Observation: We check congestion NOW to decide duration. 
                        # This models the "check 15s window" by effectively using the accumulated count.
                        
                        vehicle_count = all_lane_counts[next_lane]
                        
                        # RULE-BASED LOGIC (User Override)
                        # High congestion (>20): 40s (30 + 10)
                        # Low congestion (<=5): 15s
                        # Normal: 30s
                        
                        if vehicle_count > 20:
                            green_time = 40
                            mode_info = "HIGH CONGESTION - EXTENDED"
                        elif vehicle_count <= 5:
                            green_time = 15
                            mode_info = "LOW CONGESTION - REDUCED"
                        else:
                            green_time = 30
                            mode_info = "NORMAL FLOW"
                        
                        # Update cycle state
                        cycle_state['current_lane'] = next_lane
                        cycle_state['phase'] = 'green'
                        cycle_state['phase_start'] = current_time
                        cycle_state['phase_duration'] = green_time
                        
                        self.logger.info(
                            f"🟢 Logic Decision: {self.directions[next_lane].upper()} → GREEN ({green_time}s) "
                            f"[{vehicle_count} vehicles | {mode_info}]"
                        )
                        
                        
                        # Update all lane states with CASCADED countdowns
                        for i, direction in enumerate(self.directions):
                            if i == next_lane:
                                self.states[direction]['signal_state'] = 'GREEN'
                                self.states[direction]['time_remaining'] = green_time
                            else:
                                self.states[direction]['signal_state'] = 'RED'
                                # Calculate estimated wait time
                                # Hops: How many phases until this lane?
                                hops = (i - next_lane) % len(self.directions)
                                # Wait = Current Green + (Hops-1)*(Future_Est_Green + Clearance) + Current_Clearance
                                # Assume future phases are 30s + 5s clearance
                                estimated_wait = green_time + 5 + ((hops - 1) * 35)
                                self.states[direction]['time_remaining'] = estimated_wait
                
                # Update time remaining for all lanes
                for direction in self.directions:
                    state = self.states[direction]
                    dt = current_time - state['last_update_time']
                    state['last_update_time'] = current_time
                    state['time_remaining'] = max(0, state['time_remaining'] - dt)
                    
            except Exception as e:
                self.logger.error(f"Error in traffic light control: {e}", exc_info=True)
            
            # Small delay
            time.sleep(0.1)  # 10 FPS update rate
    
    def stop_camera(self):
        """Stop camera feed"""
        self.is_running = False
        for cam in self.camera_managers.values():
            cam.release()
        
        # Save DQN model
        try:
            self.traffic_controller.save_model("models/dqn/traffic_model.pth")
            self.logger.info("DQN model saved")
        except Exception as e:
            self.logger.error(f"Failed to save DQN model: {e}")
    
    def logout(self):
        """Handle logout"""
        self.stop_camera()
        if self.on_logout_callback:
            self.on_logout_callback()
