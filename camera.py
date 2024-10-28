import numpy as np
import math

class Camera:
    def __init__(self, target, up, distance, near=0.1, far=100):
        self.position = np.array((0,0,0), dtype=np.float32) # set in update_vectors
        self.target = np.array(target, dtype=np.float32)
        self.up = np.array(up, dtype=np.float32)
        self.yaw = 72.0  # Horizontal rotation
        self.pitch = -27.0  # Vertical rotation
        self.distance = distance
        self.is_orthographic = False
        self.aspect_ratio = None
        self.near = near
        self.far = far
        
    def set_aspect_ratio(self, width, height):
        self.aspect_ratio = width / height if height > 0 else 1.0
    
        
    @staticmethod
    def get_orthographic_projection(left, right, bottom, top, near, far):           
        return np.array([
            [2 / (right - left), 0, 0, -(right + left) / (right - left)],
            [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
            [0, 0, -2 / (far - near), -(far + near) / (far - near)],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
    @staticmethod
    def get_perspective_projection(fov, aspect, near, far):
        f = 1 / math.tan(math.radians(fov) / 2)
        return np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), -1],
            [0, 0, (2 * far * near) / (near - far), 0]
        ], dtype=np.float32)
        
    def get_view_matrix(self):
        # View matrix calculation
        return np.array([
            [self.right[0], self.up[0], -self.front[0], 0],
            [self.right[1], self.up[1], -self.front[1], 0],
            [self.right[2], self.up[2], -self.front[2], 0],
            [-np.dot(self.right, self.position), -np.dot(self.up, self.position), np.dot(self.front, self.position), 1]
        ], dtype=np.float32)
  
    def get_projection_matrix(self):
        return self.projection
  
    def update_projection(self):
        if self.is_orthographic:
            scaled_width = self.distance * self.aspect_ratio / 2
            scaled_height = self.distance * 1 / 2
            self.projection = self.get_orthographic_projection(-scaled_width, scaled_width, -scaled_height, scaled_height, -self.far, self.far) # TODO near, far
        else:
            fov = 45.0
            self.projection = self.get_perspective_projection(
                fov, self.aspect_ratio, self.near, self.far
            )

  
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
    def __init__(self, target, up, distance):
        super().__init__(target, up, distance)
        self.world_up = np.array(up, dtype=np.float32)
        self.is_2d_mode = False
        self.update_vectors()
        # self.update_projection() # aspect needs to be set first




    def update_vectors(self):
        if self.is_2d_mode:
            # 2D mode: camera always looks down the negative z-axis
            self.front = np.array([0, 0, -1], dtype=np.float32)
            self.right = np.array([1, 0, 0], dtype=np.float32)
            self.up = np.array([0, 1, 0], dtype=np.float32)
            self.position = np.array([self.target[0], self.target[1], self.distance], dtype=np.float32)
        else:
            # 3D update logic (yaw goes around z)
            front = np.array([
                math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
                math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
                math.sin(math.radians(self.pitch))
            ], dtype=np.float32)
            self.front = self.normalize(front)
            self.right = self.normalize(np.cross(self.front, self.world_up))
            self.up = self.normalize(np.cross(self.right, self.front))
            # Update position for both orthographic and perspective modes
            
            # Perspective mode
            self.position = self.target - self.front * self.distance
        
        # if self.is_orthographic:
        #     # Orthographic mode
        #     self.position = front * self.distance + self.target
        # else:
        #     # Perspective mode
        #     self.position = self.target - self.front * self.distance

    def rotate(self, yaw_offset, pitch_offset, invert=[1, 1]):
        if not self.is_2d_mode:
            invert_yaw, invert_pitch = invert
            self.yaw += yaw_offset * 2 * invert_yaw
            self.pitch += pitch_offset * 4 * invert_pitch
            self.yaw = self.yaw % 360.0
            self.pitch = max(-89.0, min(89.0, self.pitch))
            self.update_vectors()

    def pan(self, dx, dy, invert=[1, 1]):
        if self.is_2d_mode:
            # 2D panning: move target in x and y directions
            # Invert dy for 2D mode to match screen coordinates
            self.target[0] += dx * invert[0]
            self.target[1] -= dy * invert[1] 
        else:
            # 3D panning logic
            right = self.normalize(np.cross(self.front, self.world_up))
            up = self.normalize(np.cross(right, self.front))
            self.target += right * dx * invert[0] - up * dy * invert[1]
        self.update_vectors()

    def zoom(self, offset):
        self.distance = max(1.0, min(20.0, self.distance - offset))
        self.update_vectors()
        self.update_projection()
        
    def toggle_2d_mode(self):
        self.is_2d_mode = not self.is_2d_mode
        self.is_orthographic = self.is_2d_mode
        if self.is_2d_mode:
            self.pitch = -90.0  # Look straight down
        else:
            # When switching back to 3D mode, reset the pitch to a reasonable value
            self.pitch = -45.0
        self.update_vectors()

    def move(self, direction, speed):
        if self.is_2d_mode:
            # In 2D mode, only allow movement in the XY plane
            if direction == "FORWARD":
                self.target[1] += speed
            elif direction == "BACKWARD":
                self.target[1] -= speed
            elif direction == "LEFT":
                self.target[0] -= speed
            elif direction == "RIGHT":
                self.target[0] += speed
        else:
            # 3D movement
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

    def toggle_projection(self):
        self.is_orthographic = not self.is_orthographic
        self.update_vectors()
