import numpy as np
import math

class Camera:
    """Base camera class providing core camera functionality.
    
    Args:
        target (tuple): Target point to look at
        up (tuple): Up vector for camera orientation
        distance (float): Distance from target
        near (float): Near clipping plane distance
        far (float): Far clipping plane distance
    
    Attributes:
        position (np.array): Camera position in world space
        target (np.array): Point camera is looking at
        up (np.array): Camera's up vector
        yaw (float): Horizontal rotation angle in degrees
        pitch (float): Vertical rotation angle in degrees
        is_orthographic (bool): Whether using orthographic projection
    """

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
        """Set camera aspect ratio based on viewport dimensions.
        
        Args:
            width (int): Viewport width
            height (int): Viewport height
        """
        self.aspect_ratio = width / height if height > 0 else 1.0
    
        
    @staticmethod
    def get_orthographic_projection(left, right, bottom, top, near, far):
        """Create orthographic projection matrix.
        
        Args:
            left, right (float): Left/right clipping planes
            bottom, top (float): Bottom/top clipping planes
            near, far (float): Near/far clipping planes
        
        Returns:
            np.array: 4x4 orthographic projection matrix
        """
        return np.array([
            [2 / (right - left), 0, 0, -(right + left) / (right - left)],
            [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
            [0, 0, -2 / (far - near), -(far + near) / (far - near)],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
    @staticmethod
    def get_perspective_projection(fov, aspect, near, far):
        """Create perspective projection matrix.
        
        Args:
            fov (float): Field of view in degrees
            aspect (float): Aspect ratio (width/height)
            near, far (float): Near/far clipping planes
        
        Returns:
            np.array: 4x4 perspective projection matrix
        """
        f = 1 / math.tan(math.radians(fov) / 2)
        return np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), -1],
            [0, 0, (2 * far * near) / (near - far), 0]
        ], dtype=np.float32)
        
    def get_view_matrix(self):
        """Get the view matrix for the current camera position.
        
        Returns:
            np.array: 4x4 view matrix
        """
        # View matrix calculation
        return np.array([
            [self.right[0], self.up[0], -self.front[0], 0],
            [self.right[1], self.up[1], -self.front[1], 0],
            [self.right[2], self.up[2], -self.front[2], 0],
            [-np.dot(self.right, self.position), -np.dot(self.up, self.position), np.dot(self.front, self.position), 1]
        ], dtype=np.float32)
  
    def get_projection_matrix(self):
        """Get the current projection matrix.
        
        Returns:
            np.array: 4x4 projection matrix (orthographic or perspective)
        """
        return self.projection
  
    def update_projection(self):
        """Update projection matrix based on current camera settings.
        
        Updates orthographic or perspective projection based on is_orthographic flag.
        """
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
        """Normalize a vector to unit length.
        
        Args:
            v (np.array): Vector to normalize
        
        Returns:
            np.array: Normalized vector, or original if zero length
        """
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
    """Third-person camera that orbits around a target point.
    
    Supports both 2D and 3D viewing modes with orthographic/perspective projection.
    
    Args:
        target (tuple): Target point to orbit around
        up (tuple): World up vector
        distance (float): Orbit distance from target
    
    Attributes:
        world_up (np.array): Fixed world up vector
        is_2d_mode (bool): Whether in 2D top-down mode
        front (np.array): Camera forward vector
        right (np.array): Camera right vector
    """

    def __init__(self, is_2d_mode, target, up, distance):
        super().__init__(target, up, distance)
        self.world_up = np.array(up, dtype=np.float32)
        self.set_2d_mode(is_2d_mode)
        self.update_vectors()
        # self.update_projection() # aspect needs to be set first




    def update_vectors(self):
        """Update camera orientation vectors and position based on current state."""
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
            # Update position
            self.position = self.target - self.front * self.distance
    

    def rotate(self, yaw_offset, pitch_offset, invert=[1, 1]):
        """Rotate camera around target (3D mode only).
        
        Args:
            yaw_offset (float): Horizontal rotation change
            pitch_offset (float): Vertical rotation change
            invert (list): Inversion flags for yaw/pitch
        """
        if not self.is_2d_mode:
            invert_yaw, invert_pitch = invert
            self.yaw += yaw_offset * 2 * invert_yaw
            self.pitch += pitch_offset * 4 * invert_pitch
            self.yaw = self.yaw % 360.0
            self.pitch = max(-89.0, min(89.0, self.pitch))
            self.update_vectors()

    def pan(self, dx, dy, invert=[1, 1]):
        """Pan camera parallel to view plane.
        
        Args:
            dx (float): Horizontal pan amount
            dy (float): Vertical pan amount
            invert (list): Inversion flags for x/y movement
        """
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
        """Adjust distance from target.
        
        Args:
            offset (float): Change in distance
        """
        self.distance = max(1.0, min(20.0, self.distance - offset))
        self.update_vectors()
        self.update_projection()
        
    def set_2d_mode(self, enabled):
        """Set 2D top-down or 3D orbital mode.
        
        Args:
            enabled (bool): True for 2D mode, False for 3D mode
        """
        self.is_2d_mode = enabled
        self.is_orthographic = enabled
        if enabled:
            self.pitch = -90.0  # Look straight down
        else:
            # When in 3D mode
            self.pitch = -27.0
        self.update_vectors()

    def toggle_2d_mode(self):
        """Switch between 2D top-down and 3D orbital modes."""
        self.set_2d_mode(not self.is_2d_mode)

    def move(self, direction, speed):
        """Move camera target in specified direction.
        
        Args:
            direction (str): Movement direction ("FORWARD", "BACKWARD", "LEFT", "RIGHT")
            speed (float): Movement speed
        """
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

    def set_projection(self, orthographic):
        """Set orthographic or perspective projection mode.
        
        Args:
            orthographic (bool): True for orthographic, False for perspective
        """
        self.is_orthographic = orthographic
        self.update_vectors()
        self.update_projection()  # Also adding this as it's important to update the projection matrix

    def toggle_projection(self):
        """Toggle between orthographic and perspective projection."""
        self.set_projection(not self.is_orthographic)
