"""
Mario-like Platformer Game - I Wanna Be The Guy Edition!
A 2D side-scrolling platformer with RIDICULOUS traps and hazards
"""

import pygame
import sys
import random
import array

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (107, 140, 255)
GROUND_BROWN = (139, 69, 19)
BRICK_COLOR = (185, 122, 87)
PIPE_GREEN = (34, 177, 76)
PLAYER_RED = (237, 28, 36)
ENEMY_BROWN = (160, 100, 50)
ENEMY_PURPLE = (150, 50, 150)
ENEMY_ORANGE = (255, 140, 0)
COIN_GOLD = (255, 215, 0)
SPIKE_GRAY = (128, 128, 128)
TEXT_COLOR = (255, 255, 255)
FLAG_RED = (220, 20, 60)
FLAG_POLE = (200, 200, 200)
ANGRY_RED = (255, 0, 0)
CRAZY_YELLOW = (255, 255, 0)
FRUIT_RED = (255, 50, 50)
FRUIT_ORANGE = (255, 165, 0)
FRUIT_GREEN = (50, 205, 50)
BAT_BLACK = (30, 30, 30)
PLATFORM_BLUE = (70, 130, 180)
TRAP_RED = (200, 0, 0)
TRAP_DARK = (100, 0, 0)
TRAP_ORANGE = (255, 100, 0)

GRAVITY = 0.8
JUMP_FORCE = -14
PLAYER_SPEED = 5
ENEMY_SPEED = 2
MAX_FALL_SPEED = 12

TILE_EMPTY = 0
TILE_GROUND = 1
TILE_BLOCK = 2
TILE_PIPE = 3
TILE_PIPE_TOP = 4
TILE_SPIKE = 5
TILE_FLAG = 6
TILE_SPIKE_UP = 7
TILE_PLATFORM_MOVING = 8

STATE_PLAYING = 0
STATE_GAME_OVER = 1
STATE_WIN = 2
STATE_PAUSED = 3


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 28
        self.height = 32
        
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(PLAYER_RED)
        pygame.draw.rect(self.image, BLACK, (4, 4, 6, 6))
        pygame.draw.rect(self.image, BLACK, (18, 4, 6, 6))
        pygame.draw.rect(self.image, (180, 20, 20), (0, 0, self.width, 4))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        
        self.anim_frame = 0
        self.anim_timer = 0
        self.jump_pressed = False
        
        self.lives = 3
        self.score = 0
        self.alive = True
    
    def update(self, keys, tiles, platforms):
        if not self.alive:
            return
        
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
        
        self.rect.x += self.vel_x
        self.handle_collision(tiles, horizontal=True)
        
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground and not self.jump_pressed:
            self.vel_y = JUMP_FORCE
            self.on_ground = False
            self.jump_pressed = True
        
        if not (keys[pygame.K_SPACE] or keys[pygame.K_w]):
            self.jump_pressed = False
        
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
        
        self.rect.y += self.vel_y
        self.on_ground = False
        self.handle_collision(tiles, horizontal=False)
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0 and self.rect.bottom < platform.rect.centery + 10:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0 and self.rect.top > platform.rect.centery - 10:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
        
        self.anim_timer += 1
        if self.anim_timer > 10:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 2
    
    def handle_collision(self, tiles, horizontal):
        for tile in tiles:
            if tile.type in (TILE_GROUND, TILE_BLOCK, TILE_PIPE, TILE_PIPE_TOP):
                if self.rect.colliderect(tile.rect):
                    if horizontal:
                        if self.vel_x > 0:
                            self.rect.right = tile.rect.left
                        elif self.vel_x < 0:
                            self.rect.left = tile.rect.right
                    else:
                        if self.vel_y > 0:
                            self.rect.bottom = tile.rect.top
                            self.vel_y = 0
                            self.on_ground = True
                        elif self.vel_y < 0:
                            self.rect.top = tile.rect.bottom
                            self.vel_y = 0
    
    def draw(self, surface, camera_x):
        draw_x = self.rect.x - camera_x
        img = self.image.copy()
        
        if self.vel_x != 0 and self.on_ground:
            if self.anim_frame == 0:
                pygame.draw.rect(img, (200, 20, 20), (2, 10, 4, 8))
            else:
                pygame.draw.rect(img, (200, 20, 20), (2, 8, 4, 6))
        
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        
        surface.blit(img, (draw_x, self.rect.y))


