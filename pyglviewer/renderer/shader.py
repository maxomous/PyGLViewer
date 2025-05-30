from enum import Enum
from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np


class PointShape(Enum):
    CIRCLE = 0
    SQUARE = 1
    TRIANGLE = 2
    
    
# Vertex shader for basic lighting and transformations
vertex_shader_lighting = """
#version 330 core
layout (location = 0) in vec3 aPos;      // Vertex position
layout (location = 1) in vec3 aColour;    // Vertex colour
layout (location = 2) in vec3 aNormal;   // Vertex normal

out vec3 FragPos;   // Fragment position in world space
out vec3 Normal;    // Fragment normal in world space
out vec3 Colour;     // Fragment colour

// Transformation matrices
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    vec4 worldPos = model * vec4(aPos, 1.0);
    FragPos = worldPos.xyz;
    Normal = mat3(transpose(inverse(model))) * aNormal;
    Colour = aColour;
    gl_Position = projection * view * worldPos;
}
"""

# Fragment shader supporting multiple light types with Blinn-Phong lighting
fragment_shader_lighting = """
#version 330 core
in vec3 FragPos;    // Fragment position in world space
in vec3 Normal;     // Fragment normal in world space
in vec3 Colour;      // Fragment colour

out vec4 FragColour;

#define MAX_LIGHTS 10

// Light structure supporting ambient, directional, point, and spot lights
struct Light {
    int type;           // 0=ambient, 1=directional, 2=point, 3=spot
    vec3 position;      // Position for point/spot lights
    vec3 direction;     // Direction for directional/spot lights
    vec3 colour;        // Light colour
    float intensity;    // Light intensity multiplier
    vec3 attenuation;   // Distance attenuation factors (constant, linear, quadratic)
    float cutoff;       // Spotlight cone angle in radians
};

uniform Light lights[MAX_LIGHTS];
uniform int numLights;
uniform vec3 viewPos;   // Camera position for specular calculation
uniform float alpha = 1.0;  // Add alpha uniform

vec3 calcLight(Light light, vec3 normal, vec3 fragPos, vec3 viewDir) {
    if (light.type == 0) {  // Ambient light
        return light.colour * light.intensity;
    }
    
    vec3 lightDir;
    float attenuation = 1.0;

    if (light.type == 1) {  // Directional light
        lightDir = normalize(-light.direction);
    } else {                // Point or spot light
        lightDir = normalize(light.position - fragPos);
        float distance = length(light.position - fragPos);
        attenuation = 1.0 / (light.attenuation.x + light.attenuation.y * distance + 
                            light.attenuation.z * distance * distance);

        if (light.type == 3) {  // Spot light cone check
            float theta = dot(lightDir, normalize(-light.direction));
            if (theta <= cos(light.cutoff)) {
                return vec3(0.0);
            }
        }
    }

    // Blinn-Phong lighting calculation
    vec3 ambient = 0.1 * light.colour;

    float diff = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = diff * light.colour;

    vec3 halfwayDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(normal, halfwayDir), 0.0), 32.0);
    vec3 specular = spec * light.colour;

    return (ambient + diffuse + specular) * light.intensity * attenuation;
}

void main() {
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);

    vec3 result = vec3(0.0);
    for (int i = 0; i < numLights; i++) {
        result += calcLight(lights[i], norm, FragPos, viewDir);
    }

    FragColour = vec4(result * Colour, alpha);  // Use alpha uniform
}
"""

vertex_shader_points = """
#version 330 core
layout (location = 0) in vec3 aPos;      // Vertex position
layout (location = 1) in vec3 aColour;    // Vertex colour
layout (location = 2) in vec3 aNormal;   // Vertex normal

out vec3 FragPos;   // Fragment position in world space
out vec3 Normal;    // Fragment normal in world space
out vec3 Colour;     // Fragment colour

// Transformation matrices
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform float pointSize = 10.0;  // Added point size uniform

void main() {
    vec4 worldPos = model * vec4(aPos, 1.0);
    FragPos = worldPos.xyz;
    Normal = mat3(transpose(inverse(model))) * aNormal;
    Colour = aColour;
    gl_Position = projection * view * worldPos;
    gl_PointSize = pointSize;  // Set the point size
}
"""

