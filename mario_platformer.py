"""
SUPAR MAYRO - Ultimate Platformer
Boss battles, weapons, double jump, and more!
"""

import pygame
import sys
import random
import math
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
COIN_GOLD = (255, 215, 0)
SPIKE_GRAY = (128, 128, 128)
TEXT_COLOR = (255, 255, 255)
FLAG_RED = (220, 20, 60)
FLAG_POLE = (200, 200, 200)
PLATFORM_BLUE = (70, 130, 180)
TRAP_RED = (200, 0, 0)
ANGRY_RED = (255, 0, 0)
CRAZY_YELLOW = (255, 255, 0)

SKIN_COLOR = (230, 175, 79)  # #E6AF4F - Golden skin tone
HAIR_COLOR = (100, 50, 0)
SHIRT_COLOR = (50, 150, 250)
PANTS_COLOR = (30, 30, 180)
ENEMY_BROWN = (160, 100, 50)
ENEMY_GREEN = (50, 150, 50)
ENEMY_PURPLE = (150, 50, 150)
ENEMY_ORANGE = (255, 140, 0)
ENEMY_RED = (200, 50, 50)
ENEMY_CYAN = (50, 200, 200)
BAT_BLACK = (30, 30, 30)
BOSS_DARK = (50, 0, 0)
GHOST_WHITE = (220, 220, 240)
SLIME_GREEN = (50, 255, 100)
FIRE_ORANGE = (255, 100, 0)
ICE_CYAN = (150, 255, 255)
TELEPORTER_PURPLE = (180, 50, 255)
THIEF_BLUE = (50, 100, 255)
ANNOYING_PINK = (255, 100, 200)
SHIELDER_GRAY = (100, 100, 120)

GRAVITY = 0.7
JUMP_FORCE = -13
PLAYER_SPEED = 5
ENEMY_SPEED = 2
MAX_FALL_SPEED = 12
DOUBLE_JUMP_FORCE = -11

TILE_EMPTY = 0
TILE_GROUND = 1
TILE_BLOCK = 2
TILE_PIPE = 3
TILE_PIPE_TOP = 4
TILE_SPIKE = 5
TILE_FLAG = 6
TILE_SPIKE_UP = 7
TILE_PLATFORM_MOVING = 8
TILE_BOSS_DOOR = 9

STATE_PLAYING = 0
STATE_GAME_OVER = 1
STATE_WIN = 2
STATE_PAUSED = 3
STATE_BOSS = 4
STATE_CHAT = 5


class Player:
    def __init__(self, x, y):
        self.width = 24
        self.height = 32
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.can_double_jump = False
        self.jumps_left = 2
        
        self.lives = 5
        self.score = 0
        self.alive = True
        
        self.has_weapon = True
        self.weapon_type = 0
        self.shoot_cooldown = 0
        self.bullets = []
        
        self.anim_frame = 0
        self.anim_timer = 0
    
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
        
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and not getattr(self, 'jump_held', False):
            if self.on_ground:
                self.vel_y = JUMP_FORCE
                self.on_ground = False
                self.can_double_jump = True
                self.jumps_left = 1
            elif self.can_double_jump and self.jumps_left > 0:
                self.vel_y = DOUBLE_JUMP_FORCE
                self.jumps_left -= 1
                self.can_double_jump = False
        
        if not (keys[pygame.K_SPACE] or keys[pygame.K_w]):
            self.jump_held = False
        else:
            self.jump_held = True
        
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
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.right < 0 or bullet.rect.left > 4000:
                self.bullets.remove(bullet)
        
        self.anim_timer += 1
        if self.anim_timer > 8:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
    
    def shoot(self):
        if self.shoot_cooldown == 0 and self.has_weapon:
            direction = 1 if self.facing_right else -1
            bullet = Bullet(self.rect.centerx, self.rect.centery, direction)
            self.bullets.append(bullet)
            self.shoot_cooldown = 15
    
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
        if not self.alive:
            return
        
        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y
        
        head_y = draw_y
        body_y = draw_y + 12
        leg_offset = 0
        
        if self.vel_x != 0 and self.on_ground:
            leg_offset = [0, 3, 0, -3][self.anim_frame]
        
        pygame.draw.ellipse(surface, SKIN_COLOR, (draw_x + 4, head_y, 16, 12))
        pygame.draw.ellipse(surface, HAIR_COLOR, (draw_x + 2, head_y - 2, 20, 8))
        
        eye_x = draw_x + 14 if self.facing_right else draw_x + 6
        pygame.draw.circle(surface, BLACK, (eye_x, head_y + 5), 2)
        
        pygame.draw.rect(surface, SHIRT_COLOR, (draw_x + 2, body_y, 20, 12))
        pygame.draw.rect(surface, (40, 120, 200), (draw_x + 4, body_y + 2, 6, 8))
        pygame.draw.rect(surface, (40, 120, 200), (draw_x + 14, body_y + 2, 6, 8))
        
        pygame.draw.rect(surface, PANTS_COLOR, (draw_x + 4, body_y + 12, 6, 8 + leg_offset))
        pygame.draw.rect(surface, PANTS_COLOR, (draw_x + 14, body_y + 12, 6, 8 - leg_offset))
        
        pygame.draw.rect(surface, (100, 50, 50), (draw_x - 2, body_y + 2, 4, 10))
        
        for bullet in self.bullets:
            bullet.draw(surface, camera_x)


class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y - 4, 12, 8)
        self.direction = direction
        self.speed = 10
    
    def update(self):
        self.rect.x += self.speed * self.direction
    
    def draw(self, surface, camera_x):
        pygame.draw.ellipse(surface, CRAZY_YELLOW, (self.rect.x - camera_x, self.rect.y, 12, 8))


class Enemy:
    def __init__(self, x, y, enemy_type=0):
        self.type = enemy_type
        self.width = 28
        self.height = 28
        
        if enemy_type == 0:
            self.color = ENEMY_BROWN
        elif enemy_type == 1:
            self.color = ENEMY_GREEN
        elif enemy_type == 2:
            self.color = ENEMY_PURPLE
        elif enemy_type == 3:
            self.color = ENEMY_ORANGE
        elif enemy_type == 4:
            self.color = ENEMY_RED
        else:
            self.color = ENEMY_CYAN
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_x = ENEMY_SPEED
        self.vel_y = 0
        self.direction = 1
        self.on_ground = False
        self.alive = True
        
        self.rage_timer = 0
        self.spin_timer = 0
    
    def update(self, tiles):
        if not self.alive:
            return
        
        if self.type == 2:
            self.rage_timer += 1
            if self.rage_timer > 60:
                self.vel_x = ENEMY_SPEED * 2.5
                self.rage_timer = 0
        
        if self.type == 3:
            self.spin_timer += 1
            if self.spin_timer > 90:
                self.spin_timer = 0
                self.vel_x = ENEMY_SPEED * 3 if self.vel_x < ENEMY_SPEED * 2 else ENEMY_SPEED
        
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
        
        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y
        
        pygame.draw.ellipse(surface, self.color, (draw_x, draw_y, self.width, self.height))
        
        eye_offset = 4 if self.direction > 0 else -4
        pygame.draw.circle(surface, WHITE, (draw_x + 8 + eye_offset, draw_y + 8), 4)
        pygame.draw.circle(surface, WHITE, (draw_x + 20 + eye_offset, draw_y + 8), 4)
        pygame.draw.circle(surface, BLACK, (draw_x + 8 + eye_offset, draw_y + 8), 2)
        pygame.draw.circle(surface, BLACK, (draw_x + 20 + eye_offset, draw_y + 8), 2)
        
        if self.type == 2:
            pygame.draw.line(surface, ANGRY_RED, (draw_x + 4, draw_y + 4), (draw_x + 12, draw_y + 8), 2)
            pygame.draw.line(surface, ANGRY_RED, (draw_x + 16, draw_y + 8), (draw_x + 24, draw_y + 4), 2)


