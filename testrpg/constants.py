from pathlib import Path as _Path

START_SIZE = 640, 480
TICK_RATE = 10
TILE_SIZE = 32

BASE_DIR = _Path(__file__).parent
RESOURCES_DIR = BASE_DIR / 'resources'

BALL_PATH = RESOURCES_DIR / 'intro_ball.gif'
MAP_PATH = RESOURCES_DIR / 'outside.tmx'
PLAYER_ICON_PATH = RESOURCES_DIR / 'smiley.png'
