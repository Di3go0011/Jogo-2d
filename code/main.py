import pygame
import random
import os
from pygame import mixer
from spritesheet import SpriteSheet
from enemy import Enemy

pygame.init

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
        
        # screen limite for player
        if self.rect.left + dx < 0:
            dx = self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right
            
        # check collosion with plataforms
        for platform in platform_group:
            # collosion in y direction
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if above platform
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20
                        jump_fx.play()
                        
        # check if player has bounced to the top of the screen
        if self.rect.top <= SCROLL_THRESH:
            # if player is jumping
            if self.vel_y < 0:
                scroll = -dy
                
        # update rect position
        self.rect.x += dx
        self.rect.y += dy + scroll
        
        # update mask
        self.mask = pygame.mask.from_surface(self.image)
    
        return scroll
    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 12, self.rect.y - 5)) 
        
# platform class
class platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 10))
        self.moving = moving
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def update(self, scroll):
        # moving platform side to side
        if self.moving == True:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed
            
        # change platform direction if it has moved fully or hit a wall
        if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1
            self.move_counter = 0
            
        # update vertical position
        self.rect.y += scroll
        
        # check if platform has gone off the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
            
# Player instance
jumpy = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

# create sprite groups
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# create starting platforms
platform = platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
platform_group.add(platform)

# game loop

run = True
while run:
    
    clock.tick(FPS)
    
    if game_over == False:
        scroll = jumpy.move()
        
        # draw bg
        bg_scroll += scroll
        if bg_scroll >= 600:
            bg_scroll = 0
        draw_bg(bg_scroll)
        
        # generate platform
        if len(platform_group) < MAX_PLATFORMS:
            p_w = random.randint(40,60)
            p_x = random.randint(0, SCREEN_WIDTH - p_w)
            p_y = platform.rect.y - random.randint(1, 2)
            p_type = random.randint(1, 2)
            if p_type == 1 and score > 1000:
                p_moving = True
            else:
                p_moving = False
            platform = platform(p_x, p_y, p_w, p_moving)
            platform_group.add(platform)
            
        # update platform
        platform_group.update(scroll)
        
        # generate enemies 
        if len(enemy_group) == 0 and score > 2000:
            enemy = Enemy(SCREEN_WIDTH, 100, bird_sheet, 1.5)
            enemy_group.add(enemy)
            
        # update enemies
        enemy_group.update(scroll, SCREEN_WIDTH)
        
        # update score
        if scroll > 0:
            score += scroll
            
        # draw
        pygame.draw.line()
        
        
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