# imports
import pygame
import csv
import math
import pygame_shaders
import moderngl
from array import array
import json
from pygame import mixer
import random

import button
import spritesheet

# pygame initialization
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1920
screen_height = 1080

screen_gl = pygame.display.set_mode((1920, 1080), pygame.OPENGL | pygame.DOUBLEBUF)
screen = pygame.Surface((1920, 1080))
pygame.display.set_caption('CAPSTONE GAME (change later)')

font1 = pygame.font.Font("fonts/Silkscreen-Regular.ttf", 24)
font2 = pygame.font.Font("fonts/Silkscreen-Regular.ttf", 36)
font3 = pygame.font.Font("fonts/Silkscreen-Regular.ttf", 48)
font4 = pygame.font.Font("fonts/Silkscreen-Regular.ttf", 72)

# mixer initialization (audio)
mixer.init()

sfx = {
  'jump': mixer.Sound('sounds/jump.wav'),
  'text_load': mixer.Sound('sounds/text_load.wav'),
  'change_mood': mixer.Sound('sounds/change_mood.wav'),
  'start': mixer.Sound('sounds/start.wav'),
  '1up': mixer.Sound('sounds/1up.wav'),
  'pickup': mixer.Sound('sounds/pickup.wav'),
  'fallen': mixer.Sound('sounds/fallen.wav'),
  'respawn': mixer.Sound('sounds/respawn.wav'),
  'hurt': mixer.Sound('sounds/hurt.wav'),
}

for key, sound in sfx.items():
  sound.set_volume(0.2)

# game state manager
# class Begin():
#   def __init__(self, display, gameStateManager):
#     self.display = display
#     self.gameStateManager = gameStateManager
#   def run(self):
#     self.display.fill('red')

# class Level():
#   def __init__(self, display, gameStateManager):
#     self.display = display
#     self.gameStateManager = gameStateManager
#   def run(self):
#     self.display.fill('blue')

# class GameStateManager():
#   def __init__(self, currentState):
#     self.currentState = currentState
  
#   def get_state(self):
#     return self.currentState
  
#   def set_state(self, state):
#     self.currentState = state

# gameStateManager = GameStateManager('begin')
# begin = Begin(screen, gameStateManager)
# level = Level(screen, gameStateManager)

# states = {'begin': begin, 'level': level}

# moderngl
ctx = moderngl.create_context()
quad_buffer = ctx.buffer(data=array('f', [
  # position (x, y), uv coords (x, y)
  -1.0, 1.0, 0.0, 0.0, # top left
  1.0, 1.0, 1.0, 0.0, # top right
  -1.0, -1.0, 0.0, 1.0, # bottom left
  1.0, -1.0, 1.0, 1.0, # bottom right
]))

vert_shader = '''
#version 330 core

in vec2 vert;
in vec2 texcoord;
out vec2 uvs;

void main() {
  uvs = texcoord;
  gl_Position = vec4(vert, 0.0, 1.0); // vert x, vert y, vert z, scale (?) - homegenous coordinate
}
'''

frag_shader = '''
#version 330 core

uniform sampler2D tex;
uniform float r_value;
uniform float g_value;
uniform float b_value;

in vec2 uvs;
out vec4 f_color;

void main(){
  vec4 tex_color = texture(tex, uvs);

  f_color = vec4(tex_color.r * r_value, tex_color.g * g_value, tex_color.b * b_value, tex_color.a);
}
'''

program = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
render_object = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

def surf_to_texture(surf):
  tex = ctx.texture(surf.get_size(), 4)
  tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
  tex.swizzle = 'BGRA'
  tex.write(surf.get_view('1'))
  return tex

# define game variables
scroll_threshold = 1000
screen_scroll = 0
scroll_mult = 2 # possibly change later (if scrolling makes the player slightly faster or slower, movement could be an issue)
bg_scroll = 1000

sign_audio_played = False
oneup_played = False

start_game = False

screen_shake = 0
switch_cooldown = 250

golden_leaf_collected = 0

reset_level = False
new_level_pause = False

level_messages = [
  "You tried your best!",
  "If you're reading this, hi!",
]

num_previous_signs = 0

reset_transition_timer = None

# closing black bars (transition)
bar_height = screen_height // 2

# level variables
rows = 18
cols = 100
tile_size = screen.get_height() // rows
level = 0
 
# empty world data list
world_data = []

# create empty tile list
for row in range(rows):
  r = [0] * cols
  world_data.append(r)

# load in level data and create world
# for tile in range(0, cols):
#   world_data[rows - 3][tile] = 2
with open(f'level{level}_data.csv', newline='') as csvfile:
  reader = csv.reader(csvfile, delimiter=",")
  for x, row in enumerate(reader):
    for y, tile in enumerate(row):
      world_data[x][y] = int(tile)

# title
title_img_temp = pygame.image.load('assets/title.png').convert_alpha()
title_img = pygame.transform.scale_by(title_img_temp, 2)

# emotions/moods
sadness_icon_base = pygame.image.load('assets/sadness.png').convert_alpha()
sadness_icon = pygame.transform.scale2x(sadness_icon_base)
fear_icon_base = pygame.image.load('assets/fear.png').convert_alpha()
fear_icon = pygame.transform.scale2x(fear_icon_base)
anxiety_icon_base = pygame.image.load('assets/anxiety.png').convert_alpha()
anxiety_icon = pygame.transform.scale2x(anxiety_icon_base)
happiness_icon_base = pygame.image.load('assets/happiness.png').convert_alpha()
happiness_icon = pygame.transform.scale2x(happiness_icon_base)

info_icon_base = pygame.image.load('assets/info.png').convert_alpha()
info_icon = pygame.transform.scale_by(info_icon_base, 1.5)