class Goomba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 28
        self.height = 28
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(ENEMY_BROWN)
        pygame.draw.circle(self.image, WHITE, (8, 10), 4)
        pygame.draw.circle(self.image, WHITE, (20, 10), 4)
        pygame.draw.circle(self.image, BLACK, (8, 10), 2)
        pygame.draw.circle(self.image, BLACK, (20, 10), 2)
        pygame.draw.rect(self.image, (120, 70, 30), (4, 22, 8, 6))
        pygame.draw.rect(self.image, (120, 70, 30), (16, 22, 8, 6))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = ENEMY_SPEED
        self.vel_y = 0
        self.direction = 1
        self.on_ground = False
        self.alive = True
    
    def update(self, tiles):
        if not self.alive:
            return
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
        self.rect.x += self.vel_x * self.direction
        self.handle_horizontal_collision(tiles)
        self.rect.y += self.vel_y
        self.on_ground = False
        self.handle_vertical_collision(tiles)
    
    def handle_horizontal_collision(self, tiles):
        for tile in tiles:
            if tile.type in (TILE_GROUND, TILE_BLOCK, TILE_PIPE, TILE_PIPE_TOP):
                if self.rect.colliderect(tile.rect):
                    if self.vel_x * self.direction > 0:
                        self.rect.right = tile.rect.left
                    else:
                        self.rect.left = tile.rect.right
                    self.direction *= -1
    
    def handle_vertical_collision(self, tiles):
        for tile in tiles:
            if tile.type in (TILE_GROUND, TILE_BLOCK, TILE_PIPE, TILE_PIPE_TOP):
                if self.rect.colliderect(tile.rect):
                    if self.vel_y > 0:
                        self.rect.bottom = tile.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:
                        self.rect.top = tile.rect.bottom
                        self.vel_y = 0
    
    def draw(self, surface, camera_x):
        if not self.alive:
            return
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class AngryGoomba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 32
        self.height = 32
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(ENEMY_PURPLE)
        pygame.draw.circle(self.image, WHITE, (10, 12), 5)
        pygame.draw.circle(self.image, WHITE, (24, 12), 5)
        pygame.draw.line(self.image, ANGRY_RED, (6, 8), (14, 12), 3)
        pygame.draw.line(self.image, ANGRY_RED, (18, 12), (26, 8), 3)
        pygame.draw.circle(self.image, BLACK, (10, 12), 3)
        pygame.draw.circle(self.image, BLACK, (24, 12), 3)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = ENEMY_SPEED * 1.5
        self.vel_y = 0
        self.direction = 1
        self.on_ground = False
        self.alive = True
        self.rage_timer = 0
    
    def update(self, tiles):
        if not self.alive:
            return
        self.rage_timer += 1
        if self.rage_timer > 60:
            self.vel_x = ENEMY_SPEED * 2.5
            self.rage_timer = 0
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
        self.rect.x += self.vel_x * self.direction
        self.handle_horizontal_collision(tiles)
        self.rect.y += self.vel_y
        self.on_ground = False
        self.handle_vertical_collision(tiles)
    
    def handle_horizontal_collision(self, tiles):
        for tile in tiles:
            if tile.type in (TILE_GROUND, TILE_BLOCK, TILE_PIPE, TILE_PIPE_TOP):
                if self.rect.colliderect(tile.rect):
                    if self.vel_x * self.direction > 0:
                        self.rect.right = tile.rect.left
                    else:
                        self.rect.left = tile.rect.right
                    self.direction *= -1
    
    def handle_vertical_collision(self, tiles):
        for tile in tiles:
            if tile.type in (TILE_GROUND, TILE_BLOCK, TILE_PIPE, TILE_PIPE_TOP):
                if self.rect.colliderect(tile.rect):
                    if self.vel_y > 0:
                        self.rect.bottom = tile.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:
                        self.rect.top = tile.rect.bottom
                        self.vel_y = 0
    
    def draw(self, surface, camera_x):
        if not self.alive:
            return
        img = self.image.copy()
        if self.rage_timer < 5:
            pygame.draw.rect(img, ANGRY_RED, (0, 0, self.width, 4))
        surface.blit(img, (self.rect.x - camera_x, self.rect.y))


