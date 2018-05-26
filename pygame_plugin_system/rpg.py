from random import choice, random
from typing import Optional, Tuple

import pygame

import tmx
from pygame_plugin_system.quitable import QuitableWindow
from pygame_plugin_system.resizable import ResizableWindow
from pygame_plugin_system.tmx import TMXWindow

__all__ = ['RPGWindow']


class RPGWindow(QuitableWindow, ResizableWindow, TMXWindow):
	def __init__(self, *, player_icon: pygame.Surface, enemy_icon: pygame.Surface, tile_size: int = 1, **kwargs):
		self.player_icon = player_icon
		self.enemy_icon = enemy_icon
		self.tile_size = tile_size
		
		self.sprites = tmx.SpriteLayer()
		self.start_cell = (0, 0)
		super().__init__(player_icon=player_icon, tile_size=tile_size, **kwargs)
		self.player = Player(self.sprites, image=self.player_icon.convert_alpha(), window=self, location=self.start_cell)
	
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
	
	def main_loop(self, screen: pygame.Surface):
		super().main_loop(screen)
	
	def on_event(self, event: pygame.event.EventType):
		super().on_event(event)
	
	def spawn(self, enemy: 'Enemy'):
		self.sprites.add(enemy)


class Player(pygame.sprite.Sprite):
	def __init__(self, *groups, image: pygame.Surface, location: Tuple[int, int], window: RPGWindow):
		super().__init__(*groups)
		self.image = image
		self.rect = pygame.rect.Rect(location, self.image.get_size())
		self.window = window
	
	def update(self, dt):
		old = self.rect.copy()
		
		key = pygame.key.get_pressed()
		
		if key[pygame.K_UP]:
			self.rect.y -= self.rect.height
		if key[pygame.K_DOWN]:
			self.rect.y += self.rect.height
		if key[pygame.K_LEFT]:
			self.rect.x -= self.rect.width
		if key[pygame.K_RIGHT]:
			self.rect.x += self.rect.width
		
		for obj in self.window.tilemap.layers['triggers'].collide(self.rect, 'isSolid'):
			if old.right <= obj.left <= self.rect.right and (obj.top <= self.rect.top < obj.bottom or obj.top < self.rect.bottom <= obj.bottom):
				self.rect.right = obj.left
			if self.rect.left <= obj.right <= old.left and (obj.top <= self.rect.top < obj.bottom or obj.top < self.rect.bottom <= obj.bottom):
				self.rect.left = obj.right
			if old.bottom <= obj.top <= self.rect.bottom and (obj.left <= self.rect.left < obj.right or obj.left < self.rect.right <= obj.right):
				self.rect.bottom = obj.top
			if self.rect.top <= obj.bottom <= old.top and (obj.left <= self.rect.left < obj.right or obj.left < self.rect.right <= obj.right):
				self.rect.top = obj.bottom
		
		# if old.right <= obj.left <= self.rect.right and self.rect.top != obj.bottom and self.rect.bottom != obj.top:
		# 	self.rect.right = obj.left
		# if self.rect.left <= obj.right <= old.left and self.rect.top != obj.bottom and self.rect.bottom != obj.top:
		# 	self.rect.left = obj.right
		# if old.bottom <= obj.top <= self.rect.bottom and self.rect.left != obj.right and self.rect.right != obj.left:
		# 	self.rect.bottom = obj.top
		# if self.rect.top <= obj.bottom <= old.top and self.rect.left != obj.right and self.rect.right != obj.left:
		# 	self.rect.top = obj.bottom
		
		for obj in self.window.sprites:
			if obj is not self:
				if old.right <= obj.rect.left <= self.rect.right and (obj.rect.top <= self.rect.top < obj.rect.bottom or obj.rect.top < self.rect.bottom <= obj.rect.bottom):
					self.rect.right = obj.rect.left
				if self.rect.left <= obj.rect.right <= old.left and (obj.rect.top <= self.rect.top < obj.rect.bottom or obj.rect.top < self.rect.bottom <= obj.rect.bottom):
					self.rect.left = obj.rect.right
				if old.bottom <= obj.rect.top <= self.rect.bottom and (obj.rect.left <= self.rect.left < obj.rect.right or obj.rect.left < self.rect.right <= obj.rect.right):
					self.rect.bottom = obj.rect.top
				if self.rect.top <= obj.rect.bottom <= old.top and (obj.rect.left <= self.rect.left < obj.rect.right or obj.rect.left < self.rect.right <= obj.rect.right):
					self.rect.top = obj.rect.bottom
		
		tilemap = self.window.tilemap
		window_rect = pygame.Rect(tilemap.view_x, tilemap.view_y, tilemap.px_width, tilemap.px_height)
		if window_rect.right <= self.rect.right:
			self.rect.right = window_rect.right
		if self.rect.left <= window_rect.left:
			self.rect.left = window_rect.left
		if window_rect.bottom <= self.rect.bottom:
			self.rect.bottom = window_rect.bottom
		if self.rect.top <= window_rect.top:
			self.rect.top = window_rect.top
		
		for area in self.window.tilemap.layers['triggers'].collide(self.rect, 'probEnemy'):
			if old != self.rect and random() < float(area['probEnemy']):
				enemy_rect = self.rect
				self.rect = old
				self.window.spawn(Enemy(image=self.window.enemy_icon, location=enemy_rect.topleft, window=self.window))
		
		entries = self.window.tilemap.layers['triggers'].collide(self.rect, 'destinationMap')
		
		if entries:
			entry = choice(entries)
			self.window.set_tilemap(map_path=entry['destinationMap'], start_cell=(entry['destinationX'], entry['destinationY']))
		
		self.window.tilemap.set_focus(self.rect.x, self.rect.y)


class Enemy(pygame.sprite.Sprite):
	def __init__(self, *groups, image: pygame.Surface, location: Tuple[int, int], window: RPGWindow):
		super().__init__(*groups)
		self.image = image
		self.rect = pygame.rect.Rect(location, self.image.get_size())
		self.window = window
