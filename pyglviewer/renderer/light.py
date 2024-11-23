import numpy as np

class LightType:
    """Enumeration of supported light types."""
    AMBIENT = 0      # Global ambient light, no position/direction
    DIRECTIONAL = 1  # Parallel rays from infinity (sun-like)
    POINT = 2        # Light radiating in all directions from a point
    SPOT = 3         # Cone-shaped light from a point


""" Default lighting:
    - Main directional light from top-right
    - Ambient light for base illumination
    - Fill directional light from opposite side
"""
default_lighting = {  
    'main': {
        'type': LightType.DIRECTIONAL, 
        'position': (10, 10, 10), 
        'target': (0, 0, 0), 
        'colour': (1.0, 0.95, 0.8),
        'intensity': 0.4
    },
    'ambient': {
        'type': LightType.AMBIENT, 
        'colour': (1, 1, 1), 
        'intensity': 0.7
    },
    'fill': {
        'type': LightType.DIRECTIONAL, 
        'position': (-5, 5, -5), 
        'target': (0, 0, 0), 
        'colour': (0.8, 0.9, 1.0), 
        'intensity': 0.3
    }
}

class Light:
    """Represents a light source in 3D space.
    
    Supports ambient, directional, point, and spot lights with various properties
    like colour, intensity, attenuation, and cutoff angles.
    
    Args:
        type (LightType): 
            Type of light source
        position (tuple, optional): 
            3D position for point/spot lights
        direction (tuple, optional): 
            Direction vector for directional/spot lights
        target (tuple, optional): 
            Target point to calculate direction
        colour (tuple, optional): 
            RGB colour values (0-1). Defaults to white
        intensity (float, optional): 
            Light brightness multiplier. Defaults to 1.0
        attenuation (tuple, optional): 
            Distance falloff factors (constant, linear, quadratic)
        cutoff (float, optional): 
            Spotlight cone angle in degrees
    """
    def __init__(self, type, position=None, direction=None, target=None, colour=(1, 1, 1), intensity=1.0, 
                 attenuation=(1.0, 0.0, 0.0), cutoff=None):
        self.type = type
        # Convert position/target to numpy arrays if provided
        self.position = np.array(position, dtype=np.float32) if position is not None else None
        self.target = np.array(target, dtype=np.float32) if target is not None else None
        self.colour = np.array(colour, dtype=np.float32)
        self.intensity = float(intensity)
        self.attenuation = np.array(attenuation, dtype=np.float32)  # (constant, linear, quadratic)
        self.cutoff = float(cutoff) if cutoff is not None else None  # for spot light

        # Set direction either from provided value, calculated from target, or None
        if direction is not None:
            self.direction = np.array(direction, dtype=np.float32)
        elif self.position is not None and self.target is not None and self.type != LightType.AMBIENT:
            self.direction = self.calculate_direction()
        else:
            self.direction = None

    def calculate_direction(self):
        """Calculate normalized direction vector from position to target.
        
        Returns:
            np.array: Normalized direction vector, or None if position/target missing
        """
        if self.position is None or self.target is None:
            return None
        direction = self.target - self.position
        return direction / np.linalg.norm(direction)

    def get_uniform_data(self):
        """Get light data formatted for shader uniforms.
        
        Returns:
            dict: Light properties ready for shader uniform upload
        """
        # Basic properties for all light types
        data = {
            'type': self.type,
            'colour': self.colour,
            'intensity': self.intensity,
        }
        
        # Additional properties for non-ambient lights
        if self.type != LightType.AMBIENT:
            data['attenuation'] = self.attenuation
            if self.position is not None:
                data['position'] = self.position
            if self.direction is not None:
                data['direction'] = self.direction
            if self.cutoff is not None:
                data['cutoff'] = self.cutoff
        return data

    def update_direction(self):
        """Update direction vector based on current position and target.
        
        Called when position or target changes to maintain correct direction.
        """
        if self.type != LightType.AMBIENT and self.position is not None and self.target is not None:
            self.direction = self.calculate_direction()
