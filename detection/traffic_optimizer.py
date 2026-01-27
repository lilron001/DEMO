# detection/traffic_optimizer.py
import logging
from typing import Dict, List
from datetime import datetime

class TrafficOptimizer:
    """Optimize traffic flow based on vehicle detection and AI predictions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.signal_timings = {
            "green_time": 30,
            "yellow_time": 3,
            "red_time": 30
        }
        self.optimization_history = []
    
    def optimize_signal(self, vehicle_count: int, queue_length: float = 0) -> Dict:
        """Optimize traffic signal timing based on real-time data"""
        try:
            # Adjust green time based on vehicle count
            if vehicle_count > 50:
                green_time = 60
            elif vehicle_count > 30:
                green_time = 45
            elif vehicle_count > 10:
                green_time = 30
            else:
                green_time = 20
            
            optimization = {
                "timestamp": datetime.now().isoformat(),
                "vehicle_count": vehicle_count,
                "queue_length": queue_length,
                "green_time": green_time,
                "yellow_time": 3,
                "red_time": 90 - green_time - 3,
                "status": "optimized"
            }
            
            self.optimization_history.append(optimization)
            self.logger.info(f"Signal optimized: {vehicle_count} vehicles, {green_time}s green")
            
            return optimization
        except Exception as e:
            self.logger.error(f"Optimization error: {e}")
            return {"status": "error"}
    
    def get_recommendations(self) -> List[Dict]:
        """Get traffic management recommendations"""
        recommendations = []
        
        if len(self.optimization_history) > 0:
            recent = self.optimization_history[-1]
            
            if recent.get("vehicle_count", 0) > 80:
                recommendations.append({
                    "priority": "HIGH",
                    "message": "Very heavy traffic detected. Consider alternate routes.",
                    "action": "increase_monitoring"
                })
            
            if recent.get("vehicle_count", 0) > 50:
                recommendations.append({
                    "priority": "MEDIUM",
                    "message": "Heavy traffic in this area.",
                    "action": "optimize_signals"
                })
        
        return recommendations
    
    def get_statistics(self) -> Dict:
        """Get traffic statistics"""
        if not self.optimization_history:
            return {"total_optimizations": 0}
        
        vehicle_counts = [h.get("vehicle_count", 0) for h in self.optimization_history]
        
        return {
            "total_optimizations": len(self.optimization_history),
            "avg_vehicles": sum(vehicle_counts) / len(vehicle_counts) if vehicle_counts else 0,
            "max_vehicles": max(vehicle_counts) if vehicle_counts else 0,
            "min_vehicles": min(vehicle_counts) if vehicle_counts else 0
        }

