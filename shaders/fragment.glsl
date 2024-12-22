#version 330 core

in vec2 fragPos;

out vec4 FragColor;
uniform sampler2D imageTexture;

// uniform float time;
uniform vec3 fogColor;
uniform float fogStart;
uniform float fogEnd;
uniform int pixelationLevels;
uniform float pixelSize;
uniform vec3 bgColor;

void main()
{
  // color = vec4(texture(imageTexture, fragmentTexCoord).rgb * sin(time), 1.0);
  float distance = length(fragPos); // distance from camera to the fragment

  float fogFactor = (distance - fogStart) / (fogEnd - fogStart);
  fogFactor = clamp(fogFactor, 0.0, 1.0);

  fogFactor = floor(fogFactor * float(pixelationLevels)) / float(pixelationLevels);

  fogFactor = floor(fogFactor * (1.0 / pixelSize) / (1.0 / pixelSize));

  vec3 finalColor = mix(bgColor, vec3(1.0), fogFactor);

  FragColor = vec4(finalColor, 1.0);
}