class CrazyKoopa(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 28
        self.height = 40
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(ENEMY_ORANGE)
        pygame.draw.circle(self.image, WHITE, (10, 10), 4)
        pygame.draw.circle(self.image, WHITE, (20, 10), 4)
        pygame.draw.circle(self.image, CRAZY_YELLOW, (10, 10), 2)
        pygame.draw.circle(self.image, CRAZY_YELLOW, (20, 10), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = ENEMY_SPEED * 0.8
        self.vel_y = 0
        self.direction = 1
        self.on_ground = False
        self.alive = True
        self.spin_timer = 0
        self.spinning = False
    
    def update(self, tiles):
        if not self.alive:
            return
        self.spin_timer += 1
        if self.spin_timer > 90:
            self.spinning = not self.spinning
            self.spin_timer = 0
            self.vel_x = ENEMY_SPEED * 3 if self.spinning else ENEMY_SPEED * 0.8
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
        self.rect.x += self.vel_x * self.direction
        self.handle_horizontal_collision(tiles)
        self.rect.y += self.vel_y
        self.on_ground = False
        self.handle_vertical_collision(tiles)
    
    def handle_horizontal_collision(self, tiles):
        for tile in tiles:
            if tile.type in (TILE_GROUND, TILE_BLOCK, TILE_PIPE, TILE_PIPE_TOP):
                if self.rect.colliderect(tile.rect):
                    if self.vel_x * self.direction > 0:
                        self.rect.right = tile.rect.left
                    else:
                        self.rect.left = tile.rect.right
                    if not self.spinning:
                        self.direction *= -1
    
    def handle_vertical_collision(self, tiles):
        for tile in tiles:
            if tile.type in (TILE_GROUND, TILE_BLOCK, TILE_PIPE, TILE_PIPE_TOP):
                if self.rect.colliderect(tile.rect):
                    if self.vel_y > 0:
                        self.rect.bottom = tile.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:
                        self.rect.top = tile.rect.bottom
                        self.vel_y = 0
    
    def draw(self, surface, camera_x):
        if not self.alive:
            return
        img = self.image.copy()
        if self.spinning:
            angle = (self.spin_timer * 30) % 360
            img = pygame.transform.rotate(img, angle)
        surface.blit(img, (self.rect.x - camera_x, self.rect.y))


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = 20
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COIN_GOLD, (self.size//2, self.size//2), self.size//2)
        pygame.draw.circle(self.image, (255, 240, 100), (self.size//2, self.size//2), self.size//2 - 3)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.collected = False
        self.anim_timer = 0
    
    def update(self):
        self.anim_timer += 1
    
    def draw(self, surface, camera_x):
        if self.collected:
            return
        offset = 0 if (self.anim_timer // 20) % 2 == 0 else -3
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y + offset))


class BananaPeel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 24
        self.height = 24
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.arc(self.image, CRAZY_YELLOW, (2, 8, 20, 16), 0, 3.14, 6)
        pygame.draw.line(self.image, (200, 200, 100), (4, 16), (20, 16), 4)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.collected = False
        self.anim_timer = 0
    
    def update(self):
        self.anim_timer += 1
    
    def draw(self, surface, camera_x):
        if self.collected:
            return
        wobble = 0 if (self.anim_timer // 10) % 2 == 0 else -2
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y + wobble))


class Fruit(pygame.sprite.Sprite):
    def __init__(self, x, y, fruit_type=0):
        super().__init__()
        self.size = 20
        self.fruit_type = fruit_type
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        if fruit_type == 0:
            pygame.draw.circle(self.image, FRUIT_RED, (self.size//2, self.size//2), self.size//2)
            pygame.draw.circle(self.image, WHITE, (self.size//2 - 3, self.size//2 - 3), 3)
        elif fruit_type == 1:
            pygame.draw.circle(self.image, FRUIT_ORANGE, (self.size//2, self.size//2), self.size//2)
            pygame.draw.circle(self.image, (200, 100, 0), (self.size//2, self.size//2), 4)
        else:
            pygame.draw.circle(self.image, FRUIT_GREEN, (self.size//2, self.size//2), self.size//2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.collected = False
        self.anim_timer = 0
        self.start_y = y
    
    def update(self):
        self.anim_timer += 1
    
    def draw(self, surface, camera_x):
        if self.collected:
            return
        wobble = int(3 * (self.anim_timer % 30) / 15) - 3 if (self.anim_timer // 15) % 2 == 0 else 0
        surface.blit(self.image, (self.rect.x - camera_x, self.start_y + wobble))


class Bat(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 24
        self.height = 20
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BAT_BLACK, (self.width//2, self.height//2), 6)
        pygame.draw.polygon(self.image, BAT_BLACK, [(0, 0), (8, self.height//2), (0, self.height)])
        pygame.draw.polygon(self.image, BAT_BLACK, [(self.width, 0), (self.width - 8, self.height//2), (self.width, self.height)])
        pygame.draw.circle(self.image, WHITE, (self.width//2 - 3, self.height//2 - 2), 2)
        pygame.draw.circle(self.image, WHITE, (self.width//2 + 3, self.height//2 - 2), 2)
        pygame.draw.circle(self.image, BLACK, (self.width//2 - 3, self.height//2 - 2), 1)
        pygame.draw.circle(self.image, BLACK, (self.width//2 + 3, self.height//2 - 2), 1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_x = x
        self.start_y = y
        self.alive = True
        self.timer = 0
        self.angle = 0
    
    def update(self):
        if not self.alive:
            return
        self.timer += 1
        self.angle += 0.1
        self.rect.x = self.start_x + int(30 * self.angle)
        self.rect.y = self.start_y + int(20 * (self.angle % (2 * 3.14159)))
        if self.angle > 100:
            self.angle = 0
    
    def draw(self, surface, camera_x):
        if not self.alive:
            return
        draw_x = self.rect.x - camera_x
        img = self.image.copy()
        wing_offset = int(5 * abs(self.angle % 6.28 - 3.14) / 3.14) - 5
        pygame.draw.polygon(img, BAT_BLACK, [(0, wing_offset), (8, self.height//2), (0, self.height - wing_offset)])
        pygame.draw.polygon(img, BAT_BLACK, [(self.width, wing_offset), (self.width - 8, self.height//2), (self.width, self.height - wing_offset)])
        surface.blit(img, (draw_x, self.rect.y))


class MovingPlatform:
    def __init__(self, x, y, width=3):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, width * TILE_SIZE, TILE_SIZE // 2)
        self.start_x = self.rect.x
        self.start_y = self.rect.y
        self.type = TILE_PLATFORM_MOVING
        self.direction = 1
        self.speed = 2
        self.move_distance = 64
    
    def update(self):
        self.rect.x += self.speed * self.direction
        if abs(self.rect.x - self.start_x) > self.move_distance:
            self.direction *= -1
    
    def draw(self, surface, camera_x):
        draw_x = self.rect.x - camera_x
        pygame.draw.rect(surface, PLATFORM_BLUE, (draw_x, self.rect.y, self.rect.width, self.rect.height))
        pygame.draw.rect(surface, (100, 150, 200), (draw_x, self.rect.y, self.rect.width, 4))
        pygame.draw.circle(surface, (150, 180, 220), (draw_x + 8, self.rect.y + self.rect.height // 2), 4)
        pygame.draw.circle(surface, (150, 180, 220), (draw_x + self.rect.width - 8, self.rect.y + self.rect.height // 2), 4)


class SpikeTrap(pygame.sprite.Sprite):
    def __init__(self, x, y, trap_type=0):
        super().__init__()
        self.trap_type = trap_type
        self.width = 32
        self.height = 32
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        if trap_type == 0:
            for i in range(4):
                offset = i * 8
                pygame.draw.polygon(self.image, SPIKE_GRAY, [(offset, self.height), (offset + 4, 0), (offset + 8, self.height)])
        elif trap_type == 1:
            pygame.draw.circle(self.image, TRAP_RED, (self.width//2, self.height//2), 14)
            pygame.draw.circle(self.image, TRAP_DARK, (self.width//2, self.height//2), 10)
            pygame.draw.circle(self.image, ANGRY_RED, (self.width//2, self.height//2), 6)
        else:
            pygame.draw.circle(self.image, TRAP_ORANGE, (self.width//2, self.height//2), 14)
            pygame.draw.line(self.image, TRAP_DARK, (4, 4), (self.width-4, self.height-4), 3)
            pygame.draw.line(self.image, TRAP_DARK, (self.width-4, 4), (4, self.height-4), 3)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.timer = 0
    
    def update(self):
        self.timer += 1
    
    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class FallingSpike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 24
        self.height = 24
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, TRAP_RED, [(0, self.height), (self.width//2, 0), (self.width, self.height)])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_y = y
        self.falling = False
        self.timer = 0
        self.triggered = False
    
    def update(self):
        self.timer += 1
        if not self.triggered and self.timer > 60:
            self.triggered = True
            self.falling = True
        if self.falling:
            self.rect.y += 8
            if self.rect.y > SCREEN_HEIGHT + 100:
                self.rect.y = self.start_y
                self.falling = False
                self.triggered = False
                self.timer = 0
    
    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class Tile:
    def __init__(self, x, y, tile_type):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.type = tile_type
    
    def draw(self, surface, camera_x):
        draw_x = self.rect.x - camera_x
        if draw_x + TILE_SIZE < 0 or draw_x > SCREEN_WIDTH:
            return
        
        if self.type == TILE_GROUND:
            pygame.draw.rect(surface, GROUND_BROWN, (draw_x, self.rect.y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(surface, (100, 50, 10), (draw_x, self.rect.y, TILE_SIZE, 4))
        elif self.type == TILE_BLOCK:
            pygame.draw.rect(surface, BRICK_COLOR, (draw_x, self.rect.y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(surface, (150, 100, 70), (draw_x, self.rect.y, TILE_SIZE, 2))
            pygame.draw.line(surface, BLACK, (draw_x, self.rect.y + TILE_SIZE//2), (draw_x + TILE_SIZE, self.rect.y + TILE_SIZE//2), 1)
        elif self.type == TILE_PIPE:
            pygame.draw.rect(surface, PIPE_GREEN, (draw_x, self.rect.y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(surface, (20, 130, 50), (draw_x + 4, self.rect.y + 4, TILE_SIZE - 8, TILE_SIZE - 4))
        elif self.type == TILE_PIPE_TOP:
            pygame.draw.rect(surface, PIPE_GREEN, (draw_x, self.rect.y, TILE_SIZE, TILE_SIZE//2))
            pygame.draw.rect(surface, (20, 130, 50), (draw_x + 4, self.rect.y + 4, TILE_SIZE - 8, TILE_SIZE//2 - 4))
        elif self.type == TILE_SPIKE:
            points = [(draw_x, self.rect.y + TILE_SIZE), (draw_x + TILE_SIZE // 2, self.rect.y), (draw_x + TILE_SIZE, self.rect.y + TILE_SIZE)]
            pygame.draw.polygon(surface, SPIKE_GRAY, points)
        elif self.type == TILE_SPIKE_UP:
            points = [(draw_x, self.rect.y), (draw_x + TILE_SIZE // 2, self.rect.y + TILE_SIZE), (draw_x + TILE_SIZE, self.rect.y)]
            pygame.draw.polygon(surface, ANGRY_RED, points)
        elif self.type == TILE_FLAG:
            pygame.draw.rect(surface, FLAG_POLE, (draw_x + 14, self.rect.y, 4, TILE_SIZE))
            pygame.draw.polygon(surface, FLAG_RED, [(draw_x + 18, self.rect.y), (draw_x + 30, self.rect.y + 8), (draw_x + 18, self.rect.y + 16)])


def generate_random_level(level_num, width_tiles=60):
    level_width = width_tiles
    ground_row = 14
    map_data = [[0] * level_width for _ in range(18)]
    
    sky_color = [(107, 140, 255), (100, 130, 230), (80, 100, 200)][(level_num - 1) % 3]
    
    for col in range(level_width):
        map_data[ground_row][col] = TILE_GROUND
        map_data[ground_row + 1][col] = TILE_GROUND
    
    segment_width = (level_width - 10) // 5
    for seg in range(5):
        seg_start = 3 + seg * segment_width
        pit_col = seg_start + random.randint(2, segment_width - 2)
        pit_width = random.randint(1, 2)
        for p in range(pit_width):
            if pit_col + p < level_width - 3:
                map_data[ground_row][pit_col + p] = TILE_EMPTY
                map_data[ground_row + 1][pit_col + p] = TILE_EMPTY
    
    pipe_positions = []
    for _ in range(4 + level_num):
        pipe_col = random.randint(8, level_width - 8)
        pipe_height = random.randint(1, 2) if level_num == 1 else random.randint(2, 3)
        if level_num >= 2 and random.random() < 0.3:
            pipe_height = 4
        pipe_positions.append((pipe_col, pipe_height))
    
    for pipe_col, pipe_height in pipe_positions:
        for h in range(pipe_height):
            if ground_row - h >= 0:
                if h == 0:
                    map_data[ground_row - h][pipe_col] = TILE_PIPE_TOP
                else:
                    map_data[ground_row - h][pipe_col] = TILE_PIPE
    
    for _ in range(6 + level_num * 2):
        plat_col = random.randint(4, level_width - 6)
        plat_width = random.randint(2, 3)
        plat_row = random.randint(9, 12)
        for w in range(plat_width):
            if plat_col + w < level_width - 3:
                if map_data[plat_row][plat_col + w] == 0:
                    map_data[plat_row][plat_col + w] = TILE_BLOCK
    
    for col in range(4, level_width - 4):
        if random.random() < 0.08 and map_data[ground_row][col] == TILE_GROUND:
            has_pipe = any(abs(col - pc) <= 1 for pc, _ in pipe_positions)
            if not has_pipe and col > 3:
                map_data[ground_row][col] = TILE_SPIKE_UP
    
    coin_positions = []
    for _ in range(10 + level_num * 2):
        coin_col = random.randint(2, level_width - 3)
        coin_row = random.randint(11, 13)
        coin_positions.append((coin_col, coin_row))
    
    enemy_positions = []
    for _ in range(6 + level_num * 2):
        valid = False
        attempts = 0
        while not valid and attempts < 20:
            enemy_col = random.randint(5, level_width - 5)
            enemy_row = ground_row - 1
            if map_data[ground_row][enemy_col] != TILE_EMPTY:
                valid = True
                enemy_positions.append((enemy_col, enemy_row))
            attempts += 1
        if not valid:
            enemy_positions.append((random.randint(8, level_width - 8), ground_row - 1))
    
    banana_peels = []
    for _ in range(random.randint(2, 5)):
        peel_col = random.randint(4, level_width - 4)
        if map_data[ground_row][peel_col] == TILE_GROUND:
            banana_peels.append((peel_col, ground_row - 1))
    
    fruit_positions = []
    for _ in range(random.randint(3, 6)):
        fruit_col = random.randint(5, level_width - 5)
        fruit_row = random.randint(4, 10)
        if map_data[fruit_row][fruit_col] == 0:
            fruit_positions.append((fruit_col, fruit_row, random.randint(0, 2)))
    
    bat_positions = []
    for _ in range(random.randint(1, 3)):
        bat_positions.append((random.randint(10, level_width - 15) * TILE_SIZE, random.randint(3, 7) * TILE_SIZE))
    
    moving_platforms = []
    for _ in range(random.randint(2, 4)):
        moving_platforms.append((random.randint(8, level_width - 10), random.randint(7, 11), random.randint(2, 3)))
    
    trap_positions = []
    for _ in range(random.randint(3, 6 + level_num)):
        trap_col = random.randint(6, level_width - 6)
        trap_row = random.randint(3, 12)
        trap_positions.append((trap_col * TILE_SIZE, trap_row * TILE_SIZE, random.randint(0, 2)))
    
    falling_spikes = []
    for _ in range(random.randint(2, 4 + level_num)):
        fall_col = random.randint(8, level_width - 8)
        falling_spikes.append((fall_col * TILE_SIZE, -50))
    
    return {
        "name": f"Level {level_num}",
        "sky_color": sky_color,
        "map": map_data,
        "coins": coin_positions,
        "enemies": enemy_positions,
        "banana_peels": banana_peels,
        "fruits": fruit_positions,
        "bats": bat_positions,
        "moving_platforms": moving_platforms,
        "traps": trap_positions,
        "falling_spikes": falling_spikes,
        "flag_x": level_width - 3,
    }


LEVELS = {
    1: generate_random_level(1, 60),
    2: generate_random_level(2, 80),
    3: generate_random_level(3, 100),
}


class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        self.data = LEVELS[level_num]
        self.name = self.data["name"]
        self.sky_color = self.data["sky_color"]
        
        self.tiles = []
        self.coins = []
        self.enemies = []
        self.fruits = []
        self.bats = []
        self.moving_platforms = []
        self.traps = []
        self.falling_spikes = []
        self.flag_x = self.data["flag_x"] * TILE_SIZE
        
        self.load_level()
    
    def load_level(self):
        self.tile_rects = []
        
        for row_idx, row in enumerate(self.data["map"]):
            for col_idx, tile_type in enumerate(row):
                if tile_type != TILE_EMPTY:
                    tile = Tile(col_idx, row_idx, tile_type)
                    self.tiles.append(tile)
                    self.tile_rects.append(tile)
        
        for x, y in self.data["coins"]:
            self.coins.append(Coin(x * TILE_SIZE, y * TILE_SIZE))
        
        for x, y in self.data.get("banana_peels", []):
            self.coins.append(BananaPeel(x * TILE_SIZE, y * TILE_SIZE))
        
        for x, y, ftype in self.data.get("fruits", []):
            self.fruits.append(Fruit(x * TILE_SIZE, y * TILE_SIZE, ftype))
        
        for x, y in self.data.get("bats", []):
            self.bats.append(Bat(x, y))
        
        for x, y, w in self.data.get("moving_platforms", []):
            self.moving_platforms.append(MovingPlatform(x, y, w))
        
        for x, y, ttype in self.data.get("traps", []):
            self.traps.append(SpikeTrap(x, y, ttype))
        
        for x, y in self.data.get("falling_spikes", []):
            self.falling_spikes.append(FallingSpike(x, y))
        
        for x, y in self.data["enemies"]:
            enemy_type = random.randint(1, 10 + self.level_num * 2)
            if enemy_type <= 3:
                self.enemies.append(Goomba(x * TILE_SIZE, y * TILE_SIZE))
            elif enemy_type <= 5:
                self.enemies.append(AngryGoomba(x * TILE_SIZE, y * TILE_SIZE))
            else:
                self.enemies.append(CrazyKoopa(x * TILE_SIZE, y * TILE_SIZE))
        
        self.flag_x = self.data["flag_x"] * TILE_SIZE
    
    def update(self):
        for coin in self.coins:
            coin.update()
        for fruit in self.fruits:
            fruit.update()
        for bat in self.bats:
            bat.update()
        for platform in self.moving_platforms:
            platform.update()
        for trap in self.traps:
            trap.update()
        for spike in self.falling_spikes:
            spike.update()
        for enemy in self.enemies:
            enemy.update(self.tile_rects)
    
    def draw(self, surface, camera_x):
        for tile in self.tiles:
            tile.draw(surface, camera_x)
        
        for platform in self.moving_platforms:
            platform.draw(surface, camera_x)
        
        for coin in self.coins:
            coin.draw(surface, camera_x)
        
        for fruit in self.fruits:
            fruit.draw(surface, camera_x)
        
        for bat in self.bats:
            bat.draw(surface, camera_x)
        
        for trap in self.traps:
            trap.draw(surface, camera_x)
        
        for spike in self.falling_spikes:
            spike.draw(surface, camera_x)
        
        for enemy in self.enemies:
            enemy.draw(surface, camera_x)
        
        draw_flag_x = self.flag_x - camera_x
        if 0 < draw_flag_x < SCREEN_WIDTH:
            pygame.draw.rect(surface, FLAG_POLE, (draw_flag_x + 14, 10 * TILE_SIZE, 4, 6 * TILE_SIZE))
            pygame.draw.polygon(surface, FLAG_RED, [(draw_flag_x + 18, 10 * TILE_SIZE), (draw_flag_x + 40, 10 * TILE_SIZE + 12), (draw_flag_x + 18, 10 * TILE_SIZE + 24)])


class MusicPlayer:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.available = True
        except:
            self.available = False
    
    def _generate_tone(self, freq, duration, volume=0.3):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        waveform = array.array('h', [0] * n_samples)
        for i in range(n_samples):
            t = i / sample_rate
            envelope = min(1.0, (n_samples - i) / (sample_rate * 0.02))
            sample = int(envelope * volume * 32767 * 0.5)
            waveform[i] = sample if i % 2 == 0 else -sample
        return pygame.sndarray.make_sound(waveform)
    
    def play_jump(self):
        if not self.available:
            return
        try:
            for freq in [200, 300, 400]:
                sound = self._generate_tone(freq, 0.05, 0.2)
                pygame.mixer.Sound.play(sound)
                pygame.time.wait(30)
        except:
            pass
    
    def play_coin(self):
        if not self.available:
            return
        try:
            for freq in [523, 659, 784]:
                sound = self._generate_tone(freq, 0.08, 0.25)
                pygame.mixer.Sound.play(sound)
                pygame.time.wait(60)
        except:
            pass
    
    def play_enemy_stomp(self):
        if not self.available:
            return
        try:
            for freq in [300, 200, 150]:
                sound = self._generate_tone(freq, 0.1, 0.3)
                pygame.mixer.Sound.play(sound)
                pygame.time.wait(80)
        except:
            pass
    
    def play_death(self):
        if not self.available:
            return
        try:
            for freq in [400, 350, 300, 250, 200]:
                sound = self._generate_tone(freq, 0.15, 0.3)
                pygame.mixer.Sound.play(sound)
                pygame.time.wait(100)
        except:
            pass
    
    def play_level_complete(self):
        if not self.available:
            return
        try:
            notes = [523, 587, 659, 698, 784, 880, 988, 1047]
            for freq in notes:
                sound = self._generate_tone(freq, 0.15, 0.25)
                pygame.mixer.Sound.play(sound)
                pygame.time.wait(120)
        except:
            pass
    
    def play_game_over(self):
        if not self.available:
            return
        try:
            notes = [400, 350, 300, 250, 200, 150]
            for freq in notes:
                sound = self._generate_tone(freq, 0.2, 0.3)
                pygame.mixer.Sound.play(sound)
                pygame.time.wait(150)
        except:
            pass
    
    def play_win(self):
        if not self.available:
            return
        try:
            notes = [523, 659, 784, 1047, 784, 659, 523]
            for freq in notes:
                sound = self._generate_tone(freq, 0.2, 0.25)
                pygame.mixer.Sound.play(sound)
                pygame.time.wait(150)
        except:
            pass


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("I Wanna Be The Guy - Platformer!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        
        self.current_level = 1
        self.max_levels = 3
        
        self.music = MusicPlayer()
        
        self.reset_game()
    
    def reset_game(self):
        self.level = Level(self.current_level)
        self.player = Player(100, 10 * TILE_SIZE)
        self.camera_x = 0
        self.state = STATE_PLAYING
        self.level_width = len(self.level.data["map"][0]) * TILE_SIZE
    
    def reset_full_game(self):
        global LEVELS
        LEVELS = {
            1: generate_random_level(1, 60),
            2: generate_random_level(2, 80),
            3: generate_random_level(3, 100),
        }
        self.current_level = 1
        self.reset_game()
    
    def next_level(self):
        if self.current_level < self.max_levels:
            self.current_level += 1
            LEVELS[self.current_level] = generate_random_level(self.current_level, 60 + (self.current_level - 1) * 20)
            self.reset_game()
            self.music.play_level_complete()
        else:
            self.state = STATE_WIN
            self.music.play_win()
    
    def update(self):
        if self.state != STATE_PLAYING:
            return
        
        keys = pygame.key.get_pressed()
        
        self.player.update(keys, self.level.tile_rects, self.level.moving_platforms)
        
        target_camera_x = self.player.rect.x - SCREEN_WIDTH // 3
        self.camera_x = max(0, min(target_camera_x, self.level_width - SCREEN_WIDTH))
        
        self.level.update()
        
        for coin in self.level.coins:
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
                self.player.score += 50 if not hasattr(coin, 'anim_timer') else 100
                self.music.play_coin()
        
        for fruit in self.level.fruits:
            if not fruit.collected and self.player.rect.colliderect(fruit.rect):
                fruit.collected = True
                self.player.score += 150
                self.music.play_coin()
        
        for enemy in self.level.enemies:
            if not enemy.alive:
                continue
            if self.player.rect.colliderect(enemy.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < enemy.rect.centery + 10:
                    enemy.alive = False
                    self.player.vel_y = JUMP_FORCE // 2
                    self.player.score += 200
                    self.music.play_enemy_stomp()
                else:
                    self.player_died()
        
        for bat in self.level.bats:
            if bat.alive and self.player.rect.colliderect(bat.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < bat.rect.centery:
                    bat.alive = False
                    self.player.vel_y = JUMP_FORCE // 2
                    self.player.score += 250
                    self.music.play_enemy_stomp()
                else:
                    self.player_died()
        
        for tile in self.level.tiles:
            if tile.type in (TILE_SPIKE, TILE_SPIKE_UP) and self.player.rect.colliderect(tile.rect):
                self.player_died()
        
        for trap in self.level.traps:
            if self.player.rect.colliderect(trap.rect):
                self.player_died()
        
        for spike in self.level.falling_spikes:
            if self.player.rect.colliderect(spike.rect):
                self.player_died()
        
        if self.player.rect.y > SCREEN_HEIGHT:
            self.player_died()
        
        if self.player.rect.x >= self.level.flag_x:
            self.player.score += 1000
            self.next_level()
    
    def player_died(self):
        self.music.play_death()
        self.player.lives -= 1
        if self.player.lives <= 0:
            self.state = STATE_GAME_OVER
            self.music.play_game_over()
        else:
            self.player.rect.x = 100
            self.player.rect.y = 10 * TILE_SIZE
            self.player.vel_x = 0
            self.player.vel_y = 0
            self.camera_x = 0
    
    def draw(self):
        self.screen.fill(self.level.sky_color)
        
        self.level.draw(self.screen, self.camera_x)
        
        self.player.draw(self.screen, self.camera_x)
        
        score_text = self.font.render(f"Score: {self.player.score}", True, TEXT_COLOR)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, TEXT_COLOR)
        level_text = self.font.render(f"Level {self.current_level}: {self.level.name}", True, TEXT_COLOR)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 100, 10))
        
        controls_text = self.small_font.render("ARROWS: Move | SPACE: Jump | P: Pause | R: Restart", True, BLACK)
        self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))
        
        if self.state == STATE_PAUSED:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            text = self.large_font.render("PAUSED", True, WHITE)
            self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30)))
            resume_text = self.font.render("Press P to Resume", True, WHITE)
            self.screen.blit(resume_text, resume_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))
        
        elif self.state == STATE_GAME_OVER:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            text = self.large_font.render("GAME OVER", True, WHITE)
            self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
            restart_text = self.font.render("Press R to Restart", True, WHITE)
            self.screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)))
        
        elif self.state == STATE_WIN:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            text = self.large_font.render("YOU WIN!", True, COIN_GOLD)
            self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
            score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
            self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))
            restart_text = self.font.render("Press R to Play Again", True, WHITE)
            self.screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70)))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        space_pressed = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p and self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                    elif event.key == pygame.K_p and self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING
                    elif event.key == pygame.K_r and self.state in (STATE_GAME_OVER, STATE_WIN):
                        self.reset_full_game()
                    elif event.key in (pygame.K_SPACE, pygame.K_w):
                        if self.state == STATE_PLAYING and self.player.on_ground and not space_pressed:
                            self.music.play_jump()
                            space_pressed = True
            
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_SPACE, pygame.K_w):
                    space_pressed = False
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
