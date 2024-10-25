import numpy as np
from math import sin, cos

class Transform:
    def __init__(self, translation=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        self.translation = translation
        self.rotation = rotation
        self.scale = scale

    def get_matrix(self):
        """
        Create a 4x4 transformation matrix from the current transform parameters.
        
        :return: 4x4 numpy array representing the transformation matrix
        """
        tx, ty, tz = self.translation
        rx, ry, rz = self.rotation
        sx, sy, sz = self.scale

        # Create rotation matrices
        Rx = np.array([[1, 0, 0], [0, cos(rx), -sin(rx)], [0, sin(rx), cos(rx)]])
        Ry = np.array([[cos(ry), 0, sin(ry)], [0, 1, 0], [-sin(ry), 0, cos(ry)]])
        Rz = np.array([[cos(rz), -sin(rz), 0], [sin(rz), cos(rz), 0], [0, 0, 1]])

        # Combine rotations
        R = Rz @ Ry @ Rx

        # Create transformation matrix
        transform = np.array([
            [R[0, 0]*sx, R[0, 1]*sy, R[0, 2]*sz, tx],
            [R[1, 0]*sx, R[1, 1]*sy, R[1, 2]*sz, ty],
            [R[2, 0]*sx, R[2, 1]*sy, R[2, 2]*sz, tz],
            [0, 0, 0, 1]
        ])

        return transform
