from pathlib import Path

__all__ = ['START_SIZE', 'BALL_PATH', 'MAP_PATH', 'TICK_RATE', 'RESOURCES_DIR', 'PLAYER_ICON_PATH']

START_SIZE = 640, 480
TICK_RATE = 10

BASE_DIR = Path(__file__).parent
RESOURCES_DIR = BASE_DIR / 'resources'

BALL_PATH = RESOURCES_DIR / 'intro_ball.gif'
MAP_PATH = RESOURCES_DIR / 'map.tmx'
PLAYER_ICON_PATH = RESOURCES_DIR / 'player.png'
