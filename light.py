import numpy as np

class LightType:
    DIRECTIONAL = 0
    POINT = 1
    SPOT = 2

class Light:
    def __init__(self, type, position=None, direction=None, target=None, color=(1, 1, 1), intensity=1.0, 
                 attenuation=(1.0, 0.0, 0.0), cutoff=None):
        self.type = type
        self.position = np.array(position, dtype=np.float32) if position is not None else None
        self.target = np.array(target, dtype=np.float32) if target is not None else None
        self.color = np.array(color, dtype=np.float32)
        self.intensity = float(intensity)
        self.attenuation = np.array(attenuation, dtype=np.float32)  # (constant, linear, quadratic)
        self.cutoff = float(cutoff) if cutoff is not None else None  # for spot light

        if direction is not None:
            self.direction = np.array(direction, dtype=np.float32)
        elif self.position is not None and self.target is not None:
            self.direction = self.calculate_direction()
        else:
            self.direction = None

    def calculate_direction(self):
        if self.position is None or self.target is None:
            return None
        direction = self.target - self.position
        return direction / np.linalg.norm(direction)

    def get_uniform_data(self):
        data = {
            'type': self.type,
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

    def update_direction(self):
        if self.position is not None and self.target is not None:
            self.direction = self.calculate_direction()
