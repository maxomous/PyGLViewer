import glfw
import numpy as np

class Timer:
    """Simple timer for tracking frame times using ImGui."""
    
    def __init__(self):
        """Initialize timer with current ImGui time."""
        self.previous = glfw.get_time()
        self.time = glfw.get_time()
        self.dt = 0.0

    def update(self):
        """Update timer and calculate delta time between frames."""
        self.time = glfw.get_time()
        self.dt = self.time - self.previous
        self.previous = self.time
        
    def oscillate_angle(self, speed=1, reverse=False):
        """Calculate rotation angle for continuous rotation (2π per second).
        
        Returns:
            float: Angle in radians
        """
        angle = speed * self.time * 2 * np.pi  # 1 rotation per second
        return angle if reverse else 2 * np.pi - angle
    
    def oscillate_translation(self, amplitude=1, speed=1, reverse=False):
        """Calculate sinusoidal translation (1 oscillation per second).
        
        Args:
            amplitude (float): Maximum translation distance
            speed (float): Speed of oscillation
            
        Returns:
            float: Translation offset
        """
        return amplitude * np.sin(speed * self.oscillate_angle(reverse=reverse))
