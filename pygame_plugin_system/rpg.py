from enum import Enum, auto
from operator import itemgetter
from random import choice, random
from typing import Dict, Optional, Tuple

import pygame

import tmx
from pygame_plugin_system.quitable import QuitableWindow
from pygame_plugin_system.resizable import ResizableWindow
from pygame_plugin_system.tmx import TMXWindow

__all__ = ['RPGWindow', 'Direction', 'Foot']


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class Foot(Enum):
    LEFT = auto()
    RIGHT = auto()


class RPGWindow(QuitableWindow, ResizableWindow, TMXWindow):
    def __init__(self, *, enemy_icon: pygame.Surface, tile_size: int = 1, enemy_hp: float, player_hp: float,
                 font_color: Tuple[int, int, int], player_icons: Dict[Tuple[Direction, Foot], pygame.Surface],
                 **kwargs):
        self.font_color = font_color
        self.enemy_hp = enemy_hp
        self.enemy_icon = enemy_icon
        self.tile_size = tile_size

        self.sprites = tmx.SpriteLayer()
        self.start_cell = (0, 0)
        super().__init__(enemy_icon=enemy_icon, tile_size=tile_size, enemy_hp=enemy_hp, player_hp=player_hp,
                         font_color=font_color, player_icons=player_icons, **kwargs)
        self.player = Player(self.sprites, images={key: icon.convert_alpha() for key, icon in player_icons.items()},
                             window=self, location=self.start_cell, hp=player_hp)

    def set_tilemap(self, *, map_path: str, start_cell: Optional[Tuple[int, int]] = None, **kwargs):
        super().set_tilemap(map_path=map_path)

        self.tilemap.layers.append(self.sprites)

        if start_cell is None:
            start_cell = choice(self.tilemap.layers['triggers'].match(isStart='true'))
            start_cell = start_cell.px, start_cell.py

        self.tilemap.set_focus(*start_cell, force=True)

        try:
            player = self.player
        except AttributeError:
            self.start_cell = start_cell
        else:
            player.rect.x, player.rect.y = start_cell

    def main_loop(self):
        super().main_loop()

    def on_event(self, event: pygame.event.EventType):
        super().on_event(event)

    def spawn(self, enemy: 'Enemy'):
        self.sprites.add(enemy)

    def render_text(self, text: str, width: int, height: int) -> pygame.Surface:
        size = min(width * 100 / pygame.font.Font(None, 100).size(text)[0], height)
        return pygame.font.Font(None, int(size)).render(text, True, self.font_color)

    def show_big_text(self, text: str):
        self.screen.blit(self.render_text(text, self.screen.get_rect().width, self.screen.get_rect().height), (0, 0))
        pygame.display.flip()

        while not pygame.key.get_pressed()[pygame.K_RETURN]:
            for event in iter(pygame.event.poll, pygame.event.Event(pygame.NOEVENT)):
                self.on_event(event)

    def collide_rects(self, rect1, rect2):
        if rect1.right < rect2.left:
            return False
    
        if rect2.right < rect1.left:
            return False
    
        if rect1.bottom < rect2.top:
            return False
    
        if rect2.bottom < rect1.top:
            return False
    
        return True

    def collide_border(self, location):
        window_rect = pygame.Rect(self.tilemap.view_x, self.tilemap.view_y, self.tilemap.px_width,
                                  self.tilemap.px_height)
        if window_rect.right < location.right:
            return False
        if window_rect.left > location.left:
            return False
        if window_rect.bottom < location.bottom:
            return False
        if window_rect.top > location.top:
            return False
        return True

    def collide_sprite(self, sprite1):
        collisions = set()

        for sprite2 in self.sprites:
            if sprite2 is not sprite1:
                if self.collide_rects(sprite1.rect, sprite2.rect):
                    collisions.add(sprite2)
        
        return collisions

    def can_move(self, location: pygame.Rect):
        for obj in self.tilemap.layers['triggers'].collide(location, 'isSolid'):
            if self.collide_rects(location, obj):
                return False
    
        return self.collide_border(location)


class Entity(pygame.sprite.Sprite):
    def __init__(self, *groups, location: Tuple[int, int], window: RPGWindow, hp: float):
        super().__init__(*groups)
        self.image = self.get_image()
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.window = window
        self.hp = hp
        self.show_hp()
    
    def show_hp(self):
        self.image = self.get_image()
        self.image.blit(self.window.render_text(str(self.hp), self.rect.width, self.rect.height), (0, 0))
    
    def get_image(self):
        """Override this and return the image to display."""


