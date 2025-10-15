import pygame
import random
import os
from pygame import mixer
from spritesheet import SpriteSheet
from enemy import Enemy

pygame.init

screen_widht = 400
screen_height = 600

screen = pygame.display.set_mode((screen_widht, screen_height))
pygame.display.set_caption("kkkkkk")
icon = pygame.image.load("jogo 2d/assets/png")
pygame.display.set_icon(icon)

clock = pygame.time.Clock()
FPS = 60

pygame.mixer.music.load("jogo 2d/assets/")
pygame.mixer.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0)
jump_fx = pygame.mixer.Sound("jogo 2d/  ")
jump_fx.set_volume(1)
death_fx = pygame.mixer.Sound("jodo 2d/  ")
death_fx.set_volume(1)

# variables game

SCROLL_THRESH = 200
GRAVITY = 1
MAX_PLATFORMS = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

if os.path.exists("score.txt"):
    with open("score.txt", "r") as file:
        high_score = int(file.read())
else: 
    high_score = 0
    
# colours

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font_small = pygame.font.SysFont("Lucida Sans", 20)
font_big = pygame.font.SysFont("Lucida Sans", 24)

# load imagens
jumpy_image = pygame
bg_image = pygame
platform_image = pygame

# bird spritesheet

bird_sheet_img = pygame
bird_sheet = SpriteSheet(bird_sheet_img)

def draw_text(text, font, text_col, x, y):
    img =- font.render(text, True, text_col)
    screen.blit(img, (x, y))
    
# draw panel info
def draw_panel():
    
    draw_text("score: " + str(score), font_small, WHITE, 0, 0)
    
# function for drawing bg
def draw_bg(bg_scroll):
    screen.blit(bg_image, (0, 0 + bg_scroll))
    screen.blit(bg_image, (0, -600 + bg_scroll))
    
# Player class
class Player():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(jumpy_image, (45, 45))
        self.width = 25
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False
        
    def move(self):
        # reset variable
        scroll = 0
        dx = 0
        dy = 0 
        
        key = pygame.key.get_pressed()
        if key[pygame.k_a]:
            dx = -10
            self.flip = False
        if key[pygame.k_d]:
            dx = 10
            self.flip = True
        # Gravity
        self.vel_y += GRAVITY
        dy += self.vel_y
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # update high score
            if score > high_score:
                high_score = score
                with open("score.txt", "w") as file:
                    file.write(str(high_score))
            run = False
    # update display
    pygame.display.update()
    
pygame.quit()