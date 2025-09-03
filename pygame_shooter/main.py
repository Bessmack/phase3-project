"""
Main entry point for PyGame Shooter
"""
import pygame
from modules.database import db_init
from modules.ui import launcher_menu
from modules.config import WIDTH, HEIGHT

def main():
    """Initialize and run the game"""
    db_init()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Shooter — Choose Mode")
    clock = pygame.time.Clock()
    bigfont = pygame.font.SysFont("arial", 36, bold=True)

    chosen = launcher_menu(screen, clock, bigfont)
    pygame.display.quit()
    
    from modules.game import run_game
    run_game(chosen)

if __name__ == "__main__":
    main()