# tilesets
# with open('assets.json', 'r') as file:
#   assets = json.load(file)

# grass_tiles = assets['grass_tiles']
# misc_tiles = assets['misc_tiles']

# load assets
# load assets
grass_tiles_assets = {
  "grass_tl": pygame.image.load('assets/grass_tl.png').convert_alpha(),
  "grass_tm": pygame.image.load('assets/grass_tm.png').convert_alpha(),
  "grass_tm2": pygame.image.load('assets/grass_tm2.png').convert_alpha(),
  "grass_tm3": pygame.image.load('assets/grass_tm3.png').convert_alpha(),
  "grass_tr": pygame.image.load('assets/grass_tr.png').convert_alpha(),
  "grass_ml": pygame.image.load('assets/grass_ml.png').convert_alpha(),
  "grass_m": pygame.image.load('assets/grass_m.png').convert_alpha(),
  "grass_mr": pygame.image.load('assets/grass_mr.png').convert_alpha(),
  "grass_bl": pygame.image.load('assets/grass_bl.png').convert_alpha(),
  "grass_bm": pygame.image.load('assets/grass_bm.png').convert_alpha(),
  "grass_br": pygame.image.load('assets/grass_br.png').convert_alpha(),
  "grass_float1": pygame.image.load('assets/grass_float1.png').convert_alpha(),
  "grass_float2": pygame.image.load('assets/grass_float2.png').convert_alpha(),
  "grass_float3": pygame.image.load('assets/grass_float3.png').convert_alpha(),
  "grass_corner1": pygame.image.load('assets/grass_corner1.png').convert_alpha(),
  "grass_corner2": pygame.image.load('assets/grass_corner2.png').convert_alpha(),
  "grass_corner3": pygame.image.load('assets/grass_corner3.png').convert_alpha(),
  "grass_corner4": pygame.image.load('assets/grass_corner4.png').convert_alpha(),
}

misc_assets = {
  "sign": pygame.image.load('assets/sign.png').convert_alpha(),
  "flag": pygame.image.load('assets/flag.png').convert_alpha(),
  "location": pygame.image.load('assets/location.png').convert_alpha(),
}

brick_tiles_assets = {
  "brick_tl": pygame.image.load('assets/brick_tl.png').convert_alpha(),
  "brick_tm": pygame.image.load('assets/brick_tm.png').convert_alpha(),
  "brick_tr": pygame.image.load('assets/brick_tr.png').convert_alpha(),
  "brick_ml": pygame.image.load('assets/brick_ml.png').convert_alpha(),
  "brick_m": pygame.image.load('assets/brick_m.png').convert_alpha(),
  "brick_mr": pygame.image.load('assets/brick_mr.png').convert_alpha(),
  "brick_bl": pygame.image.load('assets/brick_bl.png').convert_alpha(),
  "brick_bm": pygame.image.load('assets/brick_bm.png').convert_alpha(),
  "brick_br": pygame.image.load('assets/brick_br.png').convert_alpha(),
}

hazard_assets = {
  "spike": pygame.image.load('assets/spike.png').convert_alpha(),
  "spike_left": pygame.image.load('assets/spike_left.png').convert_alpha(),
  "spike_right": pygame.image.load('assets/spike_right.png').convert_alpha(),
  "spike_top": pygame.image.load('assets/spike_top.png').convert_alpha(),
}
collectible_assets = {
  "golden_leaf": pygame.image.load('assets/golden_leaf.png').convert_alpha(),
}

grass_tiles = {}
misc_tiles = {}
brick_tiles = {}
hazard_tiles = {}
collectible_tiles = {}

asset_index = 1
for asset in grass_tiles_assets:
  grass_tiles.update({asset_index: grass_tiles_assets.get(asset)})
  asset_index += 1

for asset in misc_assets:
  misc_tiles.update({asset_index: misc_assets.get(asset)})
  asset_index += 1

for asset in brick_tiles_assets:
  brick_tiles.update({asset_index: brick_tiles_assets.get(asset)})
  asset_index += 1

for asset in hazard_assets:
  hazard_tiles.update({asset_index: hazard_assets.get(asset)})
  asset_index += 1

for asset in collectible_assets:
  collectible_tiles.update({asset_index: collectible_assets.get(asset)})
  asset_index += 1

# collectibles
golden_leaf_img = pygame.image.load('assets/golden_leaf.png').convert_alpha()

# collectibles = {
#   'golden_leaf': golden_leaf_img,
# }

# spritesheets
idle_main = pygame.image.load('assets/idle.png').convert_alpha()
walk_main = pygame.image.load('assets/walk.png').convert_alpha()
jump_main = pygame.image.load('assets/jump.png').convert_alpha()

idle_purple = pygame.image.load('assets/idle_purple.png').convert_alpha()
walk_purple = pygame.image.load('assets/walk_purple.png').convert_alpha()

idle_grey = pygame.image.load('assets/idle_grey.png').convert_alpha()
walk_grey = pygame.image.load('assets/walk_grey.png').convert_alpha()

idle_yellow = pygame.image.load('assets/idle_yellow.png').convert_alpha()
walk_yellow = pygame.image.load('assets/walk_yellow.png').convert_alpha()

fallen = pygame.image.load('assets/fallen.png').convert_alpha()

# animation list
animation_list = []
action = 0
last_update = pygame.time.get_ticks()
animation_cooldown = 150
frame = 0

temp_img_list = []

# idle animation (main)
for i in range(13):
  temp_img_list.append(spritesheet.get_image(idle_main, i, 32, 64, 2, (0, 0, 0)))
animation_list.append(temp_img_list)
temp_img_list = []