class Ghost:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 32)
        self.start_x = x
        self.start_y = y
        self.alive = True
        self.timer = 0
        self.phase = 0
        self.speed = 1.5
    
    def update(self, player_rect):
        if not self.alive:
            return
        self.timer += 1
        
        if player_rect:
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = max(1, math.sqrt(dx*dx + dy*dy))
            if dist < 200:
                self.rect.x += (dx / dist) * self.speed
                self.rect.y += (dy / dist) * self.speed
        
        self.phase = (self.timer // 10) % 2
    
    def draw(self, surface, camera_x):
        if not self.alive:
            return
        draw_x = self.rect.x - camera_x
        
        body_color = GHOST_WHITE if self.phase == 0 else (200, 200, 220)
        pygame.draw.ellipse(surface, body_color, (draw_x, self.rect.y, 28, 32))
        pygame.draw.circle(surface, BLACK, (draw_x + 8, self.rect.y + 12), 4)
        pygame.draw.circle(surface, BLACK, (draw_x + 20, self.rect.y + 12), 4)
        pygame.draw.ellipse(surface, BLACK, (draw_x + 10, self.rect.y + 20, 8, 6))


class Slime:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 24)
        self.start_y = y
        self.alive = True
        self.timer = 0
        self.jump_timer = 0
        self.vel_x = 1
        self.vel_y = 0
        self.direction = 1
    
    def update(self, tiles):
        if not self.alive:
            return
        self.timer += 1
        
        if self.timer % 90 == 0:
            self.vel_y = -8
            self.direction *= -1
        
        self.vel_x = self.direction * 1.5
        self.vel_y += 0.3
        
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        for tile in tiles:
            if tile.type in (TILE_GROUND, TILE_BLOCK, TILE_PIPE, TILE_PIPE_TOP):
                if self.rect.colliderect(tile.rect):
                    if self.vel_y > 0:
                        self.rect.bottom = tile.rect.top
                        self.vel_y = 0
                    elif self.vel_x > 0:
                        self.rect.right = tile.rect.left
                        self.direction = -1
                    elif self.vel_x < 0:
                        self.rect.left = tile.rect.right
                        self.direction = 1
    
    def draw(self, surface, camera_x):
        if not self.alive:
            return
        draw_x = self.rect.x - camera_x
        wobble = int(4 * abs((self.timer % 20) / 10 - 1))
        
        pygame.draw.ellipse(surface, SLIME_GREEN, (draw_x, self.rect.y + wobble, 32, 24 - wobble))
        pygame.draw.circle(surface, (30, 150, 60), (draw_x + 8, self.rect.y + 8), 3)
        pygame.draw.circle(surface, (30, 150, 60), (draw_x + 24, self.rect.y + 8), 3)


class Teleporter:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 28)
        self.start_pos = (x, y)
        self.alive = True
        self.timer = 0
        self.teleport_timer = 0
        self.visible = True
        self.scale = 1.0
        self.target_x = x
        self.target_y = y
        self.lerp_progress = 0
    
    def update(self, player_rect, tiles):
        if not self.alive:
            return
        self.timer += 1
        
        if self.teleport_timer > 0:
            self.teleport_timer -= 1
            if self.teleport_timer == 15:
                self.visible = False
                self.scale = 0.1
            elif self.teleport_timer == 5:
                if player_rect:
                    offset_x = random.choice([-150, -100, 100, 150])
                    offset_y = random.choice([-80, -40, 40, 80])
                    self.target_x = max(50, min(3800, player_rect.x + offset_x))
                    self.target_y = max(50, min(500, player_rect.y + offset_y))
                else:
                    self.target_x = self.start_pos[0] + random.randint(-100, 100)
                    self.target_y = self.start_pos[1] + random.randint(-50, 50)
            elif self.teleport_timer < 5:
                self.rect.x = self.target_x
                self.rect.y = self.target_y
                self.visible = True
                self.scale = min(1.0, self.scale + 0.2)
        elif self.timer % 120 == 0:
            self.teleport_timer = 20
    
    def draw(self, surface, camera_x):
        if not self.alive:
            return
        if not self.visible:
            return
        draw_x = self.rect.x - camera_x
        size = int(28 * self.scale)
        offset = (28 - size) // 2
        
        pygame.draw.ellipse(surface, TELEPORTER_PURPLE, (draw_x + offset, self.rect.y + offset, size, size))
        if self.scale > 0.7:
            pygame.draw.circle(surface, (100, 255, 100), (draw_x + 10, self.rect.y + 10), 4)
            pygame.draw.circle(surface, (100, 255, 100), (draw_x + 18, self.rect.y + 10), 4)
            pygame.draw.arc(surface, WHITE, (draw_x + 8, self.rect.y + 16, 12, 8), 0, 3.14, 2)


class Thief:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 26, 26)
        self.alive = True
        self.timer = 0
        self.steal_timer = 0
        self.has_stolen = False
        self.velocity_x = 0
        self.velocity_y = 0
        self.angle = 0
    
    def update(self, player_rect, coins):
        if not self.alive:
            return
        self.timer += 1
        self.angle += 0.2
        dist = 1000
        
        if player_rect:
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = max(1, math.sqrt(dx*dx + dy*dy))
            
            if dist < 200 and not self.has_stolen:
                self.velocity_x += (dx / dist) * 0.3
                self.velocity_y += (dy / dist) * 0.3
            elif self.has_stolen:
                self.velocity_x -= (dx / dist) * 0.5
                self.velocity_y -= (dy / dist) * 0.5
        
        self.velocity_x *= 0.95
        self.velocity_y *= 0.95
        
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y + int(3 * math.sin(self.angle))
        
        if self.steal_timer > 0:
            self.steal_timer -= 1
        
        if dist < 40 and self.steal_timer == 0 and not self.has_stolen:
            if coins:
                for coin in coins:
                    if not coin.collected:
                        coin.collected = True
                        self.has_stolen = True
                        self.steal_timer = 180
                        break
        
        if self.has_stolen and self.steal_timer < 150:
            self.has_stolen = False
    
    def draw(self, surface, camera_x):
        if not self.alive:
            return
        draw_x = self.rect.x - camera_x
        wobble = int(2 * math.sin(self.angle * 2))
        
        pygame.draw.ellipse(surface, THIEF_BLUE, (draw_x, self.rect.y + wobble, 26, 26))
        pygame.draw.circle(surface, WHITE, (draw_x + 8, self.rect.y + 8 + wobble), 3)
        pygame.draw.circle(surface, WHITE, (draw_x + 18, self.rect.y + 8 + wobble), 3)
        pygame.draw.circle(surface, BLACK, (draw_x + 8, self.rect.y + 8 + wobble), 1)
        pygame.draw.circle(surface, BLACK, (draw_x + 18, self.rect.y + 8 + wobble), 1)
        
        if self.has_stolen:
            pygame.draw.circle(surface, COIN_GOLD, (draw_x + 13, self.rect.y - 5 + wobble), 5)


