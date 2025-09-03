import random
import os
import sqlite3
import random

# --- Optional: Turtle intro (runs briefly, then auto-closes) ---
# We import lazily inside the function so headless setups won't fail on import.

def show_intro_turtle(show: bool = True, duration_sec: float = 2.0):
    if not show:
        return
    try:
        import turtle
        screen = turtle.Screen()
        screen.title("Space Shooter Intro")
        t = turtle.Turtle(visible=False)
        t.penup()
        t.goto(0, 20)
        t.write("SPACE SHOOTER", align="center", font=("Arial", 28, "bold"))
        t.goto(0, -20)
        t.write("Get ready...", align="center", font=("Arial", 16, "normal"))

        # Close after duration
        def _close():
            try:
                screen.bye()
            except Exception:
                pass
        screen.ontimer(_close, int(duration_sec * 1000))
        turtle.mainloop()
    except Exception as e:
        # If turtle can't open (e.g., no display), just skip
        print(f"[Turtle intro skipped] {e}")


# --- SQLite helpers ---
DB_PATH = os.path.join(os.path.dirname(__file__), "game.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT NOT NULL,
            score INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def save_score(player: str, score: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO scores (player, score) VALUES (?, ?)", (player, int(score)))
    conn.commit()
    conn.close()


def get_high_scores(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT player, score, created_at FROM scores ORDER BY score DESC, created_at ASC LIMIT ?",
        (limit,),
    )
    rows = c.fetchall()
    conn.close()
    return rows


# --- Tkinter UI (Menu + Scoreboard) ---
# We build Tkinter in functions that block until dismissed and return values to main flow.

def run_tk_menu_and_return_player():
    import tkinter as tk
    from tkinter import ttk, messagebox

    selected_name = {"value": None}

    def show_scores_window(parent):
        win = tk.Toplevel(parent)
        win.title("High Scores")
        win.geometry("360x340")

        cols = ("Player", "Score", "When")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for p, s, when in get_high_scores(20):
            tree.insert("", tk.END, values=(p, s, when))

        ttk.Button(win, text="Close", command=win.destroy).pack(pady=6)

    root = tk.Tk()
    root.title("Space Shooter — Menu")
    root.geometry("420x300")

    tk.Label(root, text="Welcome to Space Shooter!", font=("Arial", 18, "bold")).pack(pady=10)
    tk.Label(root, text="Enter your player name:").pack(pady=(10, 2))

    name_var = tk.StringVar(value="Player1")
    entry = ttk.Entry(root, textvariable=name_var)
    entry.pack(pady=4)
    entry.focus_set()

    btns = tk.Frame(root)
    btns.pack(pady=16)

    def start_game_click():
        name = name_var.get().strip()
        if not name:
            messagebox.showwarning("Name required", "Please enter a player name.")
            return
        selected_name["value"] = name
        root.destroy()

    ttk.Button(btns, text="Start Game", command=start_game_click).grid(row=0, column=0, padx=6)
    ttk.Button(btns, text="High Scores", command=lambda: show_scores_window(root)).grid(row=0, column=1, padx=6)
    ttk.Button(btns, text="Exit", command=root.destroy).grid(row=0, column=2, padx=6)

    root.mainloop()
    return selected_name["value"]


def show_final_scores_dialog(score: int):
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Game Over — High Scores")
    root.geometry("420x380")

    tk.Label(root, text=f"Your Score: {score}", font=("Arial", 16, "bold")).pack(pady=10)

    cols = ("Player", "Score", "When")
    tree = ttk.Treeview(root, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for p, s, when in get_high_scores(15):
        tree.insert("", tk.END, values=(p, s, when))

    ttk.Button(root, text="Close", command=root.destroy).pack(pady=10)
    root.mainloop()


# --- Pygame Game Implementation ---
import pygame

class SpaceShooterGame:
    WIDTH = 900
    HEIGHT = 650
    FPS = 60

    def __init__(self, player_name: str):
        self.player_name = player_name
        pygame.init()

        self.shoot_sound = pygame.mixer.Sound("media/laser.mp3")
        self.hit_sound = pygame.mixer.Sound("media/explosion.wav")
        self.game_over_sound = pygame.mixer.Sound("media/over.mp3")

        # Background music (looping)
        pygame.mixer.music.load("media/game.mp3")
        pygame.mixer.music.set_volume(0.5)  # 0.0 → 1.0
        pygame.mixer.music.play(-1)

        pygame.display.set_caption("Space Shooter")
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # --- Load Images ---
        self.player_img = pygame.image.load("media/fighter.png").convert_alpha()
        self.enemy_img = pygame.image.load("media/enemy.png").convert_alpha()
        self.bullet_img = pygame.image.load("media/bullet.png").convert_alpha()

        # Resize for consistency
        self.player_img = pygame.transform.scale(self.player_img, (70, 50))
        self.enemy_img = pygame.transform.scale(self.enemy_img, (60, 45))
        self.bullet_img = pygame.transform.scale(self.bullet_img, (20, 40 ))

        # Game state (Rects for positions/collisions)
        self.player = self.player_img.get_rect(midbottom=(self.WIDTH // 2, self.HEIGHT - 30))
        self.player_speed = 7
        self.bullets = []  # list of Rect
        self.bullet_speed = -10
        self.enemies = []  # list of Rect
        self.enemy_speed_min = 1
        self.enemy_speed_max = 2
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 1600  # ms
        self.enemy_speeds = {}

        self.score = 0
        self.lives = 3

        self.font = pygame.font.SysFont("Arial", 20)
        self.big_font = pygame.font.SysFont("Arial", 36, bold=True)

    def spawn_enemy(self):
        rect = self.enemy_img.get_rect(
            topleft=(random.randint(0, self.WIDTH - self.enemy_img.get_width()), -30)
        )
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

        # Keep on screen
        self.player.clamp_ip(self.screen.get_rect())

    def shoot(self):
        # Spawn bullet rect at player position
        b = self.bullet_img.get_rect(midbottom=(self.player.centerx, self.player.top))
        self.bullets.append(b)
        self.shoot_sound.play()

    def update(self, dt_ms):
        # spawn enemies
        self.enemy_spawn_timer += dt_ms
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer = 0
            self.spawn_enemy()

        # move bullets
        for b in self.bullets:
            b.y += self.bullet_speed
        self.bullets = [b for b in self.bullets if b.bottom > 0]

        # move enemies
        for e in self.enemies:
            e.y += self.enemy_speeds.get(id(e), 3)

        # off-screen enemies reduce lives
        still = []
        for e in self.enemies:
            if e.top > self.HEIGHT:
                self.lives -= 1
            else:
                still.append(e)
        self.enemies = still

        # collisions: bullet vs enemy
        remaining_enemies = []
        for e in self.enemies:
            hit = False
            for b in list(self.bullets):
                if e.colliderect(b):
                    self.score += 10
                    hit = True
                    self.bullets.remove(b)
                    self.hit_sound.play()
                    break
            if not hit:
                remaining_enemies.append(e)
        self.enemies = remaining_enemies

        # collisions: enemy vs player
        for e in list(self.enemies):
            if e.colliderect(self.player):
                self.lives -= 1
                self.enemies.remove(e)

        if self.lives <= 0:
            self.running = False

    def draw(self):
        self.screen.fill((10, 10, 18))

        # background stars
        for _ in range(80):
            x = random.randint(0, self.WIDTH - 1)
            y = random.randint(0, self.HEIGHT - 1)
            self.screen.fill((255, 255, 255), ((x, y), (1, 1)))

        # --- Draw with images instead of shapes ---
        self.screen.blit(self.player_img, self.player)

        for b in self.bullets:
            self.screen.blit(self.bullet_img, b)

        for e in self.enemies:
            self.screen.blit(self.enemy_img, e)

        # HUD
        hud = self.font.render(
            f"{self.player_name}   Score: {self.score}   Lives: {self.lives}",
            True,
            (220, 220, 220),
        )
        self.screen.blit(hud, (10, 10))

    def run(self) -> int:
        shoot_cooldown = 200  # ms
        last_shot = 0

        while self.running:
            dt = self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        now = pygame.time.get_ticks()
                        if now - last_shot >= shoot_cooldown:
                            self.shoot()
                            last_shot = now

            self.handle_input()
            self.update(dt)
            self.draw()
            pygame.display.flip()

        pygame.mixer.music.stop()
        self.game_over_sound.play()
        pygame.time.delay(5000)
        pygame.quit()
        return self.score


def main():
    init_db()

    # Optional intro
    show_intro_turtle(show=True, duration_sec=1.6)

    # Menu for player name
    player = run_tk_menu_and_return_player()
    if not player:
        print("Goodbye!")
        return

    # Run Pygame loop
    game = SpaceShooterGame(player)
    score = game.run()

    # Save + show final scoreboard
    try:
        save_score(player, score)
    except Exception as e:
        print("Failed to save score:", e)

    show_final_scores_dialog(score)


if __name__ == "__main__":
    main()