# walking animation (main)
for i in range(13):
  temp_img_list.append(spritesheet.get_image(walk_main, i, 32, 64, 2, (0, 0, 0)))
animation_list.append(temp_img_list)
temp_img_list = []

# jumping animation (main)
for i in range(4):
  temp_img_list.append(spritesheet.get_image(jump_main, i, 32, 64, 2, (0, 0, 0)))
animation_list.append(temp_img_list)
temp_img_list = []


# idle animation (purple)
for i in range(13):
  temp_img_list.append(spritesheet.get_image(idle_purple, i, 32, 64, 2, (0, 0, 0)))
animation_list.append(temp_img_list)
temp_img_list = []

# walking animation (purple)
for i in range(4):
  temp_img_list.append(spritesheet.get_image(walk_purple, i, 32, 64, 2, (0, 0, 0)))
animation_list.append(temp_img_list)
temp_img_list = []


# idle animation (grey)
for i in range(13):
  temp_img_list.append(spritesheet.get_image(idle_grey, i, 32, 64, 2, (0, 0, 0)))
animation_list.append(temp_img_list)
temp_img_list = []

# walking animation (grey)
for i in range(4):
  temp_img_list.append(spritesheet.get_image(walk_grey, i, 32, 64, 2, (0, 0, 0)))
animation_list.append(temp_img_list)
temp_img_list = []


# idle animation (yellow)
for i in range(13):
  temp_img_list.append(spritesheet.get_image(idle_yellow, i, 32, 64, 2, (0, 0, 0)))
animation_list.append(temp_img_list)
temp_img_list = []

# walking animation (yellow)
for i in range(4):
  temp_img_list.append(spritesheet.get_image(walk_yellow, i, 32, 64, 2, (0, 0, 0)))
animation_list.append(temp_img_list)
temp_img_list = []

temp_anim_array = animation_list.copy()

# fallen animation
for i in range(9):
  temp_img_list.append(spritesheet.get_image(fallen, i, 96, 64, 2, (0, 0, 0)))
animation_list[3] = temp_img_list

# player action variables
moving_left = False
moving_right = False

# outline
def outline(img, loc, alpha):
  mask = pygame.mask.from_surface(img)
  mask_surf = mask.to_surface(None, None, None, (255, 255, 255, alpha))
  mask_surf.set_colorkey((0, 0, 0))
  screen.blit(mask_surf, (loc[0] - 1, loc[1]))
  screen.blit(mask_surf, (loc[0] + 1, loc[1]))
  screen.blit(mask_surf, (loc[0], loc[1] - 1))
  screen.blit(mask_surf, (loc[0], loc[1] + 1))

