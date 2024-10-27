import numpy as np
import math

class Camera:
    def __init__(self, position, target, up):
        self.position = np.array(position, dtype=np.float32)
        self.target = np.array(target, dtype=np.float32)
        self.up = np.array(up, dtype=np.float32)
        self.yaw = 72.0  # Horizontal rotation
        self.pitch = -27.0  # Vertical rotation

            # m_Proj = glm::perspective(glm::radians(m_FOV), aspectRatio, m_Near, m_Far);
    def get_orthographic_projection(self, left, right, bottom, top, near, far):
       
        # Calculate matrix elements
        m00 = 2 / (right - left)
        m11 = 2 / (top - bottom)
        m22 = -2 / (far - near)
        m03 = -(right + left) / (right - left)
        m13 = -(top + bottom) / (top - bottom)
        m23 = -(far + near) / (far - near)
        
        # Create the matrix
        return np.array([
            [m00,  0.0,  0.0, m03],
            [0.0,  m11,  0.0, m13],
            [0.0,  0.0,  m22, m23],
            [0.0,  0.0,  0.0, 1.0]
        ], dtype=np.float32)
            
        return np.array([
            [2 / (right - left), 0, 0, -(right + left) / (right - left)],
            [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
            [0, 0, -2 / (far - near), -(far + near) / (far - near)],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
    def get_perspective_projection(self, fov, aspect, near, far):
        f = 1 / math.tan(math.radians(fov) / 2)
        return np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), -1],
            [0, 0, (2 * far * near) / (near - far), 0]
        ], dtype=np.float32)
        
    def look_at(self, eye, target, up):
        # Calculate the forward vector (z-axis)
        f = np.array(target) - np.array(eye)
        f = f / np.linalg.norm(f)

        # Calculate the right vector (x-axis)
        s = np.cross(f, up)
        s = s / np.linalg.norm(s)

        # Calculate the up vector (y-axis)
        u = np.cross(s, f)

        # Create a 4x4 view matrix
        view_matrix = np.identity(4)
        view_matrix[0, :3] = s
        view_matrix[1, :3] = u
        view_matrix[2, :3] = -f
        view_matrix[0, 3] = -np.dot(s, eye)
        view_matrix[1, 3] = -np.dot(u, eye)
        view_matrix[2, 3] = np.dot(f, eye)

        return view_matrix

    def get_view_matrix(self):
        # matrix = self.look_at(self.position, self.target, self.up)
        # print(f'view matrix: {matrix}')
        # return matrix
        # if self.is_orthographic:
        #     return self.lookAt(self.position, self.target, self.up)
        #     # return self.lookAt(self.position, self.target, self.up)
        #     # For orthographic, use a simpler view matrix
        #     return np.array([
        #         [1, 0, 0, -self.position[0]],
        #         [0, 1, 0, -self.position[1]],
        #         [0, 0, 1, -self.position[2]],
        #         [0, 0, 0, 1]
        #     ], dtype=np.float32)
        # else:
        # View matrix calculation
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
        self.is_2d_mode = False
        self.is_orthographic = False
        self.update_vectors()



    # // calculates the front vector from the Camera's (updated) Euler Angles
    # void Camera_CentreObject::updateCameraVectors()
    # { 
    #     // yaw goes around z
    #     glm::vec3 pos;
    #     pos.x = cos(glm::radians(m_Yaw)) * cos(glm::radians(m_Pitch));
    #     pos.y = sin(glm::radians(m_Yaw)) * cos(glm::radians(m_Pitch));
    #     pos.z = sin(glm::radians(m_Pitch)); 
        
    #     // Re-calculate the Front, Right and Up vector
    #     m_Front = glm::normalize(pos);
    #     m_Right = glm::normalize(glm::cross(m_Front, m_WorldUp));  // normalize the vectors, because their length gets closer to 0 the more you look up or down which results in slower movement.
    #     m_Up = glm::normalize(glm::cross(m_Right, m_Front));
        
    #     // Calculate the camera position
    #     m_Position = (m_Zoom * pos) + m_Centre;
    # }
    


    def update_vectors(self):
        # if self.is_2d_mode:
        #     # 2D mode: camera always looks down the negative z-axis
        #     self.front = np.array([0, 0, -1], dtype=np.float32)
        #     self.right = np.array([1, 0, 0], dtype=np.float32)
        #     self.up = np.array([0, 1, 0], dtype=np.float32)
        #     self.position = np.array([self.target[0], self.target[1], self.distance], dtype=np.float32)
        # else:
        # 3D update logic
        front = np.array([
            math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.pitch))
        ], dtype=np.float32)
        self.front = self.normalize(front)
        self.right = self.normalize(np.cross(self.front, self.world_up))
        self.up = self.normalize(np.cross(self.right, self.front))
        # self.position = self.target - self.front * self.distance
        self.position = front * self.distance + self.target

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
            self.target[0] += dx * invert[0]
            self.target[1] += dy * invert[1]
        else:
            # 3D panning logic
            right = self.normalize(np.cross(self.front, self.world_up))
            up = self.normalize(np.cross(right, self.front))
            self.target += right * dx * invert[0] - up * dy * invert[1]
        self.update_vectors()

    def zoom(self, offset):
        # Zoom behavior is the same for both 2D and 3D modes
        self.distance = max(1.0, min(20.0, self.distance - offset))
        self.update_vectors()

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
        if self.is_orthographic:
            # Adjust camera position for orthographic view
            self.position = self.target + np.array([0, 0, self.distance], dtype=np.float32)
        self.update_vectors()