class Dodger:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.alive = True
        self.timer = 0
        self.dodge_cooldown = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.dodge_x = 0
        self.dodge_y = 0
        self.dodging = False
        self.trail = []
    
    def update(self, player_rect, bullets):
        if not self.alive:
            return
        self.timer += 1
        
        self.trail.append((self.rect.x, self.rect.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        
        if self.dodge_cooldown > 0:
            self.dodge_cooldown -= 1
        
        if not self.dodging:
            if player_rect:
                target_x = player_rect.x
                self.velocity_x = 1.5 if self.rect.x < target_x else -1.5
        
        for bullet in bullets:
            dx = bullet.rect.centerx - self.rect.centerx
            dy = bullet.rect.centery - self.rect.centery
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < 100 and self.dodge_cooldown == 0 and not self.dodging:
                self.dodging = True
                self.dodge_cooldown = 60
                self.dodge_x = -dy / dist * 8 if dist > 0 else 0
                self.dodge_y = dx / dist * 8 if dist > 0 else 0
                break
        
        if self.dodging:
            self.rect.x += self.dodge_x
            self.rect.y += self.dodge_y
            self.dodge_x *= 0.9
            self.dodge_y *= 0.9
            if abs(self.dodge_x) < 0.5 and abs(self.dodge_y) < 0.5:
                self.dodging = False
        else:
            self.rect.x += self.velocity_x
            self.rect.y += int(2 * math.sin(self.timer * 0.1))
    
    def draw(self, surface, camera_x):
        if not self.alive:
            return
        
        for i, (tx, ty) in enumerate(self.trail):
            alpha = i / len(self.trail)
            size = int(20 * alpha)
            color = (int(ANNOYING_PINK[0] * alpha), int(ANNOYING_PINK[1] * alpha), int(ANNOYING_PINK[2] * alpha))
            offset = (24 - size) // 2
            pygame.draw.ellipse(surface, color, (tx - camera_x + offset, ty + offset, size, size))
        
        draw_x = self.rect.x - camera_x
        pygame.draw.ellipse(surface, ANNOYING_PINK, (draw_x, self.rect.y, 24, 24))
        pygame.draw.circle(surface, (255, 255, 255), (draw_x + 7, self.rect.y + 8), 4)
        pygame.draw.circle(surface, (255, 255, 255), (draw_x + 17, self.rect.y + 8), 4)
        pygame.draw.circle(surface, (0, 0, 0), (draw_x + 8, self.rect.y + 9), 2)
        pygame.draw.circle(surface, (0, 0, 0), (draw_x + 16, self.rect.y + 9), 2)


class Shielder:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.alive = True
        self.timer = 0
        self.pulse = 0
        self.angle = 0
        self.shield_radius = 60
    
    def update(self, enemies, player_rect):
        if not self.alive:
            return
        self.timer += 1
        self.angle += 0.05
        self.pulse = int(5 * math.sin(self.timer * 0.1))
        
        if player_rect:
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = max(1, math.sqrt(dx*dx + dy*dy))
            if dist > 150:
                self.rect.x += (dx / dist) * 0.8
                self.rect.y += (dy / dist) * 0.8
    
    def draw(self, surface, camera_x):
        if not self.alive:
            return
        draw_x = self.rect.x - camera_x
        
        pygame.draw.circle(surface, (150, 150, 200, 100), (draw_x + 16, self.rect.y + 16), self.shield_radius + self.pulse, 3)
        
        for i in range(3):
            angle = self.angle + i * 2.09
            sx = draw_x + 16 + int(40 * math.cos(angle))
            sy = self.rect.y + 16 + int(40 * math.sin(angle))
            pygame.draw.circle(surface, (100, 200, 255), (sx, sy), 6)
        
        pygame.draw.rect(surface, SHIELDER_GRAY, (draw_x + 4, self.rect.y + 4, 24, 24))
        pygame.draw.circle(surface, (100, 255, 100), (draw_x + 12, self.rect.y + 12), 4)
        pygame.draw.circle(surface, (100, 255, 100), (draw_x + 20, self.rect.y + 12), 4)


class Healer:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 26, 30)
        self.alive = True
        self.timer = 0
        self.heal_timer = 0
        self.bob_offset = 0
        self.heal_beams = []
    
    def update(self, enemies):
        if not self.alive:
            return
        self.timer += 1
        self.bob_offset = int(4 * math.sin(self.timer * 0.08))
        
        if self.heal_timer > 0:
            self.heal_timer -= 1
        
        self.heal_beams = []
        if self.heal_timer == 0:
            for enemy in enemies:
                if enemy.alive and enemy != self:
                    dx = enemy.rect.centerx - self.rect.centerx
                    dy = enemy.rect.centery - self.rect.centery
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < 120 and random.random() < 0.02:
                        self.heal_timer = 90
                        self.heal_beams.append((enemy.rect.centerx, enemy.rect.centery))
                        break
    
    def draw(self, surface, camera_x):
        if not self.alive:
            return
        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y + self.bob_offset
        
        for hx, hy in self.heal_beams:
            pygame.draw.line(surface, (100, 255, 100), (draw_x + 13, draw_y + 15), (hx - camera_x, hy), 3)
            pygame.draw.circle(surface, (100, 255, 100), (hx - camera_x, hy), 8)
        
        pygame.draw.ellipse(surface, (50, 200, 100), (draw_x, draw_y, 26, 30))
        pygame.draw.circle(surface, WHITE, (draw_x + 8, draw_y + 10), 4)
        pygame.draw.circle(surface, WHITE, (draw_x + 18, draw_y + 10), 4)
        pygame.draw.line(surface, WHITE, (draw_x + 10, draw_y + 20), (draw_x + 16, draw_y + 20), 2)
        
        plus_pulse = abs(math.sin(self.timer * 0.1))
        plus_size = int(8 + 4 * plus_pulse)
        pygame.draw.line(surface, (255, 255, 255), (draw_x + 13 - plus_size//2, draw_y - 5), (draw_x + 13 + plus_size//2, draw_y - 5), 3)
        pygame.draw.line(surface, (255, 255, 255), (draw_x + 13, draw_y - 5 - plus_size//2), (draw_x + 13, draw_y - 5 + plus_size//2), 3)


class Bat:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 20)
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
        pygame.draw.circle(surface, BAT_BLACK, (draw_x + 12, self.rect.y + 10), 8)
        pygame.draw.polygon(surface, BAT_BLACK, [(draw_x, self.rect.y + 5), (draw_x + 10, self.rect.y + 10), (draw_x, self.rect.y + 15)])
        pygame.draw.polygon(surface, BAT_BLACK, [(draw_x + 24, self.rect.y + 5), (draw_x + 14, self.rect.y + 10), (draw_x + 24, self.rect.y + 15)])
        pygame.draw.circle(surface, WHITE, (draw_x + 10, self.rect.y + 8), 2)
        pygame.draw.circle(surface, WHITE, (draw_x + 14, self.rect.y + 8), 2)


class Boss:
    def __init__(self, x, y, boss_type=0):
        self.type = boss_type
        self.width = 64
        self.height = 80
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_x = 2
        self.vel_y = 0
        self.health = 10
        self.max_health = 10
        self.alive = True
        self.timer = 0
        self.phase = 0
        self.attacks = []
        
        if boss_type == 0:
            self.name = "GOOMBA KING"
            self.color = ENEMY_BROWN
        elif boss_type == 1:
            self.name = "KOOPA COMMANDER"
            self.color = ENEMY_GREEN
        elif boss_type == 2:
            self.name = "DARK MASTER"
            self.color = ENEMY_PURPLE
        else:
            self.name = "DRAGON"
            self.color = ENEMY_RED
    
    def update(self, player_rect, tiles):
        if not self.alive:
            return
        
        self.timer += 1
        
        self.rect.x += self.vel_x
        if self.rect.left < 100 or self.rect.right > 700:
            self.vel_x *= -1
        
        if self.timer % 120 == 0:
            self.phase = (self.phase + 1) % 3
            
            if self.phase == 1:
                attack = Enemy(self.rect.centerx - 12, self.rect.bottom - 30, random.randint(0, 5))
                self.attacks.append(attack)
            
            elif self.phase == 2:
                for i in range(3):
                    attack = Enemy(self.rect.centerx - 12, self.rect.top - 20, random.randint(0, 5))
                    self.attacks.append(attack)
        
        for attack in self.attacks[:]:
            attack.update(tiles)
            if not attack.alive:
                self.attacks.remove(attack)
    
    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.alive = False
    
    def draw(self, surface, camera_x):
        if not self.alive:
            return
        
        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y
        
        pygame.draw.ellipse(surface, self.color, (draw_x, draw_y, self.width, self.height))
        
        pygame.draw.circle(surface, WHITE, (draw_x + 20, draw_y + 25), 8)
        pygame.draw.circle(surface, WHITE, (draw_x + 44, draw_y + 25), 8)
        pygame.draw.circle(surface, BLACK, (draw_x + 20, draw_y + 25), 4)
        pygame.draw.circle(surface, BLACK, (draw_x + 44, draw_y + 25), 4)
        
        mouth_open = (self.timer // 30) % 2 == 0
        if mouth_open:
            pygame.draw.ellipse(surface, BLACK, (draw_x + 24, draw_y + 45, 16, 12))
        else:
            pygame.draw.line(surface, BLACK, (draw_x + 24, draw_y + 50), (draw_x + 40, draw_y + 50), 3)
        
        health_width = 60 * (self.health / self.max_health)
        pygame.draw.rect(surface, (100, 0, 0), (draw_x, draw_y - 15, 64, 8))
        pygame.draw.rect(surface, ANGRY_RED, (draw_x, draw_y - 15, health_width, 8))
        
        for attack in self.attacks:
            attack.draw(surface, camera_x)


class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.collected = False
        self.anim_timer = 0
    
    def update(self):
        self.anim_timer += 1
    
    def draw(self, surface, camera_x):
        if self.collected:
            return
        offset = 0 if (self.anim_timer // 20) % 2 == 0 else -3
        pygame.draw.circle(surface, COIN_GOLD, (self.rect.x - camera_x + 10, self.rect.y + offset + 10), 10)
        pygame.draw.circle(surface, (255, 240, 100), (self.rect.x - camera_x + 10, self.rect.y + offset + 10), 7)


class Fruit:
    def __init__(self, x, y, fruit_type=0):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.fruit_type = fruit_type
        self.collected = False
        self.anim_timer = 0
        self.start_y = y
    
    def update(self):
        self.anim_timer += 1
    
    def draw(self, surface, camera_x):
        if self.collected:
            return
        wobble = int(3 * (self.anim_timer % 30) / 15) - 3 if (self.anim_timer // 15) % 2 == 0 else 0
        colors = [(255, 50, 50), (255, 165, 0), (50, 205, 50)]
        pygame.draw.circle(surface, colors[self.fruit_type], (self.rect.x - camera_x + 10, self.start_y + wobble + 10), 10)


class SpikeTrap:
    def __init__(self, x, y, trap_type=0):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.trap_type = trap_type
    
    def draw(self, surface, camera_x):
        if self.trap_type == 0:
            for i in range(4):
                offset = i * 8
                points = [(self.rect.x - camera_x + offset, self.rect.y + 32),
                         (self.rect.x - camera_x + offset + 4, self.rect.y),
                         (self.rect.x - camera_x + offset + 8, self.rect.y + 32)]
                pygame.draw.polygon(surface, SPIKE_GRAY, points)
        elif self.trap_type == 1:
            pygame.draw.circle(surface, TRAP_RED, (self.rect.x - camera_x + 16, self.rect.y + 16), 14)
            pygame.draw.circle(surface, (50, 0, 0), (self.rect.x - camera_x + 16, self.rect.y + 16), 10)


class FallingSpike:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.start_y = y
        self.falling = False
        self.timer = 0
    
    def update(self):
        self.timer += 1
        if not self.falling and self.timer > 60:
            self.falling = True
        if self.falling:
            self.rect.y += 8
            if self.rect.y > SCREEN_HEIGHT + 100:
                self.rect.y = self.start_y
                self.falling = False
                self.timer = 0
    
    def draw(self, surface, camera_x):
        points = [(self.rect.x - camera_x, self.rect.y + 24),
                 (self.rect.x - camera_x + 12, self.rect.y),
                 (self.rect.x - camera_x + 24, self.rect.y + 24)]
        pygame.draw.polygon(surface, TRAP_RED, points)


class MovingPlatform:
    def __init__(self, x, y, width=3, horizontal=True):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, width * TILE_SIZE, TILE_SIZE // 2)
        self.start_x = self.rect.x
        self.direction = 1
        self.speed = 2
        self.move_distance = 64
    
    def update(self):
        self.rect.x += self.speed * self.direction
        if abs(self.rect.x - self.start_x) > self.move_distance:
            self.direction *= -1
    
    def draw(self, surface, camera_x):
        pygame.draw.rect(surface, PLATFORM_BLUE, (self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height))
        pygame.draw.rect(surface, (100, 150, 200), (self.rect.x - camera_x, self.rect.y, self.rect.width, 4))


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
        elif self.type == TILE_PIPE:
            pygame.draw.rect(surface, PIPE_GREEN, (draw_x, self.rect.y, TILE_SIZE, TILE_SIZE))
        elif self.type == TILE_PIPE_TOP:
            pygame.draw.rect(surface, PIPE_GREEN, (draw_x, self.rect.y, TILE_SIZE, TILE_SIZE // 2))
        elif self.type == TILE_SPIKE:
            points = [(draw_x, self.rect.y + TILE_SIZE), (draw_x + 16, self.rect.y), (draw_x + 32, self.rect.y + TILE_SIZE)]
            pygame.draw.polygon(surface, SPIKE_GRAY, points)
        elif self.type == TILE_SPIKE_UP:
            points = [(draw_x, self.rect.y), (draw_x + 16, self.rect.y + TILE_SIZE), (draw_x + 32, self.rect.y)]
            pygame.draw.polygon(surface, ANGRY_RED, points)
        elif self.type == TILE_FLAG:
            pygame.draw.rect(surface, FLAG_POLE, (draw_x + 14, self.rect.y, 4, TILE_SIZE))
            pygame.draw.polygon(surface, FLAG_RED, [(draw_x + 18, self.rect.y), (draw_x + 30, self.rect.y + 8), (draw_x + 18, self.rect.y + 16)])
        elif self.type == TILE_BOSS_DOOR:
            pygame.draw.rect(surface, BOSS_DARK, (draw_x, self.rect.y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(surface, TRAP_RED, (draw_x + 8, self.rect.y + 8, 16, 16))


def generate_level(level_num, width_tiles=60, is_boss_level=False):
    level_width = width_tiles
    ground_row = 14
    map_data = [[0] * level_width for _ in range(18)]
    
    sky_color = [(107, 140, 255), (100, 130, 230), (80, 100, 200), (60, 60, 80), (80, 60, 60)][(level_num - 1) % 5]
    
    for col in range(level_width):
        map_data[ground_row][col] = TILE_GROUND
        map_data[ground_row + 1][col] = TILE_GROUND
    
    if not is_boss_level:
        for seg in range(5):
            seg_start = 3 + seg * ((level_width - 10) // 5)
            pit_col = seg_start + random.randint(2, 6)
            pit_width = random.randint(1, 2)
            for p in range(pit_width):
                if pit_col + p < level_width - 3:
                    map_data[ground_row][pit_col + p] = TILE_EMPTY
                    map_data[ground_row + 1][pit_col + p] = TILE_EMPTY
    
    for _ in range(3 + level_num):
        pipe_col = random.randint(8, level_width - 8)
        pipe_height = random.randint(2, 3)
        for h in range(pipe_height):
            if ground_row - h >= 0:
                map_data[ground_row - h][pipe_col] = TILE_PIPE_TOP if h == 0 else TILE_PIPE
    
    for _ in range(6 + level_num * 2):
        plat_col = random.randint(4, level_width - 6)
        plat_row = random.randint(9, 12)
        for w in range(random.randint(2, 3)):
            if plat_col + w < level_width - 3 and map_data[plat_row][plat_col + w] == 0:
                map_data[plat_row][plat_col + w] = TILE_BLOCK
    
    for col in range(4, level_width - 4):
        if random.random() < 0.06 and map_data[ground_row][col] == TILE_GROUND:
            map_data[ground_row][col] = TILE_SPIKE_UP
    
    coin_positions = []
    for _ in range(10 + level_num * 2):
        coin_positions.append((random.randint(2, level_width - 3), random.randint(11, 13)))
    
    enemy_positions = []
    for _ in range(8 + level_num * 3):
        enemy_col = random.randint(5, level_width - 5)
        if map_data[ground_row][enemy_col] == TILE_GROUND:
            enemy_positions.append((enemy_col, ground_row - 1, random.randint(0, 5)))
    
    bat_positions = []
    for _ in range(3 + level_num):
        bat_positions.append((random.randint(10, level_width - 15) * TILE_SIZE, random.randint(3, 7) * TILE_SIZE))
    
    moving_platforms = []
    for _ in range(2 + level_num // 2):
        moving_platforms.append((random.randint(8, level_width - 10), random.randint(7, 11), random.randint(2, 3)))
    
    trap_positions = []
    for _ in range(2 + level_num):
        trap_col = random.randint(6, level_width - 6)
        trap_row = random.randint(3, 12)
        trap_positions.append((trap_col * TILE_SIZE, trap_row * TILE_SIZE, random.randint(0, 1)))
    
    falling_spikes = []
    for _ in range(1 + level_num):
        falling_spikes.append((random.randint(8, level_width - 8) * TILE_SIZE, -50))
    
    ghost_positions = []
    for _ in range(2 + level_num):
        ghost_positions.append((random.randint(10, level_width - 15) * TILE_SIZE, random.randint(2, 6) * TILE_SIZE))
    
    slime_positions = []
    for _ in range(2 + level_num):
        slime_col = random.randint(5, level_width - 5)
        if map_data[ground_row][slime_col] == TILE_GROUND:
            slime_positions.append((slime_col * TILE_SIZE, (ground_row - 2) * TILE_SIZE))
    
    teleporter_positions = []
    for _ in range(1 + level_num // 2):
        teleporter_positions.append((random.randint(8, level_width - 10) * TILE_SIZE, random.randint(3, 8) * TILE_SIZE))
    
    thief_positions = []
    for _ in range(1 + level_num // 3):
        thief_positions.append((random.randint(10, level_width - 15) * TILE_SIZE, random.randint(4, 10) * TILE_SIZE))
    
    dodger_positions = []
    for _ in range(2 + level_num // 2):
        dodger_positions.append((random.randint(8, level_width - 10) * TILE_SIZE, random.randint(5, 12) * TILE_SIZE))
    
    shielder_positions = []
    for _ in range(1 + level_num // 3):
        shielder_positions.append((random.randint(12, level_width - 15) * TILE_SIZE, random.randint(6, 11) * TILE_SIZE))
    
    healer_positions = []
    for _ in range(1 + level_num // 4):
        healer_positions.append((random.randint(10, level_width - 12) * TILE_SIZE, random.randint(5, 10) * TILE_SIZE))
    
    boss_door_x = level_width - 3
    
    return {
        "name": f"Level {level_num}" + (" - BOSS!" if is_boss_level else ""),
        "sky_color": sky_color,
        "map": map_data,
        "coins": coin_positions,
        "enemies": enemy_positions,
        "bats": bat_positions,
        "ghosts": ghost_positions,
        "slimes": slime_positions,
        "teleporters": teleporter_positions,
        "thieves": thief_positions,
        "dodgers": dodger_positions,
        "shielders": shielder_positions,
        "healers": healer_positions,
        "moving_platforms": moving_platforms,
        "traps": trap_positions,
        "falling_spikes": falling_spikes,
        "boss_door_x": boss_door_x,
        "is_boss_level": is_boss_level,
        "boss_type": (level_num - 1) // 3 if is_boss_level else None,
    }


LEVELS = {}
for i in range(1, 11):
    is_boss = (i % 3) == 0
    width = 50 + i * 10
    LEVELS[i] = generate_level(i, width, is_boss)


class Particle:
    def __init__(self, x, y, color, velocity, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x, self.vel_y = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.2
        self.lifetime -= 1
    
    def draw(self, surface, camera_x):
        alpha = self.lifetime / self.max_lifetime
        size = max(2, int(6 * alpha))
        color = tuple(int(c * alpha) for c in self.color)
        pygame.draw.circle(surface, color, (int(self.x - camera_x), int(self.y)), size)


class PowerUp:
    def __init__(self, x, y, power_type):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.type = power_type
        self.collected = False
        self.anim_timer = 0
        self.bob_offset = 0
    
    def update(self):
        self.anim_timer += 1
        self.bob_offset = int(4 * math.sin(self.anim_timer * 0.1))
    
    def draw(self, surface, camera_x):
        if self.collected:
            return
        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y + self.bob_offset
        
        if self.type == 0:
            pygame.draw.circle(surface, (255, 50, 50), (draw_x + 12, draw_y + 12), 12)
            pygame.draw.rect(surface, WHITE, (draw_x + 8, draw_y + 6, 8, 4))
            pygame.draw.rect(surface, WHITE, (draw_x + 10, draw_y + 4, 4, 8))
        elif self.type == 1:
            pygame.draw.circle(surface, (50, 150, 255), (draw_x + 12, draw_y + 12), 12)
            pygame.draw.polygon(surface, WHITE, [(draw_x + 12, draw_y + 4), (draw_x + 16, draw_y + 14), (draw_x + 6, draw_y + 10), (draw_x + 18, draw_y + 10), (draw_x + 8, draw_y + 14)])
        elif self.type == 2:
            pygame.draw.circle(surface, (255, 215, 0), (draw_x + 12, draw_y + 12), 12)
            pygame.draw.rect(surface, BLACK, (draw_x + 10, draw_y + 6, 4, 12))


class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        self.data = LEVELS[level_num]
        self.name = self.data["name"]
        self.sky_color = self.data["sky_color"]
        
        self.tiles = []
        self.coins = []
        self.enemies = []
        self.bats = []
        self.ghosts = []
        self.slimes = []
        self.teleporters = []
        self.thieves = []
        self.dodgers = []
        self.shielders = []
        self.healers = []
        self.moving_platforms = []
        self.traps = []
        self.falling_spikes = []
        self.powerups = []
        self.particles = []
        self.boss = None
        
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
        
        for x, y, etype in self.data["enemies"]:
            self.enemies.append(Enemy(x * TILE_SIZE, y * TILE_SIZE, etype))
        
        for x, y in self.data.get("bats", []):
            self.bats.append(Bat(x, y))
        
        for x, y in self.data.get("ghosts", []):
            self.ghosts.append(Ghost(x, y))
        
        for x, y in self.data.get("slimes", []):
            self.slimes.append(Slime(x, y))
        
        for x, y in self.data.get("teleporters", []):
            self.teleporters.append(Teleporter(x, y))
        
        for x, y in self.data.get("thieves", []):
            self.thieves.append(Thief(x, y))
        
        for x, y in self.data.get("dodgers", []):
            self.dodgers.append(Dodger(x, y))
        
        for x, y in self.data.get("shielders", []):
            self.shielders.append(Shielder(x, y))
        
        for x, y in self.data.get("healers", []):
            self.healers.append(Healer(x, y))
        
        for x, y, w in self.data.get("moving_platforms", []):
            self.moving_platforms.append(MovingPlatform(x, y, w))
        
        for x, y, ttype in self.data.get("traps", []):
            self.traps.append(SpikeTrap(x, y, ttype))
        
        for x, y in self.data.get("falling_spikes", []):
            self.falling_spikes.append(FallingSpike(x, y))
        
        for _ in range(2 + self.level_num // 2):
            x = random.randint(10, len(self.data["map"][0]) - 10) * TILE_SIZE
            y = random.randint(3, 10) * TILE_SIZE
            self.powerups.append(PowerUp(x, y, random.randint(0, 2)))
        
        if self.data.get("is_boss_level") and self.data.get("boss_type") is not None:
            self.boss = Boss(500, 10 * TILE_SIZE - 80, self.data["boss_type"])
    
    def update(self, player_rect=None):
        for coin in self.coins:
            coin.update()
        for enemy in self.enemies:
            enemy.update(self.tile_rects)
        for bat in self.bats:
            bat.update()
        for ghost in self.ghosts:
            ghost.update(player_rect)
        for slime in self.slimes:
            slime.update(self.tile_rects)
        for teleporter in self.teleporters:
            teleporter.update(player_rect, self.tile_rects)
        for thief in self.thieves:
            thief.update(player_rect, self.coins)
        for dodger in self.dodgers:
            dodger.update(player_rect, [])
        for shielder in self.shielders:
            shielder.update(self.enemies, player_rect)
        for healer in self.healers:
            healer.update(self.enemies)
        for platform in self.moving_platforms:
            platform.update()
        for trap in self.traps:
            pass
        for spike in self.falling_spikes:
            spike.update()
        for powerup in self.powerups:
            powerup.update()
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        if self.boss and self.boss.alive:
            self.boss.update(self.tile_rects[0].rect if self.tile_rects else None, self.tile_rects)
    
    def draw(self, surface, camera_x):
        for tile in self.tiles:
            tile.draw(surface, camera_x)
        
        for platform in self.moving_platforms:
            platform.draw(surface, camera_x)
        
        for coin in self.coins:
            coin.draw(surface, camera_x)
        
        for bat in self.bats:
            bat.draw(surface, camera_x)
        
        for ghost in self.ghosts:
            ghost.draw(surface, camera_x)
        
        for slime in self.slimes:
            slime.draw(surface, camera_x)
        
        for teleporter in self.teleporters:
            teleporter.draw(surface, camera_x)
        
        for thief in self.thieves:
            thief.draw(surface, camera_x)
        
        for dodger in self.dodgers:
            dodger.draw(surface, camera_x)
        
        for shielder in self.shielders:
            shielder.draw(surface, camera_x)
        
        for healer in self.healers:
            healer.draw(surface, camera_x)
        
        for trap in self.traps:
            trap.draw(surface, camera_x)
        
        for spike in self.falling_spikes:
            spike.draw(surface, camera_x)
        
        for powerup in self.powerups:
            powerup.draw(surface, camera_x)
        
        for enemy in self.enemies:
            enemy.draw(surface, camera_x)
        
        if self.boss:
            self.boss.draw(surface, camera_x)
        
        for particle in self.particles:
            particle.draw(surface, camera_x)


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
            for freq in [250, 350, 450]:
                sound = self._generate_tone(freq, 0.06, 0.25)
                pygame.mixer.Sound.play(sound)
                pygame.time.wait(40)
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
    
    def play_shoot(self):
        if not self.available:
            return
        try:
            sound = self._generate_tone(800, 0.05, 0.2)
            pygame.mixer.Sound.play(sound)
        except:
            pass
    
    def play_hit(self):
        if not self.available:
            return
        try:
            sound = self._generate_tone(150, 0.15, 0.4)
            pygame.mixer.Sound.play(sound)
        except:
            pass
    
    def play_boss_hit(self):
        if not self.available:
            return
        try:
            for freq in [400, 300, 200]:
                sound = self._generate_tone(freq, 0.1, 0.3)
                pygame.mixer.Sound.play(sound)
                pygame.time.wait(80)
        except:
            pass
    
    def play_death(self):
        if not self.available:
            return
        try:
            for freq in [400, 350, 300, 250, 200, 150]:
                sound = self._generate_tone(freq, 0.12, 0.3)
                pygame.mixer.Sound.play(sound)
                pygame.time.wait(80)
        except:
            pass
    
    def play_win(self):
        if not self.available:
            return
        try:
            notes = [523, 659, 784, 1047, 784, 659, 523, 659, 784, 1047]
            for freq in notes:
                sound = self._generate_tone(freq, 0.18, 0.25)
                pygame.mixer.Sound.play(sound)
                pygame.time.wait(140)
        except:
            pass


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SUPAR MAYRO - Ultimate Platformer!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        
        self.current_level = 1
        self.max_levels = 10
        
        self.music = MusicPlayer()
        
        self.shake_timer = 0
        self.shake_intensity = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.invincible_timer = 0
        self.rapid_fire_timer = 0
        self.magnet_active = False
        
        self.chat_text = ""
        self.chat_active = False
        self.chat_history = []
        
        self.reset_game()
    
    def reset_game(self):
        if self.current_level not in LEVELS:
            LEVELS[self.current_level] = generate_level(self.current_level, 50 + self.current_level * 10, (self.current_level % 3) == 0)
        
        self.level = Level(self.current_level)
        self.player = Player(100, 10 * TILE_SIZE)
        self.camera_x = 0
        self.state = STATE_PLAYING
        self.level_width = len(self.level.data["map"][0]) * TILE_SIZE
        self.shake_timer = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.invincible_timer = 0
        self.rapid_fire_timer = 0
        self.magnet_active = False
    
    def add_shake(self, intensity, duration):
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_timer = max(self.shake_timer, duration)
    
    def spawn_particles(self, x, y, color, count=8):
        for _ in range(count):
            vel_x = random.uniform(-3, 3)
            vel_y = random.uniform(-5, -2)
            lifetime = random.randint(20, 40)
            self.level.particles.append(Particle(x, y, color, (vel_x, vel_y), lifetime))
    
    def add_combo(self):
        self.combo_count += 1
        self.combo_timer = 120
        bonus = min(self.combo_count * 10, 100)
        self.player.score += bonus
    
    def next_level(self):
        if self.current_level < self.max_levels:
            self.current_level += 1
            self.reset_game()
        else:
            self.state = STATE_WIN
            self.music.play_win()
    
    def update(self):
        if self.state == STATE_BOSS:
            self.update_boss()
            return
        
        if self.state != STATE_PLAYING:
            return
        
        if self.shake_timer > 0:
            self.shake_timer -= 1
            self.shake_intensity = max(0, self.shake_intensity - 1)
        
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        
        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1
            self.player.shoot_cooldown = max(0, self.player.shoot_cooldown - 1)
        
        if self.combo_timer > 0:
            self.combo_timer -= 1
        elif self.combo_count > 0:
            self.combo_count = 0
        
        keys = pygame.key.get_pressed()
        
        if not self.chat_active:
            if keys[pygame.K_z] or keys[pygame.K_x]:
                self.player.shoot()
                if not getattr(self, 'shoot_key_held', False):
                    self.music.play_shoot()
                    self.shoot_key_held = True
            else:
                self.shoot_key_held = False        
            self.player.update(keys, self.level.tile_rects, self.level.moving_platforms)
        else:
            self.player.vel_x = 0
        
        target_camera_x = self.player.rect.x - SCREEN_WIDTH // 3
        shake_x = random.randint(-self.shake_intensity, self.shake_intensity) if self.shake_timer > 0 else 0
        shake_y = random.randint(-self.shake_intensity, self.shake_intensity) if self.shake_timer > 0 else 0
        
        camera_lerp = 0.15
        self.camera_x = self.camera_x + (target_camera_x - self.camera_x) * camera_lerp
        self.camera_x = max(0, min(self.camera_x + shake_x, self.level_width - SCREEN_WIDTH))
        
        self.level.update(self.player.rect)
        
        if self.magnet_active:
            for coin in self.level.coins:
                if not coin.collected:
                    dx = self.player.rect.centerx - coin.rect.centerx
                    dy = self.player.rect.centery - coin.rect.centery
                    dist = max(1, math.sqrt(dx*dx + dy*dy))
                    if dist < 150:
                        coin.rect.x += (dx / dist) * 5
                        coin.rect.y += (dy / dist) * 5
        
        for coin in self.level.coins:
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
                self.player.score += 100
                self.music.play_coin()
                self.spawn_particles(coin.rect.centerx, coin.rect.centery, COIN_GOLD, 5)
        
        for powerup in self.level.powerups[:]:
            if not powerup.collected and self.player.rect.colliderect(powerup.rect):
                powerup.collected = True
                self.level.powerups.remove(powerup)
                self.music.play_coin()
                if powerup.type == 0:
                    self.player.lives = min(self.player.lives + 1, 10)
                    self.spawn_particles(powerup.rect.centerx, powerup.rect.centery, (255, 50, 50), 10)
                elif powerup.type == 1:
                    self.rapid_fire_timer = 600
                    self.spawn_particles(powerup.rect.centerx, powerup.rect.centery, (50, 150, 255), 10)
                elif powerup.type == 2:
                    self.invincible_timer = 300
                    self.spawn_particles(powerup.rect.centerx, powerup.rect.centery, (255, 215, 0), 10)
        
        for enemy in self.level.enemies:
            if not enemy.alive:
                continue
            if self.player.rect.colliderect(enemy.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < enemy.rect.centery + 10:
                    enemy.alive = False
                    self.player.vel_y = JUMP_FORCE // 2
                    self.player.score += 200
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(3, 5)
                    self.spawn_particles(enemy.rect.centerx, enemy.rect.centery, enemy.color, 10)
                elif self.invincible_timer <= 0:
                    self.player_died()
        
        for bat in self.level.bats:
            if bat.alive and self.player.rect.colliderect(bat.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < bat.rect.centery:
                    bat.alive = False
                    self.player.vel_y = JUMP_FORCE // 2
                    self.player.score += 250
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(3, 5)
                    self.spawn_particles(bat.rect.centerx, bat.rect.centery, BAT_BLACK, 10)
                elif self.invincible_timer <= 0:
                    self.player_died()
        
        for ghost in self.level.ghosts:
            if ghost.alive and self.player.rect.colliderect(ghost.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < ghost.rect.centery:
                    ghost.alive = False
                    self.player.vel_y = JUMP_FORCE // 2
                    self.player.score += 300
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(4, 5)
                    self.spawn_particles(ghost.rect.centerx, ghost.rect.centery, GHOST_WHITE, 12)
                elif self.invincible_timer <= 0:
                    self.player_died()
        
        for slime in self.level.slimes:
            if slime.alive and self.player.rect.colliderect(slime.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < slime.rect.centery:
                    slime.alive = False
                    self.player.vel_y = JUMP_FORCE // 2
                    self.player.score += 350
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(4, 5)
                    self.spawn_particles(slime.rect.centerx, slime.rect.centery, SLIME_GREEN, 12)
                elif self.invincible_timer <= 0:
                    self.player_died()
        
        for teleporter in self.level.teleporters:
            if teleporter.alive and self.player.rect.colliderect(teleporter.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < teleporter.rect.centery:
                    teleporter.alive = False
                    self.player.vel_y = JUMP_FORCE // 2
                    self.player.score += 400
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(5, 8)
                    self.spawn_particles(teleporter.rect.centerx, teleporter.rect.centery, TELEPORTER_PURPLE, 15)
                elif self.invincible_timer <= 0:
                    self.player_died()
        
        for thief in self.level.thieves:
            if thief.alive and self.player.rect.colliderect(thief.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < thief.rect.centery:
                    thief.alive = False
                    self.player.vel_y = JUMP_FORCE // 2
                    self.player.score += 500
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(4, 6)
                    self.spawn_particles(thief.rect.centerx, thief.rect.centery, THIEF_BLUE, 12)
                elif self.invincible_timer <= 0:
                    self.player_died()
        
        for dodger in self.level.dodgers:
            if dodger.alive and self.player.rect.colliderect(dodger.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < dodger.rect.centery:
                    dodger.alive = False
                    self.player.vel_y = JUMP_FORCE // 2
                    self.player.score += 450
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(4, 6)
                    self.spawn_particles(dodger.rect.centerx, dodger.rect.centery, ANNOYING_PINK, 12)
                elif self.invincible_timer <= 0:
                    self.player_died()
        
        for shielder in self.level.shielders:
            if shielder.alive and self.player.rect.colliderect(shielder.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < shielder.rect.centery:
                    shielder.alive = False
                    self.player.vel_y = JUMP_FORCE // 2
                    self.player.score += 600
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(6, 10)
                    self.spawn_particles(shielder.rect.centerx, shielder.rect.centery, SHIELDER_GRAY, 15)
                elif self.invincible_timer <= 0:
                    self.player_died()
        
        for healer in self.level.healers:
            if healer.alive and self.player.rect.colliderect(healer.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < healer.rect.centery:
                    healer.alive = False
                    self.player.vel_y = JUMP_FORCE // 2
                    self.player.score += 550
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(5, 8)
                    self.spawn_particles(healer.rect.centerx, healer.rect.centery, (50, 200, 100), 15)
                elif self.invincible_timer <= 0:
                    self.player_died()
        
        for bullet in self.player.bullets[:]:
            for enemy in self.level.enemies:
                if enemy.alive and bullet.rect.colliderect(enemy.rect):
                    enemy.alive = False
                    self.player.score += 200
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(2, 3)
                    self.spawn_particles(enemy.rect.centerx, enemy.rect.centery, enemy.color, 8)
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    break
            
            if self.level.boss and self.level.boss.alive and bullet.rect.colliderect(self.level.boss.rect):
                self.level.boss.take_damage()
                self.player.score += 100
                self.music.play_boss_hit()
                self.add_shake(5, 8)
                self.spawn_particles(bullet.rect.centerx, bullet.rect.centery, ANGRY_RED, 6)
                if bullet in self.player.bullets:
                    self.player.bullets.remove(bullet)
            
            for teleporter in self.level.teleporters:
                if teleporter.alive and bullet.rect.colliderect(teleporter.rect):
                    teleporter.alive = False
                    self.player.score += 400
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(3, 4)
                    self.spawn_particles(teleporter.rect.centerx, teleporter.rect.centery, TELEPORTER_PURPLE, 10)
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    break
            
            for thief in self.level.thieves:
                if thief.alive and bullet.rect.colliderect(thief.rect):
                    thief.alive = False
                    self.player.score += 500
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(3, 4)
                    self.spawn_particles(thief.rect.centerx, thief.rect.centery, THIEF_BLUE, 10)
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    break
            
            for dodger in self.level.dodgers:
                if dodger.alive and bullet.rect.colliderect(dodger.rect):
                    if random.random() < 0.3:
                        dodger.alive = False
                        self.player.score += 450
                        self.music.play_hit()
                        self.add_combo()
                        self.add_shake(3, 4)
                        self.spawn_particles(dodger.rect.centerx, dodger.rect.centery, ANNOYING_PINK, 10)
                        if bullet in self.player.bullets:
                            self.player.bullets.remove(bullet)
                    break
            
            for shielder in self.level.shielders:
                if shielder.alive and bullet.rect.colliderect(shielder.rect):
                    shielder.alive = False
                    self.player.score += 600
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(4, 6)
                    self.spawn_particles(shielder.rect.centerx, shielder.rect.centery, SHIELDER_GRAY, 12)
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    break
            
            for healer in self.level.healers:
                if healer.alive and bullet.rect.colliderect(healer.rect):
                    healer.alive = False
                    self.player.score += 550
                    self.music.play_hit()
                    self.add_combo()
                    self.add_shake(4, 5)
                    self.spawn_particles(healer.rect.centerx, healer.rect.centery, (50, 200, 100), 12)
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    break
        
        if self.level.boss and self.level.boss.alive:
            if self.player.rect.colliderect(self.level.boss.rect) and self.invincible_timer <= 0:
                self.player_died()
            
            if not self.level.boss.alive:
                self.player.score += 5000
                self.add_shake(15, 30)
                for _ in range(5):
                    self.spawn_particles(
                        self.level.boss.rect.centerx + random.randint(-30, 30),
                        self.level.boss.rect.centery + random.randint(-30, 30),
                        self.level.boss.color, 15
                    )
                self.music.play_win()
                self.next_level()
        
        for tile in self.level.tiles:
            if tile.type in (TILE_SPIKE, TILE_SPIKE_UP) and self.player.rect.colliderect(tile.rect):
                if self.invincible_timer <= 0:
                    self.player_died()
        
        for trap in self.level.traps:
            if self.player.rect.colliderect(trap.rect):
                if self.invincible_timer <= 0:
                    self.player_died()
        
        for spike in self.level.falling_spikes:
            if self.player.rect.colliderect(spike.rect):
                if self.invincible_timer <= 0:
                    self.player_died()
        
        if self.player.rect.y > SCREEN_HEIGHT:
            self.player_died()
        
        boss_door_x = self.level.data.get("boss_door_x", 0) * TILE_SIZE
        if self.player.rect.x >= boss_door_x:
            if self.level.data.get("is_boss_level"):
                self.state = STATE_BOSS
            else:
                self.player.score += 1000
                self.next_level()
    
    def update_boss(self):
        keys = pygame.key.get_pressed()
        
        if not self.chat_active:
            if keys[pygame.K_z] or keys[pygame.K_x]:
                self.player.shoot()
            
            self.player.update(keys, self.level.tile_rects, [])
        else:
            self.player.vel_x = 0
        
        self.level.update()
        
        for bullet in self.player.bullets[:]:
            for enemy in self.level.boss.attacks:
                if enemy.alive and bullet.rect.colliderect(enemy.rect):
                    enemy.alive = False
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
        
        if self.player.rect.colliderect(self.level.boss.rect):
            self.player_died()
        
        for enemy in self.level.boss.attacks:
            if enemy.alive and self.player.rect.colliderect(enemy.rect):
                self.player_died()
        
        for bullet in self.player.bullets[:]:
            if bullet.rect.colliderect(self.level.boss.rect):
                self.level.boss.take_damage()
                self.music.play_boss_hit()
                if bullet in self.player.bullets:
                    self.player.bullets.remove(bullet)
        
        if self.player.rect.y > SCREEN_HEIGHT:
            self.player_died()
    
    def player_died(self):
        self.music.play_death()
        self.add_shake(10, 20)
        self.spawn_particles(self.player.rect.centerx, self.player.rect.centery, SKIN_COLOR, 20)
        self.player.lives -= 1
        self.combo_count = 0
        self.invincible_timer = 0
        self.rapid_fire_timer = 0
        if self.player.lives <= 0:
            self.state = STATE_GAME_OVER
        else:
            self.player.rect.x = 100
            self.player.rect.y = 10 * TILE_SIZE
            self.player.vel_x = 0
            self.player.vel_y = 0
            self.camera_x = 0
            if self.state == STATE_BOSS:
                self.level.boss = Boss(500, 10 * TILE_SIZE - 80, self.level.data.get("boss_type", 0))
    
    def draw(self):
        self.screen.fill(self.level.sky_color)
        
        self.level.draw(self.screen, self.camera_x)
        
        self.player.draw(self.screen, self.camera_x)
        
        score_text = self.font.render(f"Score: {self.player.score}", True, TEXT_COLOR)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, TEXT_COLOR)
        level_text = self.font.render(f"Level {self.current_level}: {self.level.name}", True, TEXT_COLOR)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 120, 10))
        
        if self.state == STATE_BOSS and self.level.boss:
            boss_text = self.large_font.render(self.level.boss.name, True, TRAP_RED)
            self.screen.blit(boss_text, (SCREEN_WIDTH // 2 - 150, 50))
        
        if self.combo_count > 1:
            combo_color = (255, 255 - min(self.combo_count * 20, 200), 0)
            combo_text = self.font.render(f"COMBO x{self.combo_count}!", True, combo_color)
            combo_y = 50 + int(5 * math.sin(pygame.time.get_ticks() * 0.01))
            self.screen.blit(combo_text, (SCREEN_WIDTH // 2 - 80, combo_y))
        
        powerup_y = 50
        if self.invincible_timer > 0:
            shield_text = self.small_font.render(f"SHIELD: {self.invincible_timer // 60}s", True, (255, 215, 0))
            self.screen.blit(shield_text, (SCREEN_WIDTH - 150, powerup_y))
            powerup_y += 25
        if self.rapid_fire_timer > 0:
            rapid_text = self.small_font.render(f"RAPID: {self.rapid_fire_timer // 60}s", True, (50, 150, 255))
            self.screen.blit(rapid_text, (SCREEN_WIDTH - 150, powerup_y))
        
        if self.chat_active:
            chat_bg = pygame.Surface((SCREEN_WIDTH - 40, 40), pygame.SRCALPHA)
            chat_bg.fill((0, 0, 0, 180))
            self.screen.blit(chat_bg, (20, SCREEN_HEIGHT - 60))
            chat_prompt = self.font.render("> " + self.chat_text, True, WHITE)
            self.screen.blit(chat_prompt, (30, SCREEN_HEIGHT - 55))
            if pygame.time.get_ticks() % 1000 < 500:
                cursor_x = 30 + chat_prompt.get_width()
                pygame.draw.line(self.screen, WHITE, (cursor_x, SCREEN_HEIGHT - 55), (cursor_x, SCREEN_HEIGHT - 30), 2)
        
        if len(self.chat_history) > 0:
            y_offset = SCREEN_HEIGHT - 100
            for msg in self.chat_history[-3:]:
                chat_msg = self.small_font.render(msg, True, (220, 220, 220))
                msg_bg = pygame.Surface((chat_msg.get_width() + 10, chat_msg.get_height() + 4), pygame.SRCALPHA)
                msg_bg.fill((0, 0, 0, 120))
                self.screen.blit(msg_bg, (20, y_offset))
                self.screen.blit(chat_msg, (25, y_offset + 2))
                y_offset -= 25
        
        controls_text = self.small_font.render("ARROWS: Move | SPACE: Jump | Z/X: Shoot | P: Pause | T: Chat", True, BLACK)
        self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))
        
        if self.state == STATE_PAUSED:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            text = self.large_font.render("PAUSED", True, WHITE)
            self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        
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
        
        pygame.display.flip()
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.chat_active:
                        if event.key == pygame.K_RETURN:
                            if self.chat_text.strip():
                                self.chat_history.append(self.chat_text)
                                if len(self.chat_history) > 5:
                                    self.chat_history.pop(0)
                            self.chat_text = ""
                            self.chat_active = False
                        elif event.key == pygame.K_ESCAPE:
                            self.chat_text = ""
                            self.chat_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.chat_text = self.chat_text[:-1]
                        elif event.unicode and event.unicode.isprintable():
                            self.chat_text += event.unicode
                    else:
                        if event.key == pygame.K_t and self.state == STATE_PLAYING:
                            self.chat_active = True
                            self.chat_text = ""
                        elif event.key == pygame.K_p and self.state == STATE_PLAYING:
                            self.state = STATE_PAUSED
                        elif event.key == pygame.K_p and self.state == STATE_PAUSED:
                            self.state = STATE_PLAYING
                        elif event.key == pygame.K_r and self.state in (STATE_GAME_OVER, STATE_WIN):
                            self.current_level = 1
                            self.reset_game()
                        elif event.key == pygame.K_SPACE or event.key == pygame.K_w:
                            if self.state == STATE_PLAYING and self.player.on_ground and not self.chat_active:
                                self.music.play_jump()
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
