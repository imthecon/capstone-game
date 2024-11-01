# imports
import pygame
from pygame.locals import *

import button
import spritesheet

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

scroll_threshold = 250
screen_scroll = 0
scroll_mult = 2 # possibly change later (if scrolling makes the player slightly faster or slower, movement could be an issue)2
bg_scroll = 0

# level editor variables
rows = 18
max_cols = 100
 
# empty world data list
world_data = []

# create empty tile list
for row in range(rows):
  r = [0] * max_cols
  world_data.append(r)

# create ground
for tile in range(0, max_cols):
  world_data[rows - 3][tile] = 2

# load assets
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

# spritesheets
idle_main = pygame.image.load('assets/idle.png').convert_alpha()
walk_main = pygame.image.load('assets/walk.png').convert_alpha()

# animation list
animation_list = []
action = 0
last_update = pygame.time.get_ticks()
animation_cooldown = 150
frame = 0

temp_img_list = []

# idle animation
for i in range(13):
  temp_img_list.append(spritesheet.get_image(idle_main, i, 32, 64, 2, (0, 0, 0)))
animation_list.append(temp_img_list)
temp_img_list = []

# walking animation
for i in range(8):
  temp_img_list.append(spritesheet.get_image(walk_main, i, 32, 64, 2, (0, 0, 0)))
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
  
  def move(self):
    screen_scroll = 0
    
    # gravity
    self.dy -= self.gravity

    # move in the x direction
    self.rect.x += self.dx

    # x collision detection
    for tile in world.obstacle_list:
      if tile[1].colliderect(self.rect):
        if self.dx > 0: # moving right
          self.rect.right = tile[1].left
        if self.dx < 0: # moving left
          self.rect.left = tile[1].right

    # move in the y direction
    self.rect.y -= self.dy

    # y collision detection
    for tile in world.obstacle_list:
      if tile[1].colliderect(self.rect):
        if self.dy < 0: # above ground; falling
          self.rect.bottom = tile[1].top
          self.on_ground = True
          self.dy = 0
        if self.dy > 0: # below ground; jumping
          self.rect.top = tile[1].bottom
          self.dy = 0

    # update scroll based on player position
    if self.rect.right > screen.get_width() - scroll_threshold or self.rect.left < scroll_threshold:
      screen_scroll = -self.dx
      self.rect.x -= self.dx
    
    return screen_scroll
  
  def update(self):
    self.handle_input()
    self.move()
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
  pygame.draw.rect(screen, "black", (0, 0, 1920, 120))
  pygame.draw.rect(screen, "black", (0, 960, 1920, 120))

class World():
  def __init__(self):
    self.obstacle_list = []

  def process_data(self, data):
    # iterate through each value in world_data
    for y, row in enumerate(data):
      for x, tile in enumerate(row):
        if tile >= 1:
          img = pygame.transform.scale(grass_tiles[tile], (tile_size, tile_size))
          img_rect = img.get_rect()
          img_rect.x = x * tile_size
          img_rect.y = y * tile_size
          tile_data = (img, img_rect)
          self.obstacle_list.append(tile_data)
          if tile >= 1 and tile <= 9:
            self.obstacle_list.append(tile_data)
            
  def draw(self):
    for tile in self.obstacle_list:
      tile[1][0] += screen_scroll
      screen.blit(tile[0], tile[1])

# create instances
player = Player(500, screen_height - 320)
world = World()
world.process_data(world_data)

# game loop
run = True
while run:
  # events (general actions)
  for event in pygame.event.get():
    
    # quit the game
    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
      run = False
    
    # keypresses
    if event.type == pygame.KEYDOWN:
      # initial left/right press (animation control)
      if event.key == pygame.K_a:
        moving_left = True
        action = 1
        frame = 0
      if event.key == pygame.K_d:
        moving_right = True
        action = 1
        frame = 0
      
      # dialogue and credits
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
  screen_scroll = player.move()

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
