import pygame
import sys
import random
import os
from pygame import mixer

# --- CONSTANTS ---
WIN_WIDTH = 400
WIN_HEIGHT = 600
GRAVITY = 1
FPS = 60
SCROLL_THRESH = 200
MENU_OPTION = ["INICIAR PARTIDA", "HIGH SCORE", "TUTORIAL", "SAIR", "funções menu: ↑ e ↓ + enter"]

# Colors
C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)
C_RED = (255, 0, 0)
C_AZUL_CLARO = (173, 216, 230)
C_DARK_BLUE = (30, 30, 60)
C_BRIGHT_YELLOW = (255, 255, 100)
C_ORANGE = (255, 165, 0)
C_YELLOW = (255, 255, 0)
C_OUTLINE = (0, 0, 0)

# --- INICIALIZATION ---
pygame.init()
mixer.init()
tela = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("JUMPING HIGH")
clock = pygame.time.Clock()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- AUXILIARY FUNCTIONS ---

def get_asset_path(filename):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = BASE_DIR
    path = os.path.join(base_path, "assets", filename)
    if not os.path.exists(path):
        print(f"Aviso: arquivo {filename} não encontrado em {path}")
    return path

def load_bg(filename, fallback_color, win_width, win_height):
    """
    Carrega uma imagem de background, redimensiona para o tamanho da tela.
    Se não encontrar o arquivo, cria uma surface de fallback com cor sólida.
    """
    path = get_asset_path(filename)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert()
            return pygame.transform.scale(img, (win_width, win_height))
        except Exception as e:
            print(f"Erro ao carregar imagem {filename}: {e}")
    surf = pygame.Surface((win_width, win_height))
    surf.fill(fallback_color)
    return surf

class MockSound:
    """Classe usada quando o arquivo de som não é encontrado"""
    play = staticmethod(lambda *a, **k: None)
    set_volume = staticmethod(lambda *a, **k: None)

def load_sound(filename, volume=1.0):
    """
    Carrega um arquivo de som. Retorna MockSound se não encontrar o arquivo.
    """
    path = get_asset_path(filename)
    if os.path.exists(path):
        try:
            s = mixer.Sound(path)
            s.set_volume(volume)
            return s
        except Exception as e:
            print(f"Erro ao carregar som {filename}: {e}")
    else:
        print(f"Aviso: arquivo de som {filename} não encontrado.")
    return MockSound()

def draw_text_styled(screen, text, font, text_col, x, y, centered=False, outline_col=C_OUTLINE):
    shadow_offset = 2
    shadow = font.render(text, True, outline_col)
    text_surface = font.render(text, True, text_col)
    if centered:
        screen.blit(shadow, shadow.get_rect(center=(x + shadow_offset, y + shadow_offset)))
        screen.blit(text_surface, text_surface.get_rect(center=(x, y)))
    else:
        screen.blit(shadow, (x + shadow_offset, y + shadow_offset))
        screen.blit(text_surface, (x, y))

