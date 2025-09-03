"""
Asset loading and management
"""
import pygame
from modules.config import MODE_CONFIGS, WIDTH, HEIGHT

def load_assets():
    """Load all game assets"""
    assets = {
        "player": None,
        "bullet": None,
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
        assets["player"] = pygame.image.load("../media/player.png").convert_alpha()
        assets["player"] = pygame.transform.scale(assets["player"], (80, 60))
        
        # Load bullet image
        assets["bullet"] = pygame.image.load("../media/bullet.png").convert_alpha()
        assets["bullet"] = pygame.transform.scale(assets["bullet"], (24, 48))
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading player/bullet images: {e}")
    
    # Load enemy images
    for shape in assets["enemies"]:
        try:
            img = pygame.image.load(f"../media/enemy_{shape}.png").convert_alpha()
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
        assets["sounds"]["shoot"] = pygame.mixer.Sound("../media/shoot.wav")
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading shoot sound: {e}")
    
    try:
        assets["sounds"]["hit"] = pygame.mixer.Sound("../media/hit.wav")
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading hit sound: {e}")
    
    try:
        assets["sounds"]["explode"] = pygame.mixer.Sound("../media/explode.wav")
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading explode sound: {e}")
        
    return assets
