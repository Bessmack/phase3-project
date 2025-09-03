#!/usr/bin/env python3
"""
Space Shooter with 3 distinct modes (Easy, Medium, Hard)
- Enhanced with images, sounds, and moving backgrounds
- Pygame launcher with 3 big buttons to start each mode
- Tkinter scoreboard with CRUD functionality
- SQLite database (scores.db) for score storage

Run:
    python main.py

Dependencies:
    pip install pygame

Assets:
    Place in a 'media/' folder relative to this script:
    - Images: player.png, enemy_circle.png, enemy_triangle.png, enemy_asteroid.png,
              bg_easy.png, bg_medium.png, bg_hard.png
    - Sounds: shoot.wav, hit.wav, explode.wav, game.mp3

Tested with Python 3.10+
"""

import os
import sys
import math
import random
import time
import sqlite3
from datetime import datetime
import pygame

# Constants
WIDTH, HEIGHT = 900, 650
FPS = 60
DB_FILE = "scores.db"

# --------------------------- Database Layer ---------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player TEXT NOT NULL,
    mode TEXT NOT NULL CHECK(mode in ('Easy','Medium','Hard')),
    score INTEGER NOT NULL,
    duration_sec REAL NOT NULL,
    played_at TEXT NOT NULL
);
"""

def db_connect():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def db_init():
    conn = db_connect()
    with conn:
        conn.executescript(SCHEMA)
    conn.close()

def db_add_score(player: str, mode: str, score: int, duration_sec: float, played_at: str | None = None):
    if not played_at:
        played_at = datetime.now().isoformat(timespec='seconds')
    conn = db_connect()
    with conn:
        conn.execute(
            "INSERT INTO scores(player, mode, score, duration_sec, played_at) VALUES (?,?,?,?,?)",
            (player, mode, score, float(duration_sec), played_at),
        )
    conn.close()

def db_get_scores(mode_filter: str | None = None):
    conn = db_connect()
    cur = conn.cursor()
    if mode_filter and mode_filter in ("Easy", "Medium", "Hard"):
        cur.execute("SELECT id, player, mode, score, duration_sec, played_at FROM scores WHERE mode=? ORDER BY score DESC, played_at DESC", (mode_filter,))
    else:
        cur.execute("SELECT id, player, mode, score, duration_sec, played_at FROM scores ORDER BY score DESC, played_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def db_update_score(record_id: int, player: str | None = None, mode: str | None = None, score: int | None = None):
    fields = []
    params = []
    if player is not None:
        fields.append("player=?")
        params.append(player)
    if mode is not None:
        fields.append("mode=?")
        params.append(mode)
    if score is not None:
        fields.append("score=?")
        params.append(int(score))
    if not fields:
        return
    params.append(record_id)
    conn = db_connect()
    with conn:
        conn.execute(f"UPDATE scores SET {', '.join(fields)} WHERE id=?", params)
    conn.close()

def db_delete_score(record_id: int):
    conn = db_connect()
    with conn:
        conn.execute("DELETE FROM scores WHERE id=?", (record_id,))
    conn.close()

# --------------------------- Tkinter UI (Scoreboard & CRUD) -----------------
def open_scoreboard(last_result: dict | None = None):
    import tkinter as tk
    from tkinter import ttk, messagebox

    def refresh_tree():
        for i in tree.get_children():
            tree.delete(i)
        filt = mode_filter_var.get()
        filt = None if filt == "All" else filt
        for rid, player, mode, score, dur, ts in db_get_scores(filt):
            tree.insert("", tk.END, iid=str(rid), values=(rid, player, mode, score, f"{dur:.1f}", ts))

    def on_add():
        try:
            player = entry_player.get().strip() or "Player"
            mode = mode_var.get()
            score = int(entry_score.get())
            if score < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Score must be a non-negative integer.")
            return
        db_add_score(player, mode, score, 0.0)
        refresh_tree()
        entry_player.delete(0, tk.END)
        entry_score.delete(0, tk.END)

    def on_update():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Select a row to update.")
            return
        rid = int(sel[0])
        player = entry_player.get().strip() or None
        mode = mode_var.get() if mode_var.get() in ("Easy", "Medium", "Hard") else None
        score_text = entry_score.get().strip()
        score_val = int(score_text) if score_text else None
        try:
            if score_val is not None and score_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Score must be a non-negative integer.")
            return
        db_update_score(rid, player=player if player else None, mode=mode, score=score_val)
        refresh_tree()

    def on_delete():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Select a row to delete.")
            return
        rid = int(sel[0])
        if messagebox.askyesno("Confirm", f"Delete record #{rid}?"):
            db_delete_score(rid)
            refresh_tree()

    def on_tree_select(event=None):
        sel = tree.selection()
        if not sel:
            return
        rid = int(sel[0])
        vals = tree.item(sel[0], 'values')
        entry_player.delete(0, tk.END)
        entry_player.insert(0, vals[1])
        entry_score.delete(0, tk.END)
        entry_score.insert(0, vals[3])
        mode_var.set(vals[2])

    def launch_from_board(mode_name: str):
        root.destroy()
        run_game(mode_name)

    root = tk.Tk()
    root.title("Space Shooter — Scores & CRUD")
    root.geometry("880x560")

    title = ttk.Label(root, text="Scores & Leaderboard", font=("Arial", 18, "bold"))
    title.pack(pady=8)

    topbar = ttk.Frame(root)
    topbar.pack(fill=tk.X, padx=10)

    ttk.Label(topbar, text="Filter by mode:").pack(side=tk.LEFT)
    mode_filter_var = tk.StringVar(value="All")
    mode_filter = ttk.Combobox(topbar, textvariable=mode_filter_var, values=["All", "Easy", "Medium", "Hard"], width=10, state="readonly")
    mode_filter.pack(side=tk.LEFT, padx=6)
    mode_filter.bind("<<ComboboxSelected>>", lambda e: refresh_tree())

    btns = ttk.Frame(topbar)
    btns.pack(side=tk.RIGHT)
    ttk.Button(btns, text="Start Easy", command=lambda: launch_from_board("Easy")).pack(side=tk.LEFT, padx=4)
    ttk.Button(btns, text="Start Medium", command=lambda: launch_from_board("Medium")).pack(side=tk.LEFT, padx=4)
    ttk.Button(btns, text="Start Hard", command=lambda: launch_from_board("Hard")).pack(side=tk.LEFT, padx=4)

    cols = ("id", "player", "mode", "score", "duration_sec", "played_at")
    tree = ttk.Treeview(root, columns=cols, show="headings", height=16)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor=tk.CENTER, stretch=True, width=100)
    tree.column("player", width=150)
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
    tree.bind("<<TreeviewSelect>>", on_tree_select)

    form = ttk.Frame(root)
    form.pack(fill=tk.X, padx=10, pady=4)

    ttk.Label(form, text="Player:").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
    entry_player = ttk.Entry(form)
    entry_player.grid(row=0, column=1, padx=4, pady=4)

    ttk.Label(form, text="Mode:").grid(row=0, column=2, sticky=tk.W, padx=4, pady=4)
    mode_var = tk.StringVar(value="Easy")
    cmb = ttk.Combobox(form, textvariable=mode_var, values=["Easy", "Medium", "Hard"], state="readonly", width=10)
    cmb.grid(row=0, column=3, padx=4, pady=4)

    ttk.Label(form, text="Score:").grid(row=0, column=4, sticky=tk.W, padx=4, pady=4)
    entry_score = ttk.Entry(form, width=10)
    entry_score.grid(row=0, column=5, padx=4, pady=4)

    actions = ttk.Frame(root)
    actions.pack(pady=6)
    ttk.Button(actions, text="Add", command=on_add).pack(side=tk.LEFT, padx=6)
    ttk.Button(actions, text="Update Selected", command=on_update).pack(side=tk.LEFT, padx=6)
    ttk.Button(actions, text="Delete Selected", command=on_delete).pack(side=tk.LEFT, padx=6)
    ttk.Button(actions, text="Close", command=root.destroy).pack(side=tk.LEFT, padx=6)

    refresh_tree()

    if last_result:
        banner = ttk.Label(root, foreground="#0a0", font=("Arial", 12, "bold"),
                           text=f"Last game — {last_result['mode']} | Player: {last_result['player']} | Score: {last_result['score']} | Duration: {last_result['duration_sec']:.1f}s")
        banner.pack(pady=4)

    root.mainloop()

# --------------------------- Pygame Game ------------------------------------

# Mode configurations with image and sound assets
MODE_CONFIGS = {
    "Easy": {
        "player_speed": 6,
        "bullet_speed": -10,
        "enemy_speed": 2,
        "spawn_rate": 30,
        "bg_image": "media/bg_easy.png",
        "music": "media/game.mp3",
        "enemy_shape": "circle",
        "palette": {
            "bullet": (255, 255, 255),
        },
    },
    "Medium": {
        "player_speed": 7,
        "bullet_speed": -12,
        "enemy_speed": 3,
        "spawn_rate": 24,
        "bg_image": "media/bg_medium.png",
        "music": "media/game.mp3",
        "enemy_shape": "triangle",
        "palette": {
            "bullet": (200, 255, 200),
        },
    },
    "Hard": {
        "player_speed": 8,
        "bullet_speed": -14,
        "enemy_speed": 4,
        "spawn_rate": 18,
        "bg_image": "media/bg_hard.png",
        "music": "media/game.mp3",
        "enemy_shape": "asteroid",
        "palette": {
            "bullet": (255, 200, 255),
        },
    },
}

# Asset loading with error handling
def load_assets():
    assets = {
        "player": None,
        "bullet": None,  # Add bullet image
        "enemies": {
            "circle": None,
            "triangle": None,
            "asteroid": None,
        },
        "backgrounds": {
            "Easy": None,
            "Medium": None,
            "Hard": None,
        },
        "sounds": {
            "shoot": None,
            "hit": None,
            "explode": None,
        },
        "music": {
            "Easy": MODE_CONFIGS["Easy"]["music"],
            "Medium": MODE_CONFIGS["Medium"]["music"],
            "Hard": MODE_CONFIGS["Hard"]["music"],
        },
    }
    
    try:
        # Load player image
        assets["player"] = pygame.image.load("media/player.png").convert_alpha()
        assets["player"] = pygame.transform.scale(assets["player"], (80, 60))
        
        # Load bullet image
        assets["bullet"] = pygame.image.load("media/bullet.png").convert_alpha()
        assets["bullet"] = pygame.transform.scale(assets["bullet"], (24, 48))
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading player/bullet images: {e}")
    
    # Load enemy images
    for shape in assets["enemies"]:
        try:
            img = pygame.image.load(f"media/enemy_{shape}.png").convert_alpha()
            assets["enemies"][shape] = pygame.transform.scale(img, (50, 50))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading enemy image {shape}: {e}")
    
    # Load backgrounds
    for mode in assets["backgrounds"]:
        try:
            bg = pygame.image.load(MODE_CONFIGS[mode]["bg_image"]).convert()
            assets["backgrounds"][mode] = pygame.transform.scale(bg, (WIDTH * 2, HEIGHT))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading background for {mode}: {e}")
    
    # Load sounds
    try:
        assets["sounds"]["shoot"] = pygame.mixer.Sound("media/shoot.wav")
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading shoot sound: {e}")
    
    try:
        assets["sounds"]["hit"] = pygame.mixer.Sound("media/hit.wav")
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading hit sound: {e}")
    
    try:
        assets["sounds"]["explode"] = pygame.mixer.Sound("media/explode.wav")
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading explode sound: {e}")
        
    return assets

def draw_background(screen, mode_cfg, assets, frame):
    bg = assets["backgrounds"][mode_cfg["mode"]]
    if bg:
        bg_x = -(frame % WIDTH)
        screen.blit(bg, (bg_x, 0))
        screen.blit(bg, (bg_x + WIDTH, 0))
    else:
        # Fallback if background failed to load
        screen.fill((10, 10, 40))

def spawn_enemy(mode_cfg):
    x = random.randint(20, WIDTH - 20)
    y = -30
    speed = mode_cfg["enemy_speed"]
    shape = mode_cfg["enemy_shape"]
    size = 18
    return {"x": x, "y": y, "speed": speed, "shape": shape, "size": size}

def enemy_rect(enemy):
    size = enemy["size"]
    return pygame.Rect(enemy["x"] - size, enemy["y"] - size, size * 2, size * 2)

def run_game(mode_name: str = "Easy"):
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
                    # Create bullet with dimensions matching your image
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
            pygame.draw.rect(screen, (0, 255, 0), player)  # Fallback player
        
        for b in bullets:
            if assets["bullet"]:
                screen.blit(assets["bullet"], (b.x, b.y))
            else:
                # Fallback if bullet image failed to load
                pygame.draw.rect(screen, cfg["palette"]["bullet"], b)
        
        for e in enemies:
            if assets["enemies"][e["shape"]]:
                screen.blit(assets["enemies"][e["shape"]], (e["x"] - e["size"], e["y"] - e["size"]))
            else:
                # Fallback enemy drawing
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

def game_over(screen, bigfont, score):
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

def launcher_menu(screen, clock, bigfont):
    running = True
    frame = 0
    buttons = []  # Define buttons list here
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for label, rect in buttons:
                    if rect.collidepoint(mx, my):
                        return label

        screen.fill((6, 6, 20))
        for i in range(70):
            x = (i * 31 + frame * 2) % WIDTH
            y = (i * 13 + int(math.sin((frame + i) * 0.05) * 50)) % HEIGHT
            pygame.draw.circle(screen, (200, 200, 255), (x, y), 2)

        title = bigfont.render("SPACE SHOOTER", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        bw, bh = 240, 70
        by = 220
        gap = 20
        labels = ["Easy", "Medium", "Hard"]
        buttons = []  # Reinitialize each frame
        for idx, lbl in enumerate(labels):
            rect = pygame.Rect(WIDTH // 2 - bw // 2, by + idx * (bh + gap), bw, bh)
            buttons.append((lbl, rect))
            color = (40, 140, 255) if idx == 0 else (80, 200, 120) if idx == 1 else (220, 80, 220)
            pygame.draw.rect(screen, color, rect, border_radius=16)
            txt = bigfont.render(lbl, True, (15, 15, 25))
            screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        footer = pygame.font.SysFont("arial", 18).render(
            "Click a mode to start. After the game, a Tkinter scoreboard opens.",
            True, (210, 210, 210)
        )
        screen.blit(footer, (WIDTH // 2 - footer.get_width() // 2, HEIGHT - 60))

        pygame.display.flip()
        clock.tick(60)
        frame += 1

def main():
    db_init()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Shooter — Choose Mode")
    clock = pygame.time.Clock()
    bigfont = pygame.font.SysFont("arial", 36, bold=True)

    chosen = launcher_menu(screen, clock, bigfont)
    pygame.display.quit()
    run_game(chosen)

if __name__ == "__main__":
    main()
