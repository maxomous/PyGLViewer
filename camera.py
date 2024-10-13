import numpy as np
import math

class Camera:
    def __init__(self, position, target, up):
        self.position = np.array(position, dtype=np.float32)
        self.target = np.array(target, dtype=np.float32)
        self.up = np.array(up, dtype=np.float32)
        self.yaw = 72.0  # Horizontal rotation
        self.pitch = -27.0  # Vertical rotation

    def get_perspective_projection(self, fov, aspect, near, far):
        f = 1 / math.tan(math.radians(fov) / 2)
        return np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), -1],
            [0, 0, (2 * far * near) / (near - far), 0]
        ], dtype=np.float32)

    def get_view_matrix(self):
        return np.array([
            [self.right[0], self.up[0], -self.front[0], 0],
            [self.right[1], self.up[1], -self.front[1], 0],
            [self.right[2], self.up[2], -self.front[2], 0],
            [-np.dot(self.right, self.position), -np.dot(self.up, self.position), np.dot(self.front, self.position), 1]
        ], dtype=np.float32)
 
    def normalize(self, v):
        norm = np.linalg.norm(v)
        if norm == 0: 
            return v
        return v / norm

# class FirstPersonCamera(Camera):
#     def __init__(self, position, target, up):
#         super().__init__(position, target, up)
#         self.update_vectors()

#     def move(self, direction, speed):
#         if direction == "FORWARD":
#             self.position += self.front * speed
#         elif direction == "BACKWARD":
#             self.position -= self.front * speed
#         elif direction == "LEFT":
#             self.position -= self.right * speed
#         elif direction == "RIGHT":
#             self.position += self.right * speed
#         self.target = self.position + self.front

#     def rotate(self, yaw_offset, pitch_offset):
#         self.yaw += yaw_offset
#         self.pitch += pitch_offset
#         self.pitch = max(-89.0, min(89.0, self.pitch))
#         self.update_vectors()
#         self.target = self.position + self.front


class ThirdPersonCamera(Camera):
    def __init__(self, position, target, up, distance):
        super().__init__(position, target, up)
        self.distance = distance
        self.world_up = np.array(up, dtype=np.float32)
        self.update_vectors()
 
    def update_vectors(self):
        # Calculate the new front vector
        front = np.array([
            math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.pitch))
        ], dtype=np.float32)
        self.front = self.normalize(front)
        # Recalculate the right and up vector
        self.right = self.normalize(np.cross(self.front, self.world_up))
        self.up = self.normalize(np.cross(self.right, self.front))
        # Update position
        self.position = self.target - self.front * self.distance

    def rotate(self, yaw_offset, pitch_offset, invert=[1, 1]):
        ''' set invert to -1 to invert '''
        invert_yaw, invert_pitch = invert
        self.yaw += yaw_offset * 2 * invert_yaw
        self.pitch += pitch_offset * 4 * invert_pitch

        # Normalize yaw to [0, 360) degrees
        self.yaw = self.yaw % 360.0
        # Clamp pitch to [-89, 89] degrees
        self.pitch = max(-89.0, min(89.0, self.pitch))
        self.update_vectors()

    def pan(self, dx, dy, invert=[1, 1]):
        ''' set invert to -1 to invert '''
        right = self.normalize(np.cross(self.front, self.world_up))
        up = self.normalize(np.cross(right, self.front))
        self.target += right * dx * invert[0] - up * dy * invert[1]
        self.update_vectors()

    def zoom(self, offset):
        self.distance = max(1.0, min(20.0, self.distance - offset))
        self.update_vectors()

    def move(self, direction, speed):
        if direction == "FORWARD":
            self.target += self.front * speed
        elif direction == "BACKWARD":
            self.target -= self.front * speed
        elif direction == "LEFT":
            right = self.normalize(np.cross(self.front, self.world_up))
            self.target -= right * speed
        elif direction == "RIGHT":
            right = self.normalize(np.cross(self.front, self.world_up))
            self.target += right * speed
        self.update_vectors()