# player
class Player():
  def __init__(self, x, y):
    self.pixel_w = 60
    self.pixel_h = 120
    self.image = pygame.transform.scale(animation_list[0][0], (self.pixel_w, self.pixel_h))
    self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())
    self.width_adjustment = 30
    self.rect.width -= self.width_adjustment
    self.rect.height -= 16
    # self.rect.x = x
    # self.rect.y = y
    # self.width = self.image.get_width()
    # self.height = self.image.get_height()
    self.gravity = 0.25
    self.on_ground = False
    self.jumping = False
    self.jump_timer = 0
    self.max_jump_time = 5 
    self.direction = 1
    self.flip = False
    self.dx = 0
    self.dy = 0
    self.max_speed = 1
    self.energy = 350
    self.mood = 1
    
    self.touching_hazard = False

    self.fallen = False
    self.fallen_start_time = None

    self.coyote_timer = 0
    self.coyote_time_limit = 100
    self.jumped_during_coyote = False

    self.energy_loss_mult = 1
  
  def handle_input(self):
    global action, frame, animation_cooldown

    # keyboard inputs
    keys = pygame.key.get_pressed()

    # left/right pressed
    if moving_left:
      # self.dx = max(self.dx - 0.1, -2) # start speeding up (to the left) from 0.25 to 3
      self.dx = -self.max_speed
      self.flip = True
      self.direction = -1
      self.energy -= (0.05 * player.max_speed) / self.energy_loss_mult
    elif moving_right:
      # self.dx = min(self.dx + 0.1, 2) # start speeding up (to the right) from 0.25 to 3
      self.dx = self.max_speed
      self.flip = False
      self.direction = 1
      self.energy -= (0.05 * player.max_speed) / self.energy_loss_mult
    else:
      self.dx = 0
    
    # coyote timer
    if self.on_ground:
      self.coyote_timer = pygame.time.get_ticks()
      self.jumped_during_coyote = False
    
    # if player presses space while on the ground, set jumping to true and reset jump variables
    if keys[pygame.K_SPACE] and not new_level_pause and not player.fallen:
      current_time = pygame.time.get_ticks()

      if self.on_ground or current_time - self.coyote_timer <= self.coyote_time_limit and not self.jumped_during_coyote:
        sfx['jump'].play()
        self.jumping = True
        self.jump_timer = 0
        self.dy = 7
        frame = 0
        # action = 2
        self.on_ground = False
        self.jumped_during_coyote = True

    # change dy in increasing amounts as player holds space longer
    if keys[pygame.K_SPACE] and self.jumping and self.mood == 4:
      if self.jump_timer < self.max_jump_time:
        self.jump_timer += 1
        self.dy = 5 + 3 * (self.jump_timer / self.max_jump_time)
      else:
        self.jumping = False

    # set jumping to false when space bar is not being pressed
    if not keys[pygame.K_SPACE]:
      self.jumping = False
      if action == 2 and frame == 3:
        frame = 0
        if not keys[pygame.K_a] and not keys[pygame.K_d]:
          action = 0
        else:
          action = 1
    
    # if keys[pygame.K_SPACE] and self.dy < 1:
    #   self.dy += 0.5
    
    # if the player pressed shift to sprint
    if keys[pygame.K_LSHIFT] and self.mood == 2:
      player.max_speed = 3
      if self.dx != 0:
        if action == 2:
          animation_cooldown = 150
        else:
          animation_cooldown = 75
    else:
      player.max_speed = 2
      animation_cooldown = 150

  def move(self):
    global action, frame, reset_level, adjusted_hitbox

    screen_scroll = 0

    # gravity
    if not self.on_ground:
      if self.dy < 0:
        self.dy -= self.gravity * 1.5 # if player is falling, gravity is stronger
      else:
        self.dy -= self.gravity # if player is jumping, gravity is weaker

    # move in the x direction
    self.rect.x += self.dx

    # x collision detection
    for tile in world.obstacle_list:
      if tile[1].colliderect(self.rect):
        if self.dx > 0: # moving right
          self.dx = 0
          self.rect.right = tile[1].left
          self.energy += (0.05 * player.max_speed) / 2 # counter energy loss from running into wall
        if self.dx < 0: # moving left
          self.dx = 0
          self.rect.left = tile[1].right
          self.energy += (0.05 * player.max_speed) / 2 # counter energy loss from running into wall

    # move in the y direction
    self.rect.y -= self.dy

    # y collision detection
    self.on_ground = False
    for tile in world.obstacle_list:
      if tile[1].colliderect(self.rect):
        if self.dy < 0: # above ground; falling
          self.rect.bottom = tile[1].top
          self.dy = 0
          self.on_ground = True
        if self.dy > 0: # below ground; jumping
          self.rect.top = tile[1].bottom
          self.dy = 0
    
    # reduce energy based on player's y velocity:
    if self.dy > self.gravity:
      self.energy -= 0.05 * abs(self.dy) / self.energy_loss_mult
    
    # finish flag touching detection (next level)
    for tile in world.non_obstacle_list:
      if tile[2] == 20:
        if tile[1].colliderect(self.rect):
          reset_level = True
    
    # update scroll based on player position
    if self.rect.right > screen.get_width() - scroll_threshold or self.rect.left < scroll_threshold:
      self.rect.x -= self.dx
      screen_scroll = -self.dx * 2
    
    return screen_scroll
  
  def update(self):
    global action, frame, moving_right, moving_left, bar_height, reset_level, animation_cooldown

    self.handle_input()
    self.move()
    self.image = pygame.transform.scale(animation_list[action][frame], (self.pixel_w, self.pixel_h))

    # change energy loss based on player emotion
    if self.mood == 1:
      self.energy_loss_mult = 2
    else:
      self.energy_loss_mult = 1

    if not self.fallen or not self.flip:
      screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
    else:
      screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 128, self.rect.y, self.rect.width, self.rect.height))
    
    # check if player is touching hazards
    for tile in world.hazard_list:
      if self.rect.colliderect(tile[1].inflate(5, 0)):
        self.touching_hazard = True
        self.dy = 0
        self.gravity = 0
    
    # fallen off the map detection
    if self.rect.y > 1080:
      self.touching_hazard = True
    
    if not self.fallen and ((self.energy < 0 and self.on_ground) or self.touching_hazard):
      self.energy = 0

      self.fallen = True

      if self.touching_hazard:
        sfx['hurt'].play()

      sfx['fallen'].play()

      moving_right = False
      moving_left = False

      action = 3
      frame = 0

      self.pixel_w = 188

      self.fallen_start_time = pygame.time.get_ticks()
    
    if self.fallen and self.fallen_start_time:
      animation_cooldown = 50
      
      elapsed_time = pygame.time.get_ticks() - self.fallen_start_time

      if elapsed_time >= 2000:
        reset_level = True
      
class Collectible(pygame.sprite.Sprite):
  def __init__(self, item_type, x, y, scale):
    pygame.sprite.Sprite.__init__(self)
    self.item_type = item_type
    img = collectibles[self.item_type]
    self.image = pygame.transform.scale(img, (tile_size * scale, tile_size * scale))

    self.rect = self.image.get_rect()
    self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    self.start_y = y
  
  def update(self):
    global golden_leaf_collected

    # check if the player has picked up the item
    if pygame.sprite.collide_rect(self, player):
      # check what type of collectible it was
      if self.item_type == 'golden_leaf':
        sfx['pickup'].play()
        trigger_transition = True
        golden_leaf_collected += 1
      # delete the collectible
      self.kill()
    
    # bobbing up and down animation
    time = pygame.time.get_ticks() / 1000 # time in seconds
    amplitude = 2
    frequency = 1
    self.rect.y = self.start_y + amplitude * math.sin(2 * math.pi * frequency * time)

# create collectible groups
# collectible_group = pygame.sprite.Group()

class EnergyBar():
  def __init__(self, x, y, energy, max_energy):
    self.x = x
    self.y = y
    self.energy = energy
    self.max_energy = max_energy

  def draw(self, energy):
    # update with new energy
    self.energy = energy

    # calculate energy ratio
    ratio = self.energy / self.max_energy

    pygame.draw.rect(screen, 'white', (self.x, self.y, 400, 40))
    pygame.draw.rect(screen, 'cornflowerblue', (self.x + 5, self.y + 5, 390 * ratio, 30))

