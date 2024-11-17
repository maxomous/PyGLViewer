import glfw
import numpy as np

class Timer:
    """Simple timer for tracking frame times using ImGui."""
    previous = 0.0
    time = 0.0
    dt = 0.0

    def update(self):
        """Update timer and calculate delta time between frames."""
        self.time = glfw.get_time()
        self.dt = self.time - self.previous
        self.previous = self.time
        
    def oscillate_angle(self, speed=1, phi=0, reverse=False):
        """Calculate rotation angle for continuous rotation (2π per second).
        
        Args:
            speed (float): Rotation speed multiplier (default: 1)
            phi (float): Phase offset in radians (default: 0)
            reverse (bool): Reverse rotation direction (default: False)
            
        Returns:
            float: Angle in radians, wrapped between 0 and 2π
        """
        angle = (speed * self.time * 2 * np.pi + phi) % (2 * np.pi)  # Wrap between 0 and 2π
        return angle if reverse else 2 * np.pi - angle
    
    def oscillate_translation(self, amplitude=1, speed=1, phi=0, reverse=False):
        """Calculate sinusoidal translation (1 oscillation per second).
        
        Args:
            amplitude (float): Maximum translation distance
            speed (float): Speed of oscillation
            phi (float): Phase offset in radians (default: 0)
            reverse (bool): Reverse oscillation direction (default: False)
            
        Returns:
            float: Translation offset between -amplitude and +amplitude
        """
        return amplitude * np.sin(speed * self.oscillate_angle(phi=phi, reverse=reverse))
