import numpy as np

class LightType:
    DIRECTIONAL = 0
    POINT = 1
    SPOT = 2

class Light:
    def __init__(self, light_type, position=None, direction=None, color=(1, 1, 1), intensity=1.0, 
                 attenuation=(1.0, 0.0, 0.0), cutoff=None):
        self.light_type = light_type
        self.position = np.array(position, dtype=np.float32) if position is not None else None
        self.direction = np.array(direction, dtype=np.float32) if direction is not None else None
        self.color = np.array(color, dtype=np.float32)
        self.intensity = float(intensity)
        self.attenuation = np.array(attenuation, dtype=np.float32)  # (constant, linear, quadratic)
        self.cutoff = float(cutoff) if cutoff is not None else None  # for spot light

    def get_uniform_data(self):
        data = {
            'type': self.light_type,
            'color': self.color,
            'intensity': self.intensity,
            'attenuation': self.attenuation
        }
        if self.position is not None:
            data['position'] = self.position
        if self.direction is not None:
            data['direction'] = self.direction
        if self.cutoff is not None:
            data['cutoff'] = self.cutoff
        return data
