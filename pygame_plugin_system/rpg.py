from random import choice, random
from typing import Optional, Tuple

import pygame

import tmx
from pygame_plugin_system.quitable import QuitableWindow
from pygame_plugin_system.resizable import ResizableWindow
from pygame_plugin_system.tmx import TMXWindow

__all__ = ['RPGWindow']


class RPGWindow(QuitableWindow, ResizableWindow, TMXWindow):
	def __init__(self, *, player_icon: pygame.Surface, enemy_icon: pygame.Surface, tile_size: int = 1, enemy_hp: float, player_hp: float, font_color: Tuple[int, int, int], **kwargs):
		self.font_color = font_color
		self.enemy_hp = enemy_hp
		self.player_icon = player_icon
		self.enemy_icon = enemy_icon
		self.tile_size = tile_size
		
		self.sprites = tmx.SpriteLayer()
		self.start_cell = (0, 0)
		super().__init__(player_icon=player_icon, tile_size=tile_size, **kwargs)
		self.player = Player(self.sprites, image=self.player_icon.convert_alpha(), window=self, location=self.start_cell, hp=player_hp)
		
		self.show_big_text('Hi!')
	
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
	
	def render_text(self, text: str, width: int, height: int) -> pygame.Surface:
		size = min(width * 100 / pygame.font.Font(None, 100).size(text)[0], height)
		return pygame.font.Font(None, int(size)).render(text, True, self.font_color)
	
	def show_big_text(self, text: str):
		self.screen.blit(self.render_text(text, self.screen.get_rect().width, self.screen.get_rect().height), (0, 0))
		pygame.display.flip()
		
		while not pygame.key.get_pressed()[pygame.K_RETURN]:
			for event in iter(pygame.event.poll, pygame.event.Event(pygame.NOEVENT)):
				self.on_event(event)


class Player(pygame.sprite.Sprite):
	def __init__(self, *groups, image: pygame.Surface, location: Tuple[int, int], window: RPGWindow, hp: float):
		super().__init__(*groups)
		self.original_image = image
		self.image = image.copy()
		self.rect = pygame.rect.Rect(location, self.image.get_size())
		self.window = window
		self.hp = hp
		self.show_hp()
	
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
		
		collisions = set()
		
		if self.rect != old:
			for sprite in self.window.sprites:
				if sprite is not self:
					sprite.tick()
					if old.right <= sprite.rect.left <= self.rect.right and old.right != self.rect.right and (sprite.rect.top <= self.rect.top < sprite.rect.bottom or sprite.rect.top < self.rect.bottom <= sprite.rect.bottom):
						collisions.add(sprite)
						self.rect.right = sprite.rect.left
					if self.rect.left <= sprite.rect.right <= old.left and old.left != self.rect.left and (sprite.rect.top <= self.rect.top < sprite.rect.bottom or sprite.rect.top < self.rect.bottom <= sprite.rect.bottom):
						collisions.add(sprite)
						self.rect.left = sprite.rect.right
					if old.bottom <= sprite.rect.top <= self.rect.bottom and old.bottom != self.rect.bottom and (sprite.rect.left <= self.rect.left < sprite.rect.right or sprite.rect.left < self.rect.right <= sprite.rect.right):
						collisions.add(sprite)
						self.rect.bottom = sprite.rect.top
					if self.rect.top <= sprite.rect.bottom <= old.top and old.top != self.rect.top and (sprite.rect.left <= self.rect.left < sprite.rect.right or sprite.rect.left < self.rect.right <= sprite.rect.right):
						collisions.add(sprite)
						self.rect.top = sprite.rect.bottom
		
		for enemy in collisions:
			enemy.attack(1)
		
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
				self.window.spawn(Enemy(image=self.window.enemy_icon, location=enemy_rect.topleft, window=self.window, hp=self.window.enemy_hp))
		
		entries = self.window.tilemap.layers['triggers'].collide(self.rect, 'destinationMap')
		
		if entries:
			entry = choice(entries)
			self.window.set_tilemap(map_path=entry['destinationMap'], start_cell=(entry['destinationX'], entry['destinationY']))
		
		self.window.tilemap.set_focus(self.rect.x, self.rect.y)
	
	def attack(self, damage: float):
		self.hp -= damage
		
		if self.hp <= 0:
			pygame.display.quit()
			pygame.quit()
			print('You lose :(')
			exit()
		else:
			self.show_hp()
	
	def show_hp(self):
		self.image = self.original_image.copy()
		self.image.blit(self.window.render_text(str(self.hp), self.rect.width, self.rect.height), (0, 0))


class Enemy(pygame.sprite.Sprite):
	def __init__(self, *groups, image: pygame.Surface, location: Tuple[int, int], window: RPGWindow, hp: float):
		super().__init__(*groups)
		self.original_image = image
		self.image = image.copy()
		self.rect = pygame.rect.Rect(location, self.image.get_size())
		self.window = window
		self.hp = hp
		self.show_hp()
	
	def attack(self, damage: float):
		self.hp -= damage
		
		if self.hp <= 0:
			self.kill()
			self.window.main_loop(self.window.screen)
			self.window.show_big_text('You killed an enemy!')
		else:
			self.show_hp()
	
	def show_hp(self):
		self.image = self.original_image.copy()
		self.image.blit(self.window.render_text(str(self.hp), self.rect.width, self.rect.height), (0, 0))
	
	def tick(self):
		player_rect = self.window.player.rect
		if ((player_rect.left == self.rect.right or player_rect.right == self.rect.left) and player_rect.top == self.rect.top and player_rect.bottom == self.rect.bottom) or ((player_rect.top == self.rect.bottom or player_rect.bottom == self.rect.top) and player_rect.left == self.rect.left and player_rect.right == self.rect.right):
			self.window.player.attack(1)
