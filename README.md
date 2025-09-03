Pygame Shooter 🎮
A space shooter game built with Pygame featuring a launcher menu, gameplay, and scoreboard system.

Features
Launcher Menu: Start screen with options to play or view scores

Space Shooter Gameplay: Control a spaceship and shoot enemies

Score System: Track your high scores

Scoreboard: View your best performances

Installation
Make sure you have Python 3.7+ installed

Install Pygame:
    pip install pygame

Clone or download this project

Navigate to the project directory

How to Play
Run the game:
    python main.py
Use the launcher menu:

Press 1 to start the game

Press 2 to view the scoreboard

Press ESC to quit

In-game controls:

Use arrow keys or WASD to move your spaceship

Press SPACE to shoot

Press ESC to pause or return to menu

Project Structure
pygame_shooter/
├── main.py              # Entry point of the application
├── modules/
│   ├── ui.py           # User interface components (menus)
│   ├── game.py         # Main game logic and loop
│   ├── scoreboard.py   # Scoreboard functionality
│   ├── player.py       # Player ship class and controls
│   ├── enemies.py      # Enemy classes and behavior
│   ├── weapons.py      # Weapon systems and projectiles
│   └── utils.py        # Utility functions and constants
├── assets/
│   ├── images/         # Sprites and background images
│   ├── sounds/         # Sound effects and music
│   └── fonts/          # Custom fonts
└── scores.json         # Score data (created after first run)

Requirements
Python 3.7+

Pygame 2.0+

Troubleshooting
If you encounter circular import errors:

Make sure all imports follow the pattern established in the refactored code

Check that you're not importing between ui.py and game.py directly

Use the dedicated scoreboard.py module for score-related functionality

Customization
You can modify various game aspects by editing the constants in modules/utils.py:

Game dimensions

Player speed

Enemy spawn rates

Difficulty settings

Visual elements

License
This project is open source and available under the MIT License.