class Message():
  def __init__(self, message, speed):
    self.message = message
    self.counter = 0
    self.speed = speed
    self.complete = False
  
  def draw(self):
    if not self.complete: # if the message has NOT completed rendering
      self.counter += 1
      
      if self.counter >= self.speed * len(self.message): # if the message has completed rendering
        self.complete = True
    
    snippet = font1.render(self.message[0:self.counter // self.speed], True, "white") # render the text onto the screen

    x_pos = 960 - (snippet.get_width() // 2) # ensures the text is always centered after rerenders

    pygame.draw.rect(screen, 'black', (x_pos - 10, 990, snippet.get_width() + 20, snippet.get_height() + 10))
    screen.blit(snippet, (x_pos, 995))

messages = [
  Message("I don't know if I can carry on much longer.", speed=2),
  Message("It feels like I'm ... falling.", speed=2),
  Message("3", speed=2),
  Message("4", speed=2),
  Message("5", speed=2),
  Message("6", speed=2),
]
ellipse = Message("...", speed=2)

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

# draw text
def draw_text(text, font, colour, x, y):
  text_surface = font.render(text, True, colour)
  screen.blit(text_surface, (x, y))
  return text_surface

# background
bg_layer1_main_base = pygame.image.load('assets/tree1.png').convert_alpha()
bg_layer1_main = pygame.transform.scale_by(bg_layer1_main_base, 6)

bg_layer2_main_base = pygame.image.load('assets/tree2.png').convert_alpha()
bg_layer2_main = pygame.transform.scale_by(bg_layer2_main_base, 6)

bg_layer3_main_base = pygame.image.load('assets/tree3.png').convert_alpha()
bg_layer3_main = pygame.transform.scale_by(bg_layer3_main_base, 6)

bg_layer1_city_base = pygame.image.load('assets/city1.png').convert_alpha()
bg_layer1_city = pygame.transform.scale_by(bg_layer1_city_base, 6)

bg_layer2_city_base = pygame.image.load('assets/city2.png').convert_alpha()
bg_layer2_city = pygame.transform.scale_by(bg_layer2_city_base, 6)

bg_layer3_city_base = pygame.image.load('assets/city3.png').convert_alpha()
bg_layer3_city = pygame.transform.scale_by(bg_layer3_city_base, 6)


def draw_bg():
  # screen.fill('white')
  width = bg_layer1_main.get_width()
  if level == 0:
    for i in range(10):
      screen.blit(bg_layer1_main, (((i * width)) - bg_scroll * 0.5, 0))
      screen.blit(bg_layer2_main, (((i * width)) - bg_scroll * 0.7, 0))
      screen.blit(bg_layer3_main, (((i * width)) - bg_scroll * 0.9, 0))
  elif level == 1:
    for i in range(10):
      screen.blit(bg_layer1_city, (((i * width)) - bg_scroll * 0.5, 0))
      screen.blit(bg_layer2_city, (((i * width)) - bg_scroll * 0.7, 0))
      screen.blit(bg_layer3_city, (((i * width)) - bg_scroll * 0.9, 0))
    

# black bars
def draw_black_bars():
  # pygame.draw.rect(screen, "black", (0, 0, 1920, 135))
  # pygame.draw.rect(screen, "black", (0, 945, 1920, 135))
  pass

# def screen_wipe():
#   rect_x = 1920
#   rect = pygame.draw.rect(screen, 'black', (rect_x, 0, 1920, 1080))
#   rect_x -= 5

class World():
  def __init__(self):
    self.obstacle_list = []
    self.hazard_list = []
    self.non_obstacle_list = []
    self.collectible_list = []
    self.sign_list = []
    self.sign_id = None

  def process_data(self, data):
    # iterate through each value in world_data
    for y, row in enumerate(data):
      for x, tile in enumerate(row):
        if tile >= 1 and tile <= 18:
          img = pygame.transform.scale(grass_tiles.get(tile), (tile_size, tile_size))
          img_rect = img.get_rect()
          img_rect.x = x * tile_size - (tile_size * 10)
          img_rect.y = y * tile_size
          tile_data = (img, img_rect, tile)
          self.obstacle_list.append(tile_data)
        elif tile >= 19 and tile <= 21:
          img = pygame.transform.scale(misc_tiles.get(tile), (tile_size, tile_size))
          img_rect = img.get_rect()
          img_rect.x = x * tile_size - (tile_size * 10)
          img_rect.y = y * tile_size + 10
          tile_data = (img, img_rect, tile)
          self.non_obstacle_list.append(tile_data)
          if tile == 19: # sign
            self.sign_list.append((img, img_rect, x, self.sign_id))
        elif tile >= 22 and tile <= 30:
          img = pygame.transform.scale(brick_tiles.get(tile), (tile_size, tile_size))
          img_rect = img.get_rect()
          img_rect.x = x * tile_size - (tile_size * 10)
          img_rect.y = y * tile_size
          tile_data = (img, img_rect, tile)
          self.obstacle_list.append(tile_data)
        elif tile >= 31 and tile <= 34:
          img = pygame.transform.scale(hazard_tiles.get(tile), (tile_size, tile_size))
          img_rect = img.get_rect()
          if tile == 31:
            img_rect.height //= 2
            img_rect.x = x * tile_size - (tile_size * 10)
            img_rect.y = y * tile_size + 42
          elif tile == 32:
            img_rect.x = x * tile_size - (tile_size * 10) - 30
            img_rect.y = y * tile_size
          elif tile == 33:
            img_rect.width //= 2.
            img_rect.x = x * tile_size - (tile_size * 10) + 30
            img_rect.y = y * tile_size
          elif tile == 34:
            img_rect.x = x * tile_size - (tile_size * 10)
            img_rect.y = y * tile_size - 42
          tile_data = (img, img_rect, tile)
          self.hazard_list.append(tile_data)
        elif tile >= 35:
          img = pygame.transform.scale(collectible_tiles.get(tile), (tile_size - 12, tile_size - 12))
          img_rect = img.get_rect()
          img_rect.height //= 2
          img_rect.x = x * tile_size - (tile_size * 10)
          img_rect.y = y * tile_size
          tile_data = (img, img_rect, tile)
          self.collectible_list.append(tile_data)
      
      self.sign_list.sort(key=lambda sign: sign[2]) # sort sign_list by csv (grid) x (lowest to highest)
      
      # assign sign_id based on csv (grid) x position (first)
      for sign_id, sign in enumerate(self.sign_list):
        # replace the None value with the assigned sign_id
        self.sign_list[sign_id] = (sign[0], sign[1], sign[2], sign_id)
    
  def draw(self):
    for tile in self.obstacle_list:
      tile[1][0] += screen_scroll
      screen.blit(tile[0], (tile[1][0] + player.width_adjustment // 2, tile[1][1])) # player hitbox change here
    for tile in self.hazard_list:
      tile[1][0] += screen_scroll
      screen.blit(tile[0], (tile[1][0] + player.width_adjustment // 2, tile[1][1])) # player hitbox change here
    for tile in self.non_obstacle_list:
      tile[1][0] += screen_scroll
      screen.blit(tile[0], (tile[1][0] + player.width_adjustment // 2, tile[1][1]))
    for tile in self.collectible_list:
      tile[1][0] += screen_scroll
      screen.blit(tile[0], (tile[1][0] + player.width_adjustment // 2, tile[1][1]))

# create instances
player = Player(960, screen_height - 400)
energy_bar = EnergyBar(245, 45, player.energy, player.energy)

# golden_leaf = Collectible('golden_leaf', 800, 700, 1)
# collectible_group.add(golden_leaf)

world = World()
world.process_data(world_data)

total_collectibles = len(world.collectible_list)

# game loop
run = True
while run:
  if start_game == False:
    screen.fill('black')
    screen.blit(title_img, (screen_width // 2 - 600, screen_height // 2 - 256))
    draw_text("Press [T] to begin", font2, 'white', screen_width // 2 - 200, screen_height // 2 + 100)

  else:
    # world render/update
    draw_bg()
    world.draw()
    draw_black_bars()

    screen_scroll = player.move()
    bg_scroll -= screen_scroll

    # check if sign nearby
    for index, sign in enumerate(world.sign_list):
      if player.rect.colliderect(sign[1].inflate(150, 150)):
        if messages[num_previous_signs + sign[3]].counter == 1:
          sfx['text_load'].play()

        mark_base = pygame.image.load('assets/mark.png').convert_alpha()
        mark = pygame.transform.scale_by(mark_base, 1.5)
        mark_width, mark_height = mark.get_size()

        time = pygame.time.get_ticks() / 1000
        amplitude = 2
        frequency = 1

        x_pos = sign[1].centerx - mark_width // 2
        y_pos = sign[1].top - mark_height - 5

        screen.blit(mark, (x_pos + player.width_adjustment // 2, y_pos + amplitude * math.sin(2 * math.pi * frequency * time)))
    
    # player update
    player.update()
      
    for index, sign in enumerate(world.sign_list):
      if player.rect.colliderect(sign[1].inflate(150, 150)):
        messages[num_previous_signs + sign[3]].draw()
      else:
        messages[num_previous_signs + sign[3]].counter = 0
        messages[num_previous_signs + sign[3]].complete = False
    
    
    # energy bar update
    energy_bar.draw(player.energy)
    draw_text('Energy:', font2, 'white', 50, 40)

    # level information
    draw_text(f'Level {level + 1}', font2, 'white', 870, 40)

    # collection update
    screen.blit(pygame.transform.scale2x(golden_leaf_img), (1700, 40))
    draw_text(f'{golden_leaf_collected}/{total_collectibles}', font3, 'white', 1780, 40)

    # collection update
    for tile in world.collectible_list:
      if tile[2] == 35: # golden leaf
        start_y = tile[1].y

        time = pygame.time.get_ticks() / 1000
        amplitude = 1  # up and down movement range
        frequency = 2  # speed of oscillation

        # cosine-based easing
        tile[1].y = start_y + amplitude * math.cos(2 * math.pi * frequency * time)

        if tile[1].colliderect(player.rect):
          sfx['pickup'].play()
          golden_leaf_collected += 1
          world.collectible_list.remove(tile)

    # emotions
    if player.mood == 1: # sadness
      outline(sadness_icon, (100, 300), 255)
      sadness_icon.set_alpha(255)
      draw_text('[1] Sadness', font2, 'white', 190, 305)
    else:
      outline(sadness_icon, (100, 300), 50)
      sadness_icon.set_alpha(50)
      draw_text('[1] Sadness', font1, 'white', 190, 315)
    screen.blit(sadness_icon, (100, 300))

    if player.mood == 2: # fear
      outline(fear_icon, (100, 390), 255)
      fear_icon.set_alpha(255)
      draw_text('[2] Fear', font2, 'white', 190, 395)
    else:
      outline(fear_icon, (100, 390), 50)
      fear_icon.set_alpha(50)
      draw_text('[2] Fear', font1, 'white', 190, 405)
    screen.blit(fear_icon, (100, 390))
    
    if player.mood == 3: # anxiety
      outline(anxiety_icon, (100, 480), 255)
      anxiety_icon.set_alpha(255)
      draw_text('[3] Anxiety', font2, 'white', 190, 485)
    else:
      outline(anxiety_icon, (100, 480), 50)
      anxiety_icon.set_alpha(50)
      draw_text('[3] Anxiety', font1, 'white', 190, 495)
    screen.blit(anxiety_icon, (100, 480))

    if player.mood == 4: # happiness
      outline(happiness_icon, (100, 570), 255)
      happiness_icon.set_alpha(255)
      draw_text('[4] Happiness', font2, 'white', 190, 575)
    else:
      outline(happiness_icon, (100, 570), 50)
      happiness_icon.set_alpha(50)
      draw_text('[4] Happiness', font1, 'white', 190, 585)
    screen.blit(happiness_icon, (100, 570))

    # info icons
    icon_positions = [(40, 305), (40, 395), (40, 485), (40, 575)]
    
    icon_rects = []

    icon_info = [
      "Sadness: Basic movement; conserve energy",
      "Fear: Hold shift to sprint",
      "Anxiety: ?",
      "Happiness: Hold jump to jump higher",
    ]

    for pos in icon_positions:
      rect = screen.blit(info_icon, pos)
      icon_rects.append(rect)

    for i, rect in enumerate(icon_rects):
      if rect.collidepoint(pygame.mouse.get_pos()):
        info_text = draw_text(icon_info[i], font1, "white", icon_rects[i][0] + 60, icon_rects[i][1])
        pygame.draw.rect(screen, 'black', (icon_rects[i].x + 60, icon_rects[i].y, info_text.get_width() + 20, info_text.get_height() + 10))
        
        draw_text(icon_info[i], font1, "white", icon_rects[i][0] + 70, icon_rects[i][1] + 5)

    # update and draw groups
    # for collectible in collectible_group:
    #   collectible.rect.x += screen_scroll
    # collectible_group.update()
    # collectible_group.draw(screen)

    # update animation
    current_time = pygame.time.get_ticks()
    if current_time - last_update >= animation_cooldown:
      frame += 1
      last_update = current_time       
      if frame >= len(animation_list[action]):
        if action == 3:
          frame = 8
        else:
          frame = 0

    # messages render
    # if current_message_index < len(messages) and start_game == True:
    #   messages[current_message_index].draw()
    # else:
    #   ellipse.draw()

    # credits scene
    if credits_scene.running:
      credits_scene.draw()

    # reset emotion/mood switch cooldown
    if switch_cooldown < 250:
      switch_cooldown += 1
    
    ratio = switch_cooldown / 250
    pygame.draw.rect(screen, 'white', (50, 250, 200, 30))
    pygame.draw.rect(screen, 'crimson', (55, 255, 190 * ratio, 20))
    if switch_cooldown < 250:
      draw_text('ON COOLDOWN', font1, 'white', 270, 250)
    else:
      draw_text('READY', font1, 'white', 270, 250)

    # screen shake
    if screen_shake > 0:
      screen_shake -= 1

    render_offset = [0, 0]
    if screen_shake:
      render_offset[0] = random.randint(0, 20) - 10
      render_offset[1] = random.randint(0, 20) - 10
    
    screen.blit(screen, render_offset)

  # events (general actions)
  for event in pygame.event.get():
    
    # quit the game
    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
      run = False

    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_t and not start_game:
        start_game = True
        sfx['start'].play()

      if start_game:
        # "curtain" opening for a new level
        if bar_height == 640 and event.key == pygame.K_e:
          player.mood = 1
          switch_cooldown = 250

          animation_list[0] = temp_anim_array[0]
          animation_list[1] = temp_anim_array[1]
          frame = 0

          sfx['start'].play()
          new_level_pause = False
      
      if start_game and not new_level_pause and not player.fallen: 
        # initial left/right press (animation control)
        if event.key == pygame.K_a:
          moving_left = True
          if moving_right == False:
            frame = 0
            action = 1
        if event.key == pygame.K_d:
          moving_right = True
          if moving_left == False:
            frame = 0
            action = 1

        # dialogue and credits
        # if event.key == pygame.K_e:
        #   if current_message_index < len(messages) and messages[current_message_index].complete:
        #     current_message_index += 1
        # if event.key == pygame.K_z:
        #   credits_scene.running = True

        # emotion changing
        if switch_cooldown == 250:
          if (event.key == pygame.K_1 and player.mood != 1): # sadness
            player.mood = 1
            screen_shake = 30
            sfx['change_mood'].play()
            switch_cooldown = 0

            # character swaps
            animation_list[0] = temp_anim_array[0]
            animation_list[1] = temp_anim_array[1]
            frame = 0

          if event.key == pygame.K_2 and player.mood != 2 and not keys[pygame.K_SPACE]: # fear
            player.mood = 2
            screen_shake = 30
            sfx['change_mood'].play()
            switch_cooldown = 0

            # scaled_screen = pygame.transform.scale_by(screen, 0.9)
            # offset_x = (scaled_screen.get_width() - screen.get_width()) // 2
            # offset_y = (scaled_screen.get_height() - screen.get_height()) // 2

            # character swaps
            animation_list[0] = temp_anim_array[3]
            animation_list[1] = temp_anim_array[4]
            frame = 0

          if event.key == pygame.K_3 and player.mood != 3 and not keys[pygame.K_SPACE]: # anxiety
            player.mood = 3
            screen_shake = 30
            sfx['change_mood'].play()
            switch_cooldown = 0

            # character swaps
            animation_list[0] = temp_anim_array[5]
            animation_list[1] = temp_anim_array[6]
            frame = 0

          
          if event.key == pygame.K_4 and player.mood != 4 and not keys[pygame.K_SPACE]: # happiness
            player.mood = 4
            screen_shake = 30
            sfx['change_mood'].play()
            switch_cooldown = 0

            # character swaps
            animation_list[0] = temp_anim_array[7]
            animation_list[1] = temp_anim_array[8]
            frame = 0

    if start_game == True and not new_level_pause and not player.fallen:
      if event.type == pygame.KEYUP:
        if event.key == pygame.K_a:
          moving_left = False
          if moving_right == False:
            frame = 0
            action = 0
        if event.key == pygame.K_d:
          moving_right = False
          if moving_left == False:
            frame = 0
            action = 0
        # if event.key == pygame.K_LSHIFT:
        #   player.max_speed = 2
        #   frame = 0
        #   if player.dx != 0:
        #     action = 1
        #   else:
        #     action = 0
    
    if start_game == True:
      keys = pygame.key.get_pressed()

  #     if keys[pygame.K_c] and player.mood == 1:
  #       if player.pixel_w >= 40 and player.pixel_h >= 80:
  #         player.rect.width -= 3
  #         player.rect.height -= 7
  #         player.pixel_w -= 4
  #         player.pixel_h -= 8
  
  # # if player is sad and small, make her big
  # if player.mood == 1:
  #   if player.pixel_w <= 40 and player.pixel_h <= 80:
  #     player.rect.w += 3
  #     player.rect.h += 7
  #     player.pixel_w += 4
  #     player.pixel_h += 8
  #   print(player.rect.w, player.rect.h, player.pixel_w, player.pixel_h)

  # "curtain" opening for the game / level reset / player fallen
  if start_game == True:
    if bar_height >= 10 and not new_level_pause:
      bar_height -= 10
    pygame.draw.rect(screen, 'black', (0, 0, screen_width, bar_height))
    pygame.draw.rect(screen, 'black', (0, screen_height - bar_height, screen_width, bar_height))
    if new_level_pause:
      new_level_text = font1.render(level_messages[level], True, "white")
      new_level_text_rect = new_level_text.get_rect()
      new_level_text_rect.center = (screen.get_width() // 2, screen.get_height() // 2)
      screen.blit(new_level_text, new_level_text_rect)

      next_text = font2.render("Press [E] to continue.", True, "white")
      next_text_rect = next_text.get_rect()
      next_text_rect.center = (screen.get_width() // 2, 1000)
      screen.blit(next_text, next_text_rect)
  
  # if bar_height >= 10 and new_level_pause:
  #   bar_height -= 10

  # if bar_height == 0:
  #   new_level_pause = False

  # level switch bar close and open
  if reset_level:
    bar_height = 640

    # play 1up sound effect
    if not oneup_played:
      sfx['1up'].play()
      oneup_played = True

    # add number of signs to list (before changing world)
    if not player.fallen:
      for sign in world.sign_list:
        num_previous_signs += 1

    # empty current world data
    with open(f'level{level}_data.csv', newline='') as csvfile:
      reader = csv.reader(csvfile, delimiter=",")
      for x, row in enumerate(reader):
        for y, tile in enumerate(row):
          world_data[x][y] = 0
    
    # change level
    if not player.fallen:
      level += 1
    
    # reset and create new world, player, and other instances
    bg_scroll = 1000
    animation_cooldown = 150
    golden_leaf_collected = 0

    player = Player(960, screen_height - 400)
    world = World()
    world.process_data(world_data)

    total_collectibles = len(world.collectible_list)

    # empty world data list
    world_data = []

    # create empty tile list
    for row in range(rows):
      r = [0] * cols
      world_data.append(r)

    # load in new level data and create world
    with open(f'level{level}_data.csv', newline='') as csvfile:
      reader = csv.reader(csvfile, delimiter=",")
      for x, row in enumerate(reader):
        for y, tile in enumerate(row):
          world_data[x][y] = int(tile)
    
    world.process_data(world_data)

    oneup_played = False
    
    # cut player movement
    moving_left = False
    moving_right = False
    frame = 0
    action = 0

    # triggers
    new_level_pause = True
    reset_level = False

    reset_transition_timer = None

  # time += 0.05
  # if start_game == False:
  #   screen_shader.send("time", [time])
  # else:
  #   screen_shader.send("time", [1])

  frame_tex = surf_to_texture(screen)
  frame_tex.use(0)
  program['tex'] = 0

  # print comments here

  if not start_game:
    program['r_value'] = 1
    program['g_value'] = 1
    program['b_value'] = 1
  elif player.fallen:
    if player.fallen_start_time is None:
        player.fallen_start_time = pygame.time.get_ticks()
    elapsed_time = pygame.time.get_ticks() - player.fallen_start_time

    progress = elapsed_time / 4000

    program['r_value'] = 1 * (1 - math.sin(progress * math.pi))
    program['g_value'] = 1 * (1 - math.sin(progress * math.pi))
    program['b_value'] = 1 * (1 - math.sin(progress * math.pi))
  elif player.mood == 1:
    if new_level_pause:
      if reset_transition_timer is None:
        reset_transition_timer = pygame.time.get_ticks()

      elapsed_time = pygame.time.get_ticks() - reset_transition_timer

      if elapsed_time < 50:
        program['r_value'] = 0.0
        program['g_value'] = 0.0
        program['b_value'] = 0.0
      else:
        program['r_value'] = 1
        program['g_value'] = 1
        program['b_value'] = 1
    else:
      program['r_value'] = 0.7
      program['g_value'] = 0.7
      program['b_value'] = 0.8
  elif player.mood == 2:
    program['r_value'] = 0.8
    program['g_value'] = 0.4
    program['b_value'] = 0.3
  elif player.mood == 3:
    program['r_value'] = 0.5
    program['g_value'] = 0.5
    program['b_value'] = 0.4
  elif player.mood == 4:
    program['r_value'] = 1
    program['g_value'] = 1
    program['b_value'] = 1
  
  # if player.fallen:
    # program['r_value'] = 0.6
    # program['g_value'] = 0.6
    # program['b_value'] = 0.6

  render_object.render(mode=moderngl.TRIANGLE_STRIP)

  pygame.display.flip()

  frame_tex.release()

  clock.tick(fps)

pygame.quit()
