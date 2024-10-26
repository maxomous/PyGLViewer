from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np

basic_vertex_shader = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;
layout (location = 2) in vec3 aNormal;

out vec3 FragPos;
out vec3 Normal;
out vec3 Color;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
    Color = aColor;
    gl_Position = projection * view * vec4(FragPos, 1.0);
}
"""

basic_fragment_shader = """
#version 330 core
in vec3 FragPos;
in vec3 Normal;
in vec3 Color;

out vec4 FragColor;

#define MAX_LIGHTS 10

struct Light {
    int type;
    vec3 position;
    vec3 direction;
    vec3 color;
    float intensity;
    vec3 attenuation;
    float cutoff;
};

uniform Light lights[MAX_LIGHTS];
uniform int numLights;
uniform vec3 viewPos;

vec3 calcLight(Light light, vec3 normal, vec3 fragPos, vec3 viewDir) {
    if (light.type == 0) {  // Ambient light
        return light.color * light.intensity;
    }
    
    vec3 lightDir;
    float attenuation = 1.0;

    if (light.type == 1) {  // Directional light
        lightDir = normalize(-light.direction);
    } else {
        lightDir = normalize(light.position - fragPos);
        float distance = length(light.position - fragPos);
        attenuation = 1.0 / (light.attenuation.x + light.attenuation.y * distance + light.attenuation.z * distance * distance);

        if (light.type == 3) {  // Spot light
            float theta = dot(lightDir, normalize(-light.direction));
            if (theta <= cos(light.cutoff)) {
                return vec3(0.0);
            }
        }
    }

    // Ambient
    vec3 ambient = 0.1 * light.color;

    // Diffuse
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = diff * light.color;

    // Specular
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
    def __init__(self, vertex_shader, fragment_shader):
        self.program = shaders.compileProgram(
            self.compile_shader(vertex_shader, GL_VERTEX_SHADER),
            self.compile_shader(fragment_shader, GL_FRAGMENT_SHADER)
        )
        self.validate_program()

    def compile_shader(self, source, shader_type):
        shader = shaders.compileShader(source, shader_type)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            print(f"Shader compilation error: {error}")
            raise RuntimeError(f"Shader compilation failed: {error}")
        return shader

    def validate_program(self):
        glValidateProgram(self.program)
        if not glGetProgramiv(self.program, GL_VALIDATE_STATUS):
            error = glGetProgramInfoLog(self.program).decode()
            print(f"Program validation error: {error}")
            raise RuntimeError(f"Program validation failed: {error}")

    def use(self):
        glUseProgram(self.program)

    def set_uniform(self, name, value):
        location = glGetUniformLocation(self.program, name)
        if location == -1:
            print(f"Warning: Uniform '{name}' not found in shader program.")
            return

        if isinstance(value, int):
            glUniform1i(location, value)
        elif isinstance(value, float):
            glUniform1f(location, value)
        elif isinstance(value, (list, tuple, np.ndarray)):
            if isinstance(value, np.ndarray):
                value = value.flatten()  # Flatten the array
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
        self.use()
        self.set_uniform('numLights', len(lights))
        for i, light in enumerate(lights):
            light_data = light.get_uniform_data()
            for key, value in light_data.items():
                self.set_uniform(f'lights[{i}].{key}', value)

    def set_model_matrix(self, model_matrix):
        self.set_uniform("model", model_matrix)

    def set_view_matrix(self, view_matrix):
        self.set_uniform("view", view_matrix)

    def set_projection_matrix(self, projection_matrix):
        self.set_uniform("projection", projection_matrix)

    def set_view_position(self, view_position):
        self.set_uniform("viewPos", view_position)
