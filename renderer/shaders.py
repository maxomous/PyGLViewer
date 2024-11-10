from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np

# Vertex shader for basic lighting and transformations
basic_vertex_shader = """
#version 330 core
layout (location = 0) in vec3 aPos;      // Vertex position
layout (location = 1) in vec3 aColor;    // Vertex color
layout (location = 2) in vec3 aNormal;   // Vertex normal

out vec3 FragPos;   // Fragment position in world space
out vec3 Normal;    // Fragment normal in world space
out vec3 Color;     // Fragment color

// Transformation matrices
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    vec4 worldPos = model * vec4(aPos, 1.0);
    FragPos = worldPos.xyz;
    Normal = mat3(transpose(inverse(model))) * aNormal;
    Color = aColor;
    gl_Position = projection * view * worldPos;
}
"""

# Fragment shader supporting multiple light types with Blinn-Phong lighting
basic_fragment_shader = """
#version 330 core
in vec3 FragPos;    // Fragment position in world space
in vec3 Normal;     // Fragment normal in world space
in vec3 Color;      // Fragment color

out vec4 FragColor;

#define MAX_LIGHTS 10

// Light structure supporting ambient, directional, point, and spot lights
struct Light {
    int type;           // 0=ambient, 1=directional, 2=point, 3=spot
    vec3 position;      // Position for point/spot lights
    vec3 direction;     // Direction for directional/spot lights
    vec3 color;        // Light color
    float intensity;    // Light intensity multiplier
    vec3 attenuation;   // Distance attenuation factors (constant, linear, quadratic)
    float cutoff;       // Spotlight cone angle in radians
};

uniform Light lights[MAX_LIGHTS];
uniform int numLights;
uniform vec3 viewPos;   // Camera position for specular calculation

vec3 calcLight(Light light, vec3 normal, vec3 fragPos, vec3 viewDir) {
    if (light.type == 0) {  // Ambient light
        return light.color * light.intensity;
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
    vec3 ambient = 0.1 * light.color;

    float diff = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = diff * light.color;

    vec3 halfwayDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(normal, halfwayDir), 0.0), 32.0);
    vec3 specular = spec * light.color;

    return (ambient + diffuse + specular) * light.intensity * attenuation;
}

void main() {
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);

    vec3 result = vec3(0.0);
    for (int i = 0; i < numLights; i++) {
        result += calcLight(lights[i], norm, FragPos, viewDir);
    }

    FragColor = vec4(result * Color, 1.0);
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
            print(f"Error: Uniform '{name}' not found in shader program.")
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

    def shutdown(self):
        """Delete shader program and individual shaders."""
        if self.program:
            glDeleteProgram(self.program)
            self.program = None
        if self.vertex_shader:
            glDeleteShader(self.vertex_shader)
            self.vertex_shader = None
        if self.fragment_shader:
            glDeleteShader(self.fragment_shader)
            self.fragment_shader = None

    def __del__(self):
        """Ensure shader resources are cleaned up."""
        self.shutdown()
