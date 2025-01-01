# imports
import pygame
import button
import csv
import json

# initialization
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1920
screen_height = 1080
lower_margin = 100
side_margin = 300

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('CAPSTONE GAME (change later)')

screen.fill('white')

font1 = pygame.font.Font("fonts/Silkscreen-Regular.ttf", 24)
font2 = pygame.font.Font("fonts/Silkscreen-Regular.ttf", 36)
font3 = pygame.font.Font("fonts/Silkscreen-Regular.ttf", 48)
font4 = pygame.font.Font("fonts/Silkscreen-Regular.ttf", 72)

# level editor variables
rows = 18
max_cols = 100

tile_size = screen.get_height() // rows

level = 0

current_tile = 0

scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 2

sign_id = 0
sign_list = []

# empty world data list
world_data = []

# create empty tile list
for row in range(rows):
  r = [0] * max_cols
  world_data.append(r)

# create ground
# grass
for tile in range(0, max_cols):
  world_data[rows - 4][tile] = 2

for tile in range(0, max_cols):
  world_data[rows - 3][tile] = 7
  world_data[rows - 2][tile] = 7
  world_data[rows - 1][tile] = 7

# brick
# for tile in range(0, max_cols):
#   world_data[rows - 4][tile] = 22

# for tile in range(0, max_cols):
#   world_data[rows - 3][tile] = 25
#   world_data[rows - 2][tile] = 25
#   world_data[rows - 1][tile] = 25

def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

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

grass_tiles = {}
misc_tiles = {}
brick_tiles = {}

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

# assets = {'grass_tiles': grass_tiles, 'misc_tiles': misc_tiles}

# with open('assets.json', 'w') as file:
#   json.dump(assets, file)

# level editor grid
def draw_grid():
  # vertical lines
  for c in range(max_cols + 10):
    pygame.draw.line(screen, "white", (c * tile_size - scroll, 0), (c * tile_size - scroll, screen.get_height()))
  
  # horizontal lines
  for r in range(rows + 1):
    pygame.draw.line(screen, "white", (0, r * tile_size), (screen.get_width() - 300, r * tile_size))

# create buttons
save_img = pygame.image.load('assets/save.png').convert_alpha()
load_img = pygame.image.load('assets/load.png').convert_alpha()

save_button = button.Button(screen.get_width() - 225, screen.get_height() - 100, save_img, 2)
load_button = button.Button(screen.get_width() - 125, screen.get_height() - 100, load_img, 2)

# make a button list
button_list = []
button_col = 0
button_row = 0
for i in range(len(grass_tiles)):
  tile_button = button.Button(screen.get_width() - 300 + (75 * button_col) + 50, 75 * button_row + 50, grass_tiles.get(i + 1), 1)
  button_list.append(tile_button)
  button_col += 1
  if button_col == 3:
    button_row += 1
    button_col = 0

for i in range(len(grass_tiles), len(grass_tiles) + len(misc_tiles)):
  tile_button = button.Button(screen.get_width() - 300 + (75 * button_col) + 50, 75 * button_row + 50, misc_tiles.get(i + 1), 1)
  button_list.append(tile_button)
  button_col += 1
  if button_col == 3:
    button_row += 1
    button_col = 0

brick_lower_index = len(grass_tiles) + len(misc_tiles)
brick_upper_index = len(grass_tiles) + len(misc_tiles) + len(brick_tiles)

for i in range(brick_lower_index, brick_upper_index):
  tile_button = button.Button(screen.get_width() - 300 + (75 * button_col) + 50, 75 * button_row + 50, brick_tiles.get(i + 1), 1)
  button_list.append(tile_button)
  button_col += 1
  if button_col == 3:
    button_row += 1
    button_col = 0

# background
def draw_bg():
  pygame.draw.rect(screen, "#708090", (0, 0, 1920, 1080))

def draw_world():
  for y, row in enumerate(world_data):
    for x, tile in enumerate(row):
      if tile >= 1 and tile <= 18:
        img = pygame.transform.scale(grass_tiles.get(tile), (tile_size, tile_size))
        screen.blit(img, (x * tile_size - scroll, y * tile_size))
      if tile >= 19 and tile <= 20:
        img = pygame.transform.scale(misc_tiles.get(tile), (tile_size, tile_size))
        screen.blit(img, (x * tile_size - scroll, y * tile_size + 10))
      if tile >= 21 and tile <= 28:
        img = pygame.transform.scale(brick_tiles.get(tile), (tile_size, tile_size))
        screen.blit(img, (x * tile_size - scroll, y * tile_size))

# game loop
run = True
while run:
  # events (general actions)
  for event in pygame.event.get():
    
    # quit the game
    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
      run = False
    
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_UP:
        level += 1
      if event.key == pygame.K_DOWN and level > 0:
        level -= 1
      if event.key == pygame.K_LEFT:
        scroll_left = True
      if event.key == pygame.K_RIGHT:
        scroll_right = True
    
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_LEFT:
        scroll_left = False
      if event.key == pygame.K_RIGHT:
        scroll_right = False
  

  # level editor screen
  draw_bg()
  draw_grid()
  draw_world()
  
  # draw tile panel
  pygame.draw.rect(screen, "#7393B3", (screen.get_width() - 300, 0, side_margin, screen.get_height()))
  # pygame.draw.rect(screen, "#7393B3", (0, screen.get_height() - 135, screen.get_width(), 135))

  # save and load data
  if save_button.draw(screen):
    # save level data
    # pickle_out = open(f'level{level}_data', 'wb') # open and write in a python list called level{level}_data
    # pickle.dump(world_data, pickle_out) # dump the values of world_data into the list
    # pickle_out.close() # closes the list

    with open(f'level{level}_data.csv', 'w', newline='') as csvfile:
      writer = csv.writer(csvfile, delimiter=",")
      for row in world_data:
        writer.writerow(row)
        
  if load_button.draw(screen):
    # load in level data
    # reset scroll back to the start of the level
    scroll = 0
    # world_data = [] # empty world_data in case it's being used
    # pickle_in = open(f'level{level}_data', 'rb') # open and read the list created when saved (level{level}_data)
    # world_data = pickle.load(pickle_in) # load in the list

    with open(f'level{level}_data.csv', newline='') as csvfile:
      reader = csv.reader(csvfile, delimiter=",")
      for x, row in enumerate(reader):
        for y, tile in enumerate(row):
          world_data[x][y] = int(tile)

  draw_text(f'Level: {level}', font1, "white", 10, screen.get_height() - 110)
  draw_text('Press UP or DOWN to change level', font1, "white", 10, screen.get_height() - 80)

  # choose a tile
  button_count = 0
  for button_count, button in enumerate(button_list):
    if button.draw(screen):
      current_tile = button_count
  
  # highlight the selected tile
  pygame.draw.rect(screen, "red", button_list[current_tile].rect, 3)

  # scroll
  if scroll_left == True:
    scroll -= 5 * scroll_speed
  if scroll_right == True:
    scroll += 5 * scroll_speed
  
  # add new tiles to the screen
  # get mouse position
  pos = pygame.mouse.get_pos()
  x = (pos[0] + scroll) // tile_size
  y = pos[1] // tile_size

  # check that the coordinates are within the tile area
  if pos[0] < screen.get_width() - 300:
    # update tile value
    if pygame.mouse.get_pressed()[0] == 1:
      if world_data[y][x] != current_tile + 1:
        world_data[y][x] = current_tile + 1
    if pygame.mouse.get_pressed()[2] == 1:
      world_data[y][x] = 0

  clock.tick(fps)
  pygame.display.flip()

pygame.quit()
