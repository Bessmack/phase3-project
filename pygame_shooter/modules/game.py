"""
Game logic and rendering
"""
import pygame
import math
import random
import time
import os
import sys
from datetime import datetime
from modules.config import WIDTH, HEIGHT, FPS, MODE_CONFIGS
from modules.assets import load_assets
from modules.database import db_add_score
from modules.ui import open_scoreboard

def draw_background(screen, mode_cfg, assets, frame):
    """Draw the scrolling background"""
    bg = assets["backgrounds"][mode_cfg["mode"]]
    if bg:
        bg_x = -(frame % WIDTH)
        screen.blit(bg, (bg_x, 0))
        screen.blit(bg, (bg_x + WIDTH, 0))
    else:
        screen.fill((10, 10, 40))

def spawn_enemy(mode_cfg):
    """Create a new enemy with random position"""
    x = random.randint(20, WIDTH - 20)
    y = -30
    speed = mode_cfg["enemy_speed"]
    shape = mode_cfg["enemy_shape"]
    size = 18
    return {"x": x, "y": y, "speed": speed, "shape": shape, "size": size}

def enemy_rect(enemy):
    """Get the pygame Rect for an enemy"""
    size = enemy["size"]
    return pygame.Rect(enemy["x"] - size, enemy["y"] - size, size * 2, size * 2)

def game_over(screen, bigfont, score):
    """Display game over screen"""
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    msg1 = bigfont.render("GAME OVER", True, (255, 60, 60))
    msg2 = bigfont.render(f"Score: {score}", True, (220, 220, 220))
    msg3 = bigfont.render("Press any key to continue", True, (180, 180, 180))
    screen.blit(msg1, (WIDTH // 2 - msg1.get_width() // 2, HEIGHT // 2 - 90))
    screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2 - 40))
    screen.blit(msg3, (WIDTH // 2 - msg3.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

def run_game(mode_name: str = "Easy"):
    """Run the main game loop"""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Space Shooter — {mode_name}")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20)
    bigfont = pygame.font.SysFont("arial", 36, bold=True)

    if mode_name not in MODE_CONFIGS:
        mode_name = "Easy"

    cfg = MODE_CONFIGS[mode_name]
    cfg["mode"] = mode_name
    assets = load_assets()

    try:
        pygame.mixer.music.load(assets["music"][mode_name])
        pygame.mixer.music.play(-1)
    except:
        print("Could not load music")

    player = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 70, 50, 40)
    player_speed = cfg["player_speed"]
    bullets = []
    enemies = []
    score = 0
    lives = 3 if mode_name != "Hard" else 2
    frame = 0
    last_shot = 0
    start_time = time.time()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                now = frame
                if now - last_shot > 10:
                    bullets.append(pygame.Rect(player.centerx - 3, player.top - 12, 6, 12))
                    last_shot = now
                    if assets["sounds"]["shoot"]:
                        assets["sounds"]["shoot"].play()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player.x += player_speed
        player.x = max(10, min(WIDTH - player.width - 10, player.x))

        if frame % cfg["spawn_rate"] == 0:
            enemies.append(spawn_enemy(cfg))

        for b in bullets:
            b.y += cfg["bullet_speed"]
        bullets = [b for b in bullets if b.bottom > 0]

        for e in enemies:
            e["y"] += e["speed"]
            if cfg["enemy_shape"] in ("triangle", "asteroid"):
                e["x"] += math.sin((frame + e["y"]) * 0.03) * (1 if cfg["enemy_shape"] == "triangle" else 2)
        enemies = [e for e in enemies if e["y"] - e["size"] < HEIGHT]

        to_remove_b = []
        to_remove_e = []
        for i, e in enumerate(enemies):
            er = enemy_rect(e)
            for j, b in enumerate(bullets):
                if er.colliderect(b):
                    to_remove_b.append(j)
                    to_remove_e.append(i)
                    score += 10
                    if assets["sounds"]["explode"]:
                        assets["sounds"]["explode"].play()
                    break
            if er.colliderect(player):
                to_remove_e.append(i)
                lives -= 1
                if assets["sounds"]["hit"]:
                    assets["sounds"]["hit"].play()
                if lives <= 0:
                    running = False
                    break
        to_remove_b = sorted(set(to_remove_b), reverse=True)
        to_remove_e = sorted(set(to_remove_e), reverse=True)
        for idx in to_remove_b:
            if 0 <= idx < len(bullets):
                bullets.pop(idx)
        for idx in to_remove_e:
            if 0 <= idx < len(enemies):
                enemies.pop(idx)

        frame += 1
        draw_background(screen, cfg, assets, frame)

        if assets["player"]:
            screen.blit(assets["player"], (player.x, player.y))
        else:
            pygame.draw.rect(screen, (0, 255, 0), player)
        
        for b in bullets:
            if assets["bullet"]:
                screen.blit(assets["bullet"], (b.x, b.y))
            else:
                pygame.draw.rect(screen, cfg["palette"]["bullet"], b)
        
        for e in enemies:
            if assets["enemies"][e["shape"]]:
                screen.blit(assets["enemies"][e["shape"]], (e["x"] - e["size"], e["y"] - e["size"]))
            else:
                pygame.draw.circle(screen, (255, 0, 0), (int(e["x"]), int(e["y"])), e["size"])

        hud = font.render(f"Mode: {mode_name}   Score: {score}   Lives: {lives}", True, (240, 240, 240))
        screen.blit(hud, (14, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.mixer.music.stop()
    duration = time.time() - start_time
    game_over(screen, bigfont, score)
    pygame.display.quit()

    player_name = os.getenv("USER") or os.getenv("USERNAME") or "Player"
    db_add_score(player_name, mode_name, score, duration)

    open_scoreboard({
        "player": player_name,
        "mode": mode_name,
        "score": score,
        "duration_sec": duration,
        "played_at": datetime.now().isoformat(timespec='seconds'),
    })
