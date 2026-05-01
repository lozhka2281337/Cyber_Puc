import pygame
import math

from entity.weapon import LaserWeapon, MeleeWeapon
from entity.bullet import SparkEffect 

from config import MAP_WIDTH

class Handler:
    def __init__(self, player, walls, bullets, enemies):
        self.player = player
        self.walls = walls
        self.bullets = bullets
        self.enemies = enemies

    def process_events(self, game, camera_x: float, camera_y: float) -> bool | None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.player.current_weapon_idx = (self.player.current_weapon_idx - 1) % len(self.player.inventory)
                
                if event.button == 5:
                    self.player.current_weapon_idx = (self.player.current_weapon_idx + 1) % len(self.player.inventory)

                if event.button == 1: 
                    new_bullets = self.player.shot(camera_x, camera_y)
                    if new_bullets:
                        self.bullets.extend(new_bullets)

    def process_bullets(self, game): 
        for bullet in self.bullets[:]:

            if getattr(bullet, 'is_effect', False):
                if not bullet.is_alive:
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                continue

            if hasattr(bullet, 'exploded'):
                if bullet.exploded:
                    for _ in range(5): 
                        self.bullets.append(SparkEffect(bullet.rect.centerx, bullet.rect.centery, (255, 100, 50)))

                    for enemy in self.enemies[:]:
                        enemy_pos = pygame.math.Vector2(enemy.rect.center)
                        if bullet.pos.distance_to(enemy_pos) <= bullet.blast_radius:
                            if enemy in self.enemies:
                                enemy.get_damage(200) 
                                if enemy.hp <= 0: self.enemies.remove(enemy)
                    
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                continue

            if hasattr(bullet, 'is_alive') and not bullet.is_alive:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue

            hit_wall = False
            for wall in self.walls:
                if bullet.rect.colliderect(wall):
                    if hasattr(bullet, 'exploded'):
                        bullet.is_moving = False
                    else:
                        if bullet in self.bullets:
                            self.bullets.append(SparkEffect(bullet.rect.centerx, bullet.rect.centery, bullet.color))
                            self.bullets.remove(bullet)
                        hit_wall = True
                    break
            
            if hit_wall: continue

            if abs(bullet.pos.x) > MAP_WIDTH * 40: 
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue

            if getattr(bullet, 'is_enemy_bullet', False):
                if bullet.rect.colliderect(self.player.rect):
                    damage = getattr(bullet, 'damage', 1)
                    self.player.get_damage(damage)
                    if self.player.hp <= 0: game.death_player()
                    
                    if bullet in self.bullets:
                        self.bullets.append(SparkEffect(bullet.rect.centerx, bullet.rect.centery, bullet.color))
                        self.bullets.remove(bullet)
            else:
                for enemy in self.enemies[:]: 
                    if bullet.rect.colliderect(enemy.rect):
                        if hasattr(bullet, 'exploded'):
                            bullet.is_moving = False
                        else:
                            enemy.get_damage(bullet.damage if hasattr(bullet, 'damage') else 50)
                            if enemy.hp <= 0: self.enemies.remove(enemy)
                            
                            if bullet in self.bullets:
                                self.bullets.append(SparkEffect(bullet.rect.centerx, bullet.rect.centery, bullet.color))
                                self.bullets.remove(bullet)
                        break

    def process_player_damage(self, game):
        for enemy in self.enemies:
            damage = getattr(enemy, 'damage', 1) 
            
            if hasattr(enemy, 'attack_range') and not hasattr(enemy, 'shoot_cooldown'): 
                enemy_pos = pygame.math.Vector2(enemy.rect.center)
                player_pos = pygame.math.Vector2(self.player.rect.center)

                if enemy_pos.distance_to(player_pos) <= enemy.attack_range:
                    self.player.get_damage(damage) 
                    if self.player.hp <= 0: game.death_player()
            elif not hasattr(enemy, 'shoot_cooldown'):
                if enemy.rect.colliderect(self.player.rect):
                    self.player.get_damage(damage) 
                    if self.player.hp <= 0: game.death_player()

    def get_laser_end_pos(self, weapon):
        start_pos = self.player.rect.center
        max_end = pygame.math.Vector2(
            start_pos[0] + weapon.locked_dir.x * 1500, 
            start_pos[1] + weapon.locked_dir.y * 1500
        )
        final_point = max_end
        min_dist = 1500
        start_v = pygame.math.Vector2(start_pos)

        for wall in self.walls:
            intersect = wall.clipline(start_pos, max_end)
            if intersect:
                hit_point = pygame.math.Vector2(intersect[0])
                dist = start_v.distance_to(hit_point)
                if dist < min_dist:
                    min_dist = dist
                    final_point = hit_point
        return final_point

    def process_laser_damage(self):
        weapon = self.player.inventory[self.player.current_weapon_idx]
        if isinstance(weapon, LaserWeapon) and weapon.is_firing:
            start_pos = self.player.rect.center
            end_pos = self.get_laser_end_pos(weapon)
            for enemy in self.enemies[:]:
                if enemy.rect.clipline(start_pos, end_pos):
                    enemy.get_damage(2) 
                    if enemy.hp <= 0: self.enemies.remove(enemy)

    def process_melee_damage(self):
        weapon = self.player.inventory[self.player.current_weapon_idx]
        if isinstance(weapon, MeleeWeapon) and weapon.is_swinging:
            start_pos = pygame.math.Vector2(self.player.rect.center)
            for enemy in self.enemies[:]:
                if enemy in weapon.hit_enemies: continue
                enemy_pos = pygame.math.Vector2(enemy.rect.center)
                dist = start_pos.distance_to(enemy_pos)
                if dist <= weapon.reach + 16:
                    dx = enemy_pos.x - start_pos.x
                    dy = enemy_pos.y - start_pos.y
                    angle_to_enemy = math.degrees(math.atan2(dy, dx))
                    angle_diff = (angle_to_enemy - weapon.locked_angle + 180) % 360 - 180
                    if abs(angle_diff) <= weapon.arc_degrees / 2:
                        enemy.get_damage(150)
                        if enemy.hp <= 0: self.enemies.remove(enemy)
                        weapon.hit_enemies.append(enemy)