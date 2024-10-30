# imports
import pygame
from pygame.locals import *

# initialization
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1920
screen_height = 1080

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('CAPSTONE GAME (change later)')

screen.fill('white')

font1 = pygame.font.Font("fonts/Silkscreen-Regular.ttf", 24)
font2 = pygame.font.Font("fonts/Silkscreen-Regular.ttf", 36)
font3 = pygame.font.Font("fonts/Silkscreen-Regular.ttf", 48)
font4 = pygame.font.Font("fonts/Silkscreen-Regular.ttf", 72)

# define game variables
tile_size = 60 # 16:9 tile ratio
scroll_threshold = 300
screen_scroll = 0
scroll_mult = 2 # possibly change later (if scrolling makes the player slightly faster or slower, movement could be an issue)2
bg_scroll = 0

# load assets
grass_tile = pygame.image.load('assets/grass_tile.png')

# spritesheets
idle_main = pygame.image.load('assets/idle.png').convert_alpha()
walk_main = pygame.image.load('assets/walk.png').convert_alpha()

class SpriteSheet():
  def __init__(self, image):
    self.sheet = image
  
def get_image(sheet, frame, width, height, scale, colour):
  image = pygame.Surface((width, height)).convert()
  image.blit(sheet, (0, 0), ((frame * width), 0, width, height))
  image = pygame.transform.scale(image, (width * scale, height * scale))
  image.set_colorkey(colour)
  return image

# animation list
animation_list = []
action = 0
last_update = pygame.time.get_ticks()
animation_cooldown = 150
frame = 0

temp_img_list = []

# idle animation
for i in range(13):
  temp_img_list.append(get_image(idle_main, i, 32, 64, 2, (0, 0, 0)))
animation_list.append(temp_img_list)
temp_img_list = []

# walking animation
for i in range(8):
  temp_img_list.append(get_image(walk_main, i, 32, 64, 2, (0, 0, 0)))
animation_list.append(temp_img_list)
temp_img_list = []

print(animation_list)

# player action variables
moving_left = False
moving_right = False

