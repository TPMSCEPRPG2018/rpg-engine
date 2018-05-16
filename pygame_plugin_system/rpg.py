import pygame
import tmx

from pygame_plugin_system.quitable import QuitableWindow
from pygame_plugin_system.resizable import ResizableWindow
from pygame_plugin_system.tmx import TMXWindow

__all__ = ['RPGWindow']


class Player(pygame.sprite.Sprite):
	def __init__(self, *groups, image, location, window):
		super().__init__(*groups)
		self.image = image
		self.rect = pygame.rect.Rect(location, self.image.get_size())
		self.window = window
	
	def update(self, dt):
		last = self.rect.copy()
		
		key = pygame.key.get_pressed()
		
		if key[pygame.K_UP]:
			self.rect.y -= self.rect.height
		if key[pygame.K_DOWN]:
			self.rect.y += self.rect.height
		if key[pygame.K_LEFT]:
			self.rect.x -= self.rect.width
		if key[pygame.K_RIGHT]:
			self.rect.x += self.rect.width
		
		new = self.rect
		
		for cell in self.window.tilemap.layers['triggers'].collide(new, 'blockers'):
			if last.right <= cell.left <= new.right and new.top != cell.bottom and new.bottom != cell.top:
				new.right = cell.left
			if new.left <= cell.right <= last.left and new.top != cell.bottom and new.bottom != cell.top:
				new.left = cell.right
			if last.bottom <= cell.top <= new.bottom and new.left != cell.right and new.right != cell.left:
				new.bottom = cell.top
			if cell.top <= new.bottom <= last.top and new.left != cell.right and new.right != cell.left:
				new.top = cell.bottom
		
		self.window.tilemap.set_focus(new.x, new.y)


class RPGWindow(QuitableWindow, ResizableWindow, TMXWindow):
	def __init__(self, *, player_icon: pygame.Surface, tile_size: int = 1, **kwargs):
		super().__init__(player_icon=player_icon, tile_size=tile_size, **kwargs)
		
		self.sprites = tmx.SpriteLayer()
		self.tilemap.layers.append(self.sprites)
		start_cell = self.tilemap.layers['triggers'].find('player')[0]
		self.player = Player(self.sprites, image=player_icon.convert_alpha(), location=(start_cell.px, start_cell.py), window=self)
		self.tilemap.set_focus(start_cell.px, start_cell.py, force=True)
		self.tile_size = tile_size
	
	def main_loop(self, screen: pygame.Surface):
		super().main_loop(screen)
	
	def on_event(self, event: pygame.event.EventType):
		super().on_event(event)
