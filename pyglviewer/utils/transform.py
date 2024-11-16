import numpy as np

class Transform:
    """Handles 3D transformations including translation, rotation, and scaling."""
    def __init__(self, translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1)):
        self.translate = np.array(translate, dtype=np.float32)
        self.rotate = np.array(rotate, dtype=np.float32)  # In radians
        self.scale = np.array(scale, dtype=np.float32)
        self.dirty = True
        self.cached_matrix = None
    def transform_position(self, position):
        """Transform a 3D position using this transform.
        
        Args:
            position (np.array): 3D position vector
            
        Returns:
            np.array: Transformed position
        """
        return (self.transform_matrix() @ np.append(position, 1))[:3]

    def transform_matrix(self):
        """Create a 4x4 transformation matrix.
        
        Returns:
            np.array: 4x4 transformation matrix
        """
        if self.dirty:
            tx, ty, tz = self.translate
            rx, ry, rz = self.rotate
            sx, sy, sz = self.scale

            # Create rotation matrices
            Rx = np.array([[1, 0, 0], [0, np.cos(rx), -np.sin(rx)], [0, np.sin(rx), np.cos(rx)]])
            Ry = np.array([[np.cos(ry), 0, np.sin(ry)], [0, 1, 0], [-np.sin(ry), 0, np.cos(ry)]])
            Rz = np.array([[np.cos(rz), -np.sin(rz), 0], [np.sin(rz), np.cos(rz), 0], [0, 0, 1]])

            # Combine rotations
            R = Rz @ Ry @ Rx

            # Create transformation matrix
            transform = np.array([
                [R[0, 0]*sx, R[0, 1]*sy, R[0, 2]*sz, tx],
                [R[1, 0]*sx, R[1, 1]*sy, R[1, 2]*sz, ty],
                [R[2, 0]*sx, R[2, 1]*sy, R[2, 2]*sz, tz],
                [0, 0, 0, 1]
            ], dtype=np.float32)  # Ensure float32 type

            self.dirty = False
            self.cached_matrix = transform
            
        return self.cached_matrix

    def set_translate(self, x, y, z):
        """Set absolute translation values."""
        self.translate = np.array([x, y, z], dtype=np.float32)
        self.dirty = True
        return self

    def translate(self, x, y, z):
        """Update position by the given amounts."""
        self.translate += np.array([x, y, z], dtype=np.float32)
        self.dirty = True
        return self
    
    def set_rotate(self, rx, ry, rz):
        """Set absolute rotation values."""
        self.rotate = np.array([rx, ry, rz], dtype=np.float32)
        self.dirty = True
        return self

    def rotate(self, rx, ry, rz):
        """Update rotation by the given angles (in radians)."""
        self.rotate += np.array([rx, ry, rz], dtype=np.float32)
        self.dirty = True
        return self

    def set_scale(self, x, y, z):
        """Set absolute scale values."""
        self.scale = np.array([x, y, z], dtype=np.float32)
        self.dirty = True
        return self

    def scale(self, x, y, z):
        """Scale relatively by multiplying current scale."""
        self.scale *= np.array([x, y, z], dtype=np.float32)
        self.dirty = True
        return self
