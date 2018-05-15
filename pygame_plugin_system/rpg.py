import pygame
import tmx

from pygame_plugin_system.quitable import QuitableWindow
from pygame_plugin_system.resizable import ResizableWindow
from pygame_plugin_system.tmx import TMXWindow

__all__ = ['RPGWindow']


class Player(pygame.sprite.Sprite):
	def __init__(self, *groups, image, location, tilemap):
		super().__init__(*groups)
		self.image = image
		self.rect = pygame.rect.Rect(location, self.image.get_size())
		self.tilemap = tilemap
	
	def update(self, dt):
		# last = self.rect.copy()
		
		key = pygame.key.get_pressed()
		
		if key[pygame.K_UP]:
			self.rect.y -= self.rect.height + 2
		if key[pygame.K_DOWN]:
			self.rect.y += self.rect.height + 2
		if key[pygame.K_LEFT]:
			self.rect.x -= self.rect.height + 2
		if key[pygame.K_RIGHT]:
			self.rect.x += self.rect.height + 2
		
		new = self.rect
		self.resting = False
		# for cell in self.tilemap.layers['triggers'].collide(new, 'blockers'):
		# 	blockers = cell['blockers']
		# 	if 'l' in blockers and last.right <= cell.left < new.right:
		# 		new.right = cell.left
		# 	if 'r' in blockers and cell.right <= new.left < last.left:
		# 		new.left = cell.right
		# 	if 't' in blockers and last.bottom <= cell.top < new.bottom:
		# 		new.bottom = cell.top
		# 	if 'b' in blockers and new.top < cell.bottom <= last.top:
		# 		new.top = cell.bottom
		
		self.tilemap.set_focus(new.x, new.y)


class RPGWindow(QuitableWindow, ResizableWindow, TMXWindow):
	def __init__(self, *, player_icon: pygame.Surface, **kwargs):
		super().__init__(player_icon=player_icon, **kwargs)
		
		self.sprites = tmx.SpriteLayer()
		self.tilemap.layers.append(self.sprites)
		start_cell = self.tilemap.layers['triggers'].find('player')[0]
		self.player = Player(self.sprites, image=player_icon.convert(), location=(start_cell.px, start_cell.py), tilemap=self.tilemap)
		self.tilemap.set_focus(start_cell.px, start_cell.py, force=True)
	
	def main_loop(self, screen: pygame.Surface):
		super().main_loop(screen)
	
	def on_event(self, event: pygame.event.EventType):
		super().on_event(event)