fragment_shader_points = """
#version 330 core
in vec3 FragPos;
in vec3 Normal;
in vec3 Colour;

out vec4 FragColour;

uniform int pointShape = 0;  // 0=circle, 1=square, 2=triangle
uniform float alpha = 1.0;   // Add alpha uniform

void main() {
    // Convert from [0,1] to [-0.5,0.5]
    vec2 coord = gl_PointCoord - vec2(0.5);
    
    // Different shape masks
    bool inside = false;
    
    if (pointShape == 0) {  // Circle
        inside = length(coord) <= 0.5;
    }
    else if (pointShape == 1) {  // Square
        inside = max(abs(coord.x), abs(coord.y)) <= 0.5;
    }
    else if (pointShape == 2) {  // Triangle
        vec2 triCoord = vec2(coord.x * 2, coord.y + 0.5);
        inside = triCoord.y >= 0.0 &&
                triCoord.y <= 1.0 &&
                triCoord.x >= -triCoord.y &&
                triCoord.x <= triCoord.y;
    }
    
    if (!inside) discard;
    FragColour = vec4(Colour, alpha);  // Use alpha uniform
}
"""
    
class Shader:
    """OpenGL shader program wrapper supporting vertex and fragment shaders.
    
    Handles shader compilation, program linking, uniform setting, and common
    transformations for 3D rendering with lighting.
    """

    def __init__(self, vertex_shader, fragment_shader):
        """Initialize shader program from vertex and fragment shader sources.

        Parameters
        ----------
        vertex_shader : str
            GLSL vertex shader source code
        fragment_shader : str
            GLSL fragment shader source code
        
        Raises
        ------
        RuntimeError
            If shader compilation or program linking fails
        """
        self.vertex_shader = self.compile_shader(vertex_shader, GL_VERTEX_SHADER)
        self.fragment_shader = self.compile_shader(fragment_shader, GL_FRAGMENT_SHADER)
        self.program = shaders.compileProgram(self.vertex_shader, self.fragment_shader)
        self.validate_program()

    def compile_shader(self, source, shader_type):
        """Compile a single shader from source.

        Parameters
        ----------
        source : str
            GLSL shader source code
        shader_type : GL_enum
            GL_VERTEX_SHADER or GL_FRAGMENT_SHADER

        Returns
        -------
        int
            OpenGL shader object ID

        Raises
        ------
        RuntimeError
            If shader compilation fails
        """
        shader = shaders.compileShader(source, shader_type)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            print(f"Error: Shader compilation failed: {error}")
            raise RuntimeError(f"Shader compilation failed: {error}")
        return shader

    def validate_program(self):
        """Validate the shader program.

        Raises
        ------
        RuntimeError
            If program validation fails
        """
        glValidateProgram(self.program)
        if not glGetProgramiv(self.program, GL_VALIDATE_STATUS):
            error = glGetProgramInfoLog(self.program).decode()
            print(f"Error: Program validation failed: {error}")
            raise RuntimeError(f"Program validation failed: {error}")

    def use(self):
        """Activate this shader program for rendering."""
        glUseProgram(self.program)

    def set_uniform(self, name, value):
        """Set a uniform variable in the shader.

        Supports int, float, vec2/3/4, mat3/4 uniforms.

        Parameters
        ----------
        name : str
            Uniform variable name in shader
        value : int, float, list, tuple, np.ndarray
            Value to set. Type must match shader uniform type

        Raises
        ------
        ValueError
            If value type or size is not supported
        """
        location = glGetUniformLocation(self.program, name)
        if location == -1:
            # print(f"Error: Uniform '{name}' not found in shader program.")
            return

        if isinstance(value, int):
            glUniform1i(location, value)
        elif isinstance(value, float):
            glUniform1f(location, value)
        elif isinstance(value, (list, tuple, np.ndarray)):
            if isinstance(value, np.ndarray):
                value = value.flatten()
            if len(value) == 2:
                glUniform2f(location, *value)
            elif len(value) == 3:
                glUniform3f(location, *value)
            elif len(value) == 4:
                glUniform4f(location, *value)
            elif len(value) == 9:  # 3x3 matrix
                glUniformMatrix3fv(location, 1, GL_FALSE, (GLfloat * 9)(*value))
            elif len(value) == 16:  # 4x4 matrix
                glUniformMatrix4fv(location, 1, GL_FALSE, (GLfloat * 16)(*value))
            else:
                raise ValueError(f"Unsupported uniform vector size: {len(value)}")
        else:
            raise ValueError(f"Unsupported uniform type: {type(value)}")

    def set_light_uniforms(self, lights):
        """Set uniforms for all lights in the scene.

        Parameters
        ----------
        lights : list
            List of Light objects to upload to shader
        """
        self.use()
        self.set_uniform('numLights', len(lights))
        for i, light in enumerate(lights):
            light_data = light.get_uniform_data()
            for key, value in light_data.items():
                self.set_uniform(f'lights[{i}].{key}', value)

    def set_model_matrix(self, model_matrix):
        """Set the model transformation matrix.

        Parameters
        ----------
        model_matrix : np.ndarray
            4x4 model transformation matrix
        """
        self.set_uniform("model", model_matrix)

    def set_view_matrix(self, view_matrix):
        """Set the view transformation matrix.

        Parameters
        ----------
        view_matrix : np.ndarray
            4x4 view transformation matrix
        """
        self.set_uniform("view", view_matrix)

    def set_projection_matrix(self, projection_matrix):
        """Set the projection transformation matrix.

        Parameters
        ----------
        projection_matrix : np.ndarray
            4x4 projection transformation matrix
        """
        self.set_uniform("projection", projection_matrix)

    def set_view_position(self, view_position):
        """Set the camera position for lighting calculations.

        Parameters
        ----------
        view_position : np.ndarray
            3D camera position vector
        """
        self.set_uniform("viewPos", view_position)

    def set_point_shape(self, shape):
        """Set point shape: 0=circle, 1=square, 2=triangle."""

        if shape == PointShape.CIRCLE:
            shape = 0
        elif shape == PointShape.SQUARE:
            shape = 1
        elif shape == PointShape.TRIANGLE:
            shape = 2
        else:
            print(f"Warning: Unsupported point shape: {shape}")
            shape = 0
        
        self.set_uniform("pointShape", shape)

    def set_alpha(self, alpha):
        """Set the alpha (transparency) value for rendering."""
        self.set_uniform('alpha', alpha)

    def shutdown(self):
        """Delete shader program and individual shaders."""
        try:
            if self.program and bool(glDeleteProgram):  # Check if OpenGL functions are still available
                glDeleteProgram(self.program)
                self.program = None
            if self.vertex_shader and bool(glDeleteShader):
                glDeleteShader(self.vertex_shader)
                self.vertex_shader = None
            if self.fragment_shader and bool(glDeleteShader):
                glDeleteShader(self.fragment_shader)
                self.fragment_shader = None
        except:
            # Ignore errors during shutdown
            pass

    def __del__(self):
        """Ensure shader resources are cleaned up."""
        self.shutdown()

class DefaultShaders:
    """Manage default shaders."""
    default_shader = None
    default_point_shader = None

    @staticmethod
    def initialise():
        """Initialise default shaders, should be called once at start of program after OpenGL initialisation."""
        DefaultShaders.default_shader = Shader(vertex_shader_lighting, fragment_shader_lighting)
        DefaultShaders.default_point_shader = Shader(vertex_shader_points, fragment_shader_points)