def load_spritesheet(filename, frame_width, frame_height, scale=1.0):
    try:
        sheet = pygame.image.load(get_asset_path(filename)).convert_alpha()
    except:
        placeholder = pygame.Surface((int(frame_width*scale), int(frame_height*scale)), pygame.SRCALPHA)
        placeholder.fill(C_RED)
        return [placeholder]
    sheet_width = sheet.get_width()
    frames = []
    if sheet_width < frame_width:
        frame = pygame.transform.scale(sheet, (int(frame_width*scale), int(frame_height*scale)))
        frames.append(frame)
    else:
        num_frames = sheet_width // frame_width
        for i in range(num_frames):
            frame = sheet.subsurface((i*frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (int(frame_width*scale), int(frame_height*scale)))
            frames.append(frame)
    return frames

def load_sound(filename, volume=1.0):
    try:
        s = mixer.Sound(get_asset_path(filename))
        s.set_volume(volume)
        return s
    except:
        print(f"Aviso: não foi possível carregar {filename}")
        return MockSound()

# --- PLAYER ---
class Player(pygame.sprite.Sprite):
    SCALE = 1.5
    FRAME_WIDTH = 30
    FRAME_HEIGHT = 48
    ANIMATION_SPEED = 5
    def __init__(self, x, y):
        super().__init__()
        self.images_right = load_spritesheet('jumpy_right.png', self.FRAME_WIDTH, self.FRAME_HEIGHT, self.SCALE)
        self.images_left = [pygame.transform.flip(img, True, False) for img in self.images_right]
        self.image = self.images_right[0]
        self.rect = pygame.Rect(0,0,int(self.FRAME_WIDTH*self.SCALE*0.7),int(self.FRAME_HEIGHT*self.SCALE*0.9))
        self.rect.center = (x,y)
        self.vel_y = 0
        self.is_moving_x = False
        self.current_direction = 'R'
        self.last_direction = self.current_direction
        self.frame_index = 0
        self.update_tick = 0

    def move(self, platform_group, jump_fx):
        scroll = dx = dy = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_a]: dx = -10; self.current_direction='L'
        if key[pygame.K_d]: dx = 10; self.current_direction='R'
        self.is_moving_x = (dx != 0)
        self.vel_y += GRAVITY
        dy += self.vel_y
        self.rect.x = (self.rect.x + dx) % WIN_WIDTH
        for platform in platform_group:
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.rect.bottom < platform.rect.centery and self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    dy = 0
                    self.vel_y = -20
                    jump_fx.play()
        if self.rect.top <= SCROLL_THRESH and self.vel_y < 0:
            scroll = -dy
        self.rect.y += dy + scroll
        return scroll

    def update_animation(self):
        animation_list = self.images_right if self.current_direction=='R' else self.images_left
        if self.last_direction != self.current_direction:
            self.frame_index = 0
            self.update_tick = 0
            self.last_direction = self.current_direction
        self.update_tick += 1
        if self.update_tick >= self.ANIMATION_SPEED:
            self.update_tick = 0
            self.frame_index = (self.frame_index + 1) % len(animation_list)
        self.image = animation_list[self.frame_index]

    def draw(self, screen):
        self.update_animation()
        screen.blit(self.image,(self.rect.x-(self.image.get_width()-self.rect.width)//2, self.rect.y-(self.image.get_height()-self.rect.height)//2))

# --- PLATFORM ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving, platform_image):
        super().__init__()
        scale_height = int(platform_image.get_height() * (width / platform_image.get_width()))
        self.image = pygame.transform.scale(platform_image, (width, scale_height))
        self.moving = moving
        self.direction = random.choice([-1,1])
        self.speed = random.randint(1,2)
        self.move_counter = random.randint(0,50)
        self.rect = self.image.get_rect(topleft=(x,y))
    def update(self, scroll):
        if self.moving:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed
            if self.move_counter >= 100 or self.rect.left<0 or self.rect.right>WIN_WIDTH:
                self.direction *= -1
                self.move_counter = 0
        self.rect.y += scroll
        if self.rect.top>WIN_HEIGHT: self.kill()

# --- MENU ---
class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("Lucida Sans", 50, bold=True)
        self.font_options = pygame.font.SysFont("Lucida Sans", 24, bold=True)
        self.font_tutorial = pygame.font.SysFont("Lucida Sans", 20, bold=True)
        self.bg = load_bg("bg.png", C_DARK_BLUE, WIN_WIDTH, WIN_HEIGHT)
        # SOUNDS
        self.menu_music = load_sound("music.mp3", 0.3)
        self.sound_move = load_sound("select.mp3", 0.5)
        self.sound_select = load_sound("select.mp3", 0.7)

    def play_sound(self, sound):
        if sound: sound.play()

    def play_menu_music(self):
        try:
            mixer.music.load(get_asset_path("music.mp3"))
            mixer.music.set_volume(0.3)
            mixer.music.play(-1)
        except:
            pass

    def show_tutorial(self):
        running = True
        while running:
            self.screen.fill(C_DARK_BLUE)
            draw_text_styled(self.screen, "TUTORIAL", self.font_title, C_ORANGE, WIN_WIDTH//2, 80, True)
            draw_text_styled(self.screen, "Use A e D para mover o jogador", self.font_tutorial, C_WHITE, WIN_WIDTH//2, 200, True)
            draw_text_styled(self.screen, "Evite cair e suba nas plataformas", self.font_tutorial, C_WHITE, WIN_WIDTH//2, 230, True)
            draw_text_styled(self.screen, "Use ↑ e ↓ para navegar no menu", self.font_tutorial, C_WHITE, WIN_WIDTH//2, 260, True)
            draw_text_styled(self.screen, "Pressione ESC para voltar ao menu", self.font_tutorial, C_YELLOW, WIN_WIDTH//2, 400, True)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_RETURN]:
                        running = False

    def run(self):
        self.play_menu_music()
        menu_option = 0
        while True:
            self.clock.tick(30)
            self.screen.blit(self.bg,(0,0))
            draw_text_styled(self.screen,"Jumping",self.font_title,C_ORANGE,WIN_WIDTH//2,70,True)
            draw_text_styled(self.screen,"High",self.font_title,C_ORANGE,WIN_WIDTH//2,120,True)
            for i,opt in enumerate(MENU_OPTION):
                color = C_YELLOW if i==menu_option else C_WHITE
                draw_text_styled(self.screen,opt,self.font_options,color,WIN_WIDTH//2,200+35*i,True)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type==pygame.QUIT: pygame.quit(); sys.exit()
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_DOWN: menu_option = (menu_option + 1) % len(MENU_OPTION); self.play_sound(self.sound_move)
                    elif event.key==pygame.K_UP: menu_option = (menu_option - 1) % len(MENU_OPTION); self.play_sound(self.sound_move)
                    elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE]:
                        self.play_sound(self.sound_select)
                        if MENU_OPTION[menu_option]=="INICIAR PARTIDA":
                            mixer.music.stop(); return 'game'
                        elif MENU_OPTION[menu_option]=="HIGH SCORE":
                            return 'high_score'
                        elif MENU_OPTION[menu_option]=="TUTORIAL":
                            self.show_tutorial(); self.play_menu_music()
                        elif MENU_OPTION[menu_option]=="SAIR":
                            pygame.quit(); sys.exit()

# --- GAME ---
class Game:
    def __init__(self, screen, high_score_ref):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.scroll = self.score = 0
        self.game_over = False
        self.victory = False
        self.high_score_ref = high_score_ref
        self.music_playing = False

        # BG
        self.bg_day = load_bg("bg_day_sky.png", C_AZUL_CLARO, WIN_WIDTH, WIN_HEIGHT)
        self.bg_night = load_bg("bg_night_sky.png", C_DARK_BLUE, WIN_WIDTH, WIN_HEIGHT)
        try:
            self.bg_clouds = pygame.image.load(get_asset_path("bg_clouds.png")).convert_alpha()
        except:
            self.bg_clouds = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
            self.bg_clouds.fill((255,255,255,0))
        self.bg_clouds = pygame.transform.scale(self.bg_clouds,(WIN_WIDTH,WIN_HEIGHT))
        self.cloud_x = 0
        self.cloud_speed = 0.3

        try:
            moon_img_raw = pygame.image.load(get_asset_path("bg_moon.png")).convert_alpha()
        except:
            moon_img_raw = pygame.Surface((100,100),pygame.SRCALPHA)
            pygame.draw.circle(moon_img_raw,C_BRIGHT_YELLOW,(50,50),50)
        self.moon = pygame.transform.scale(moon_img_raw,(80,80))

        # PLAYER
        self.jumpy = Player(WIN_WIDTH//2, WIN_HEIGHT-150)

        # PLATFORM
        try:
            self.platform_image = pygame.image.load(get_asset_path("platform.png")).convert_alpha()
        except:
            self.platform_image = pygame.Surface((100,40))
            self.platform_image.fill((0,200,0))

        # SOUNDS
        try:
            self.jump_fx = mixer.Sound(get_asset_path("jump.mp3"))
            self.jump_fx.set_volume(0.2)
        except: self.jump_fx = MockSound()
        try:
            self.death_fx = mixer.Sound(get_asset_path("death.mp3"))
        except: self.death_fx = MockSound()
        try:
            music_path = get_asset_path("music1.mp3")
            if os.path.exists(music_path):
                self.music_path = music_path
        except:
            self.music_path = None

        self.platform_group = pygame.sprite.Group()
        self.create_platforms()
        self.font_small = pygame.font.SysFont("Arial",18,bold=True)
        self.font_big = pygame.font.SysFont("Arial",28,bold=True)

    def create_platforms(self):
        self.platform_group.empty()
        base = Platform(WIN_WIDTH//2-50, WIN_HEIGHT-50, 100, False, self.platform_image)
        self.platform_group.add(base)
        for i in range(5):
            p_w = random.randint(90, 120)
            p_x = random.randint(0, WIN_WIDTH-p_w)
            p_y = WIN_HEIGHT-150-(i*100)
            moving = random.choice([True, False])
            self.platform_group.add(Platform(p_x,p_y,p_w,moving,self.platform_image))

    def draw_bg(self):
        is_night = self.score>=2000
        sky = self.bg_night if is_night else self.bg_day
        self.screen.blit(sky,(0,0))
        if not is_night:
            self.cloud_x -= self.cloud_speed
            if self.cloud_x <= -WIN_WIDTH:
                self.cloud_x = 0
            self.screen.blit(self.bg_clouds,(self.cloud_x,0))
            self.screen.blit(self.bg_clouds,(self.cloud_x + WIN_WIDTH,0))
        else:
            self.screen.blit(self.moon,(WIN_WIDTH-100,20))

    def draw_panel(self):
        draw_text_styled(self.screen, f"SCORE: {self.score}", self.font_small, C_WHITE, 10, 10)

    def reset_game(self):
        self.scroll = self.score = 0
        self.game_over = False
        self.victory = False
        self.jumpy.rect.center = (WIN_WIDTH//2, WIN_HEIGHT-150)
        self.jumpy.vel_y = 0
        self.create_platforms()
        if self.music_path:
            mixer.music.load(self.music_path)
            mixer.music.set_volume(0.5)
            mixer.music.play(-1)
            self.music_playing = True

    def run(self):
        self.reset_game()
        while True:
            self.clock.tick(FPS)
            if not self.game_over and not self.victory:
                self.scroll = self.jumpy.move(self.platform_group,self.jump_fx)
                self.draw_bg()
                self.platform_group.update(self.scroll)
                self.platform_group.draw(self.screen)
                if len(self.platform_group) < 6:
                    p_w = random.randint(90, 120)
                    p_x = random.randint(0, WIN_WIDTH-p_w)
                    if self.platform_group.sprites():
                        highest = min(p.rect.top for p in self.platform_group)
                        p_y = highest - random.randint(70, 120)
                    else:
                        p_y = WIN_HEIGHT - random.randint(150,200)
                    moving = random.choice([True, False])
                    self.platform_group.add(Platform(p_x,p_y,p_w,moving,self.platform_image))
                self.jumpy.draw(self.screen)
                if self.scroll>0: self.score += int(self.scroll*0.5)
                self.draw_panel()
                if self.score>=4000:
                    self.victory=True
                    if self.music_playing: mixer.music.stop(); self.music_playing=False
                if self.jumpy.rect.top>WIN_HEIGHT:
                    self.game_over=True
                    self.death_fx.play()
                    if self.music_playing: mixer.music.stop(); self.music_playing=False
            else:
                if self.score > self.high_score_ref[0]:
                    self.high_score_ref[0] = self.score
                if self.victory:
                    draw_text_styled(self.screen,"PARABÉNS!",self.font_big,C_ORANGE,WIN_WIDTH//2,WIN_HEIGHT//2-50,True)
                    draw_text_styled(self.screen,f"SCORE: {self.score}",self.font_big,C_WHITE,WIN_WIDTH//2,WIN_HEIGHT//2,True)
                    draw_text_styled(self.screen,"R - JOGAR NOVAMENTE",self.font_small,C_YELLOW,WIN_WIDTH//2,WIN_HEIGHT//2+50,True)
                    draw_text_styled(self.screen,"ESC - VOLTAR AO MENU",self.font_small,C_YELLOW,WIN_WIDTH//2,WIN_HEIGHT//2+80,True)
                else:
                    draw_text_styled(self.screen,"GAME OVER",self.font_big,C_RED,WIN_WIDTH//2,WIN_HEIGHT//2,True)
                    draw_text_styled(self.screen,"ESC - VOLTAR AO MENU",self.font_small,C_WHITE,WIN_WIDTH//2,WIN_HEIGHT//2+50,True)
            for event in pygame.event.get():
                if event.type==pygame.QUIT: pygame.quit(); sys.exit()
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE:
                        if self.music_playing: mixer.music.stop(); self.music_playing=False
                        return 'menu'
                    if self.victory and event.key==pygame.K_r:
                        self.reset_game()
                        self.victory=False
            pygame.display.update()

# --- HIGH SCORE ---
class HighScoreScreen:
    def __init__(self, screen, high_score_ref):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.high_score_ref = high_score_ref
        self.font_header = pygame.font.SysFont("Arial",37,bold=True)
        self.font_score = pygame.font.SysFont("Arial",30,bold=True)
        self.bg = load_bg("bg.png",C_DARK_BLUE,WIN_WIDTH,WIN_HEIGHT)

    def run(self):
        while True:
            self.clock.tick(30)
            self.screen.blit(self.bg,(0,0))
            score_text = str(self.high_score_ref[0])
            score_surf = self.font_score.render(score_text, True, C_WHITE)
            rect_bg = score_surf.get_rect(center=(WIN_WIDTH//2,250))
            rect_bg.inflate_ip(20,10)
            pygame.draw.rect(self.screen,(0,0,0),rect_bg)
            draw_text_styled(self.screen,"HIGH SCORE",self.font_header,C_BRIGHT_YELLOW,WIN_WIDTH//2,100,True)
            draw_text_styled(self.screen,score_text,self.font_score,C_WHITE,WIN_WIDTH//2,250,True)
            draw_text_styled(self.screen,"ESC - VOLTAR AO MENU",self.font_score,C_YELLOW,WIN_WIDTH//2,400,True)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type==pygame.QUIT: pygame.quit(); sys.exit()
                if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                    return "menu"

# --- MAIN LOOP ---
def main():
    high_score_ref = [0]
    state = "menu"
    menu = Menu(tela)
    game = Game(tela,high_score_ref)
    hs_screen = HighScoreScreen(tela,high_score_ref)
    while True:
        if state=="menu": state = menu.run()
        elif state=="game": state = game.run()
        elif state=="high_score": state = hs_screen.run()
        elif state=="quit": pygame.quit(); sys.exit()

if __name__=="__main__":
    main()
