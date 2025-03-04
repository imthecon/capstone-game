import pygame

class SpriteSheet():
  def __init__(self, image):
    self.sheet = image
  
def get_image(sheet, frame, width, height, scale, colour):
  image = pygame.Surface((width, height)).convert()
  image.blit(sheet, (0, 0), ((frame * width), 0, width, height))
  image = pygame.transform.scale(image, (width * scale, height * scale))
  image.set_colorkey(colour)
  return image