import pygame
import random

class SpaceInvadersGame:
    WIDTH = 900
    HEIGHT = 650
    FPS = 60

    def __init__(self, player_name):
        self.player_name = player_name

        pygame.init()
        pygame.display.set_caption("Space Invaders")
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.player_img = pygame.image.load("media/fighter.png").convert_alpha()
        self.enemy_img = pygame.image.load("media/enemy.png").convert_alpha()
        self.bullet_img = pygame.image.load("media/bullet.png").convert_alpha()

        self.player_img = pygame.transform.scale(self.player_img, (50, 40))
        self.enemy_img = pygame.transform.scale(self.enemy_img, (40, 30))
        self.bullet_img = pygame.transform.scale(self.bullet_img, (6, 12))

        self.player = self.player_img.get_rect(midbottom=(self.WIDTH // 2, self.HEIGHT - 30))
        self.player_speed = 7
        self.bullets = []
        self.bullet_speed = -10
        self.enemies = []
        self.enemy_speed_min = 1
        self.enemy_speed_max = 2
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 1600
        self.enemy_speeds = {}

        self.score = 0
        self.lives = 10
        self.font = pygame.font.SysFont("Arial", 20)
        self.big_font = pygame.font.SysFont("Arial", 36, bold=True)
    
    def spawn(self):
        w, h = 40, 30
        x = random.randint(0, self.WIDTH - w)
        y = -h
        rect = pygame.Rect(x, y, w, h)
        speed = random.randint(self.enemy_speed_min, self.enemy_speed_max)
        self.enemies.append(rect)
        self.enemy_speeds[id(rect)] = speed

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.x -= self.player_speed
        if keys[pygame.K_RIGHT]:
            self.player.x += self.player_speed
        if keys[pygame.K_UP]:
            self.player.y -= self.player_speed
        if keys[pygame.K_DOWN]:
            self.player.y += self.player_speed
        self.player.x = max(0, min(self.player.x, self.WIDTH - self.player.width))
        self.player.y = max(0, min(self.player.y, self.HEIGHT - self.player.height))


    def shoot(self):
        b = pygame.Rect(self.player.centerx - 3, self.player.top - 12, 6, 12)
        self.bullets.append(b)

    def update(self, dt_ms):
        self.enemy_spawn_timer += dt_ms
        if self.enemy_spawn_timer >= self.enemy_spawn_timer:
            self.enemy_spawn_timer = 0
            self.spawn()
        
        for b in self.bullets:
            b.y += self.bullet_speed
        self.bullets = [b for b in self.bullets if b.bottom > 0]

        for e in self.enemies:
            e.y += self.enemy_speeds.get(id(e), 3)
        still = []
        for e in self.enemies:
            if e.top > self.HEIGHT:
                self.lives -= 1
            else:
                still.append(e)
        self.enemies = still

        remaining_enemies = []
        for e in self.enemies:
            hit = False
            for b in list(self.bullets):
                if e.colliderect(b):
                    self.score += 10
                    hit = True
                    self.bullets.remove(b)
                    break
            if not hit:
                remaining_enemies.append(e)
        self.enemies = remaining_enemies

        for e in list(self.enemies):
            if e.colliderect(self.player):
                self.lives -= 1
                self.enemies.remove(e)

        if self.lives <= 0:
            self.running = False

    def draw(self):
        pass

    def run(self):
        pass