# player
class Player():
  def __init__(self, x, y):
    img = pygame.image.load('assets/idle.png')
    self.image = pygame.transform.scale(animation_list[0][0], (64, 128))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.width = self.image.get_width()
    self.height = self.image.get_height()
    self.gravity = 0.35
    self.on_ground = False
    self.direction = 1
    self.flip = False
    self.dx = 0
    self.dy = 0
  
  def handle_input(self):
    global action, frame

    # keyboard inputs
    keys = pygame.key.get_pressed()

    # left/right pressed
    if moving_left:
      self.dx = max(self.dx - 0.2, -3) # start speeding up (to the left) from 0.25 to 3
      self.flip = True
      self.direction = -1
    elif moving_right:
      self.dx = min(self.dx + 0.2, 3) # start speeding up (to the right) from 0.25 to 3
      self.flip = False
      self.direction = 1
    else:
      self.dx *= 0.8
    
    # up pressed
    if keys[pygame.K_w]:
      if self.on_ground:
        self.dy = 10
        self.on_ground = False
        print(self.dy)
  
  def move(self, moving_left, moving_right):
    screen_scroll = 0
    
    # gravity
    self.dy -= self.gravity

    # move in the x direction
    self.rect.x += self.dx

    # x collision detection
    for tile in world.tile_list:
      if tile[1].colliderect(self.rect):
        if self.dx > 0: # moving right
          self.rect.right = tile[1].left
        if self.dx < 0: # moving left
          self.rect.left = tile[1].right

    # move in the y direction
    self.rect.y -= self.dy

    # y collision detection
    for tile in world.tile_list:
      if tile[1].colliderect(self.rect):
        if self.dy < 0: # falling
          self.rect.bottom = tile[1].top
          self.on_ground = True
          self.dy = 0
        if self.dy > 0: # jumping
          self.rect.top = tile[1].bottom
          self.dy = 0

    # update scroll based on player position
    if self.rect.right > screen.get_width() - scroll_threshold or self.rect.left < scroll_threshold:
      screen_scroll = -self.dx * scroll_mult
      self.rect.x -= self.dx
    
    return screen_scroll
  
  def update(self):
    self.handle_input()
    self.move(moving_left, moving_right)
    self.image = pygame.transform.scale(animation_list[action][frame], (64, 128))
    screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Message():
  def __init__(self, message, speed):
    self.message = message
    self.counter = 0
    self.speed = speed
    self.complete = False
  
  def draw(self):
    if self.counter < self.speed * len(self.message): # if the message has NOT completed rendering
      self.counter += 1
    elif self.counter >= self.speed * len(self.message): # if the message has completed rendering
      self.complete = True
    
    snippet = font1.render(self.message[0:self.counter // self.speed], True, "white") # render the text onto the screen

    x_pos = 960 - (snippet.get_width() // 2) # ensures the text is always centered after rerenders

    # black bars
    pygame.draw.rect(screen, "black", (0, 0, 1920, 120))
    pygame.draw.rect(screen, "black", (0, 960, 1920, 120))

    screen.blit(snippet, (x_pos, 1002.5))

messages = [
  Message("I don't know if I can carry on much longer.", speed=2),
  Message("It feels like I'm ... falling.", speed=2),
]
ellipse = Message("...", speed=2)
current_message_index = 0

class Credits():
  def __init__(self, speed, credits):
    self.credits = credits
    self.speed = speed
    self.surfaces = []
    self.y_offset = screen.get_height()
    self.running = False
    
    for line, font in credits:
      if font == font1:
        colour = "#A9A9A9"
      else:
        colour = "white"
      surface = font.render(line, True, colour)
      self.surfaces.append(surface)
    
  def draw(self):
    self.y_offset -= self.speed
    screen.fill("black")
    y = self.y_offset
    for surface in self.surfaces:
      x = (screen.get_width() - surface.get_width()) // 2 # centers each line
      screen.blit(surface, (x, y))
      y += surface.get_height()

credits_scene = Credits(
  speed=10,
  credits=[
    ("Credits", font3),

    ("", font1),
    ("Game Design", font2),
    ("Level Designer: Sarder", font1),
    ("UI/UX: Sarder", font1),

    ("", font1),
    ("Programming", font2),
    ("Lead Programmer: Sarder", font1),

    ("", font1),
    ("Art and Character Design", font2),
    ("Lead Artist: Jubi", font1),
    ("Character Artist: Jubi", font1),
    ("Animator: Jubi", font1),
    ("Environment Artist: Jubi", font1),
    ("Lighting and Ambience: Sarder", font1),

    ("", font1),
    ("Writing", font2),
    ("Story Writer: Sarder and Jubi", font1),
    ("Dialogue: Sarder and Jubi", font1),

    ("", font1),
    ("Sound Design", font2),
    ("VFX Artist: Sarder", font1),

    ("", font1),
    ("", font1),
    ("", font1),
    ("Software", font3),
    ("Coding Environment: Visual Studio Code", font1),
    ("Fonts: Google Fonts", font1),
    ("Pixel Art: ?", font1),
    ("Animation: ?", font1),
    ("Image/Animation Editing: Piskel", font1),

    ("", font1),
    ("", font1),
    ("", font1),
    ("", font1),
    ("", font1),
    ("Thanks for playing!", font4),
  ]
)

# background
def draw_bg():
  pygame.draw.rect(screen, "#708090", (0, 120, 1920, 840))

# grid/map
class World():
  def __init__(self, data):
    self.tile_list = []
    
    # load images
    grass_tl = pygame.image.load('assets/grass_tl.png')
    grass_tm = pygame.image.load('assets/grass_tm.png')
    grass_tr = pygame.image.load('assets/grass_tr.png')
    grass_ml = pygame.image.load('assets/grass_ml.png')
    grass_m = pygame.image.load('assets/grass_m.png')
    grass_mr = pygame.image.load('assets/grass_mr.png')
    grass_bl = pygame.image.load('assets/grass_bl.png')
    grass_bm = pygame.image.load('assets/grass_bm.png')
    grass_br = pygame.image.load('assets/grass_br.png')

    grass_tiles = {
      1: grass_tl,
      2: grass_tm,
      3: grass_tr,
      4: grass_ml,
      5: grass_m,
      6: grass_mr,
      7: grass_bl,
      8: grass_bm,
      9: grass_br,
    }

    row_count = 0
    for row in data:
      col_count = 0
      for tile in row:
        if tile != 0:
          img = pygame.transform.scale(grass_tiles[tile], (tile_size, tile_size))
          img_rect = img.get_rect()
          img_rect.x = col_count * tile_size
          img_rect.y = row_count * tile_size
          tile = (img, img_rect)
          self.tile_list.append(tile)
        col_count += 1
      row_count += 1
    
  def draw(self):
    for tile in self.tile_list:
      tile[1][0] += screen_scroll
      screen.blit(tile[0], tile[1])

world_data = [
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 1
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 2
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 3
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 4
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 0
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 6
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 7
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 8
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 9
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 10
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 11
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 12
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 13
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 14
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 10
  [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], # 16
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 17
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 18
]

# create instances
player = Player(500, screen_height - 320)
world = World(world_data)

# game loop
run = True
while run:
  # events (general actions)
  for event in pygame.event.get():
    
    # quit the game
    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
      run = False
    
    # initial left/right press (animation control)
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_a:
        moving_left = True
        action = 1
        frame = 0
      if event.key == pygame.K_d:
        moving_right = True
        action = 1
        frame = 0
      if event.key == pygame.K_e:
        if current_message_index < len(messages) and messages[current_message_index].complete:
          current_message_index += 1
      if event.key == pygame.K_c:
        credits_scene.running = True
    
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_a:
        moving_left = False
        if moving_right == 0:
          action = 0
          frame = 0
      if event.key == pygame.K_d:
        moving_right = False
        if moving_left == 0:
          action = 0
          frame = 0
  
  # world and player render/update
  draw_bg()
  world.draw()
  player.update()
  screen_scroll = player.move(moving_left, moving_right)

  # update animation
  current_time = pygame.time.get_ticks()
  if current_time - last_update >= animation_cooldown:
    frame += 1
    last_update = current_time
    if frame >= len(animation_list[action]):
      frame = 0
  
  print(action, frame, moving_left, moving_right)
  print(player.on_ground)

  # messages render
  if current_message_index < len(messages):
    messages[current_message_index].draw()
  else:
    ellipse.draw()

  # credits scene
  if credits_scene.running:
    credits_scene.draw()

  clock.tick(fps)
  pygame.display.flip()

pygame.quit()
