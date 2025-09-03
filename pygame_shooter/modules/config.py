"""
Game configuration and constants
"""
WIDTH, HEIGHT = 900, 650
FPS = 60
DB_FILE = "sqlite:///scores.db"

# Mode configurations
MODE_CONFIGS = {
    "Easy": {
        "player_speed": 6,
        "bullet_speed": -10,
        "enemy_speed": 2,
        "spawn_rate": 30,
        "bg_image": "../media/bg_easy.png",
        "music": "../media/game.mp3",
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
        "bg_image": "../media/bg_medium.png",
        "music": "../media/game.mp3",
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
        "bg_image": "../media/bg_hard.png",
        "music": "../media/game.mp3",
        "enemy_shape": "asteroid",
        "palette": {
            "bullet": (255, 200, 255),
        },
    },
}
