#version 330 core

layout (location = 0) in vec2 aPos;

out vec2 fragPos;

uniform mat4 projection;
uniform vec2 cameraPos;

void main()
{
  fragPos = aPos - cameraPos;
  gl_Position = projection * vec4(aPos, 0.0, 1.0);
}