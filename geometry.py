import numpy as np
from OpenGL.GL import *

class Geometry:
    @staticmethod
    def create_point(x, y, z, color):
        return np.array([x, y, z, *color], dtype=np.float32), np.array([0], dtype=np.uint32)

    @staticmethod
    def create_line(start, end, color):
        return np.array([*start, *color, *end, *color], dtype=np.float32), np.array([0, 1], dtype=np.uint32)

    @staticmethod
    def create_triangle(p1, p2, p3, color):
        return np.array([*p1, *color, *p2, *color, *p3, *color], dtype=np.float32), np.array([0, 1, 2], dtype=np.uint32)

    @staticmethod
    def create_rectangle(x, y, width, height, color):
        half_w, half_h = width / 2, height / 2
        vertices = np.array([
            x - half_w, y - half_h, 0, *color,
            x + half_w, y - half_h, 0, *color,
            x + half_w, y + half_h, 0, *color,
            x - half_w, y + half_h, 0, *color
        ], dtype=np.float32)
        indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
        return vertices, indices

    @staticmethod
    def create_circle(x, y, radius, segments, color):
        vertices = [x, y, 0, *color]
        indices = []
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            vertices.extend([
                x + radius * np.cos(angle),
                y + radius * np.sin(angle),
                0, *color
            ])
            if i > 0:
                indices.extend([0, i, i + 1])
        indices.extend([0, segments, 1])
        return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

    @staticmethod
    def create_cube(position, size, color, wireframe=False):
        s = size / 2
        x, y, z = position
        vertices = np.array([
            x-s, y-s, z+s, *color,  # 0
            x+s, y-s, z+s, *color,  # 1
            x+s, y+s, z+s, *color,  # 2
            x-s, y+s, z+s, *color,  # 3
            x-s, y-s, z-s, *color,  # 4
            x+s, y-s, z-s, *color,  # 5
            x+s, y+s, z-s, *color,  # 6
            x-s, y+s, z-s, *color,  # 7
        ], dtype=np.float32)

        if wireframe:
            indices = np.array([
                0, 1, 1, 2, 2, 3, 3, 0,  # Front face
                4, 5, 5, 6, 6, 7, 7, 4,  # Back face
                0, 4, 1, 5, 2, 6, 3, 7   # Connecting edges
            ], dtype=np.uint32)
        else:
            indices = np.array([
                0, 1, 2, 2, 3, 0,  # Front face
                5, 4, 7, 7, 6, 5,  # Back face
                4, 0, 3, 3, 7, 4,  # Left face
                1, 5, 6, 6, 2, 1,  # Right face
                3, 2, 6, 6, 7, 3,  # Top face
                4, 5, 1, 1, 0, 4   # Bottom face
            ], dtype=np.uint32)

        return vertices, indices