class Player(Entity):
    def __init__(self, *groups, images: Dict[Tuple[Direction, Foot], pygame.Surface], location: Tuple[int, int],
                 window: RPGWindow, hp: float):
        self.direction = Direction.UP
        self.foot = Foot.LEFT
        self.images = images

        super().__init__(*groups, location=location, window=window, hp=hp)
    
    def get_image(self):
        return self.images[self.direction, self.foot].copy()

    def update(self, dt):
        old = self.rect.copy()
        new = self.rect.copy()
        
        key = pygame.key.get_pressed()

        if key[pygame.K_UP]:
            self.direction = Direction.UP
            self.animate_walk()
            new.y -= self.rect.height
        if key[pygame.K_DOWN]:
            self.direction = Direction.DOWN
            self.animate_walk()
            new.y += self.rect.height
        if key[pygame.K_LEFT]:
            self.direction = Direction.LEFT
            self.animate_walk()
            new.x -= self.rect.width
        if key[pygame.K_RIGHT]:
            self.direction = Direction.RIGHT
            self.animate_walk()
            new.x += self.rect.width

        if self.window.can_move(new):
            self.rect = new

        if old != new:
            for enemy in self.window.collide_sprite(self):
                self.rect = old
                enemy.attack(1)
    
            for enemy in self.window.sprites:
                if enemy is not self:
                    enemy.tick()

        for area in self.window.tilemap.layers['triggers'].collide(self.rect, 'probEnemy'):
            if old != self.rect and random() < float(area['probEnemy']):
                enemy_rect = self.rect
                self.rect = old
                self.window.spawn(Enemy(image=self.window.enemy_icon, location=enemy_rect.topleft, window=self.window,
                                        hp=self.window.enemy_hp))

        entries = self.window.tilemap.layers['triggers'].collide(self.rect, 'destinationMap')

        if entries:
            entry = choice(entries)
            self.window.set_tilemap(map_path=entry['destinationMap'],
                                    start_cell=(entry['destinationX'], entry['destinationY']))

        self.window.tilemap.set_focus(self.rect.x, self.rect.y)

    def attack(self, damage: float):
        self.hp -= damage

        if self.hp <= 0:
            self.show_hp()
            self.window.tilemap.draw(self.window.screen)
            self.window.show_big_text('You lose :(')
            pygame.display.quit()
            pygame.quit()
            exit()
        else:
            self.show_hp()

    def animate_walk(self):
        self.foot = Foot.LEFT if self.foot == Foot.RIGHT else Foot.RIGHT
        self.show_hp()


class Enemy(Entity):
    def __init__(self, *groups, image: pygame.Surface, location: Tuple[int, int], window: RPGWindow, hp: float):
        self.original_image = image

        super().__init__(*groups, location=location, window=window, hp=hp)

    def get_image(self):
        return self.original_image.copy()

    def attack(self, damage: float):
        self.hp -= damage

        if self.hp <= 0:
            self.show_hp()
            self.window.tilemap.draw(self.window.screen)
            self.window.show_big_text('You killed an enemy!')
            self.kill()
        else:
            self.show_hp()

    def get_player_distances(self):
        player_rect = self.window.player.rect
        print(self.rect, player_rect)
        return {
            Direction.LEFT:  (self.rect.left - player_rect.right) // self.rect.width,
            Direction.RIGHT: (player_rect.left - self.rect.right) // self.rect.width,
            Direction.UP:    (self.rect.top - player_rect.bottom) // self.rect.height,
            Direction.DOWN:  (player_rect.top - self.rect.bottom) // self.rect.height
        }

    def move(self, direction: Direction, distance: int = 1):
        rect = self.rect.copy()

        if direction == Direction.UP:
            rect.y -= self.rect.height * distance
        elif direction == Direction.DOWN:
            rect.y += self.rect.height * distance
        elif direction == Direction.LEFT:
            rect.x -= self.rect.width * distance
        elif direction == Direction.RIGHT:
            rect.x += self.rect.width * distance

        return rect

    def tick(self):
        player_distances = self.get_player_distances()
        print(player_distances)

        if max(player_distances.values()) <= 0:
            self.window.player.attack(1)
        else:
            try:
                self.rect = self.move(
                    max(
                        ((direction, distance) for direction, distance in player_distances.items() if
                         self.window.can_move(self.move(direction)) and not self.window.collide_sprite(self)),
                        key=itemgetter(1)
                    )[0]
                )
            except ValueError:
                pass  # If it's impossible to move, don't move.
