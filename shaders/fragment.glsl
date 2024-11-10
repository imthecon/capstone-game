#version 330 core

in vec2 fragmentTexCoord;

out vec4 color;
uniform sampler2D imageTexture;

uniform float time;

void main()
{
  color = vec4(texture(imageTexture, fragmentTexCoord).rgb * sin(time), 1.0);
}