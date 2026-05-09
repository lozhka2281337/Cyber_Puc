import pygame
import math

from entity.weapon import LaserWeapon, MeleeWeapon
from entity.bullet import Bullet, Grenade, SparkEffect 

from config import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, ZIP_BOMB, SCANNER, FIREWALL, DEFRAG, MELEE

class Handler:
    def __init__(self, player, world):
        self.player = player
        self.walls = world.walls
        self.bullets = world.bullets
        self.enemies = world.enemies
        self.effects = world.effects
        self.grenades = world.grenades

    def process_events(self, game, camera_x: float, camera_y: float) -> bool | None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            
            # выход на esc
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # обработка колесика мышки (переключает оружие)
                if event.button == 4:
                    self.player.current_weapon_idx = (self.player.current_weapon_idx - 1) % len(self.player.inventory)
                if event.button == 5:
                    self.player.current_weapon_idx = (self.player.current_weapon_idx + 1) % len(self.player.inventory)

                # выстрел
                if event.button == 1: 
                    new_elements = self.player.shot(camera_x, camera_y)
                    if new_elements: self.create_new_elements(new_elements)

    def create_new_elements(self, new_elements: list):
        inventory = self.player.inventory
        weapon = inventory[self.player.current_weapon_idx]
        
        if weapon.name == SCANNER or weapon.name == FIREWALL: self.bullets.extend(new_elements)
        elif weapon.name == ZIP_BOMB: self.grenades.extend(new_elements)

    def process_elements(self, game): 
        """Главный метод-диспетчер."""
        self._process_effects()
        self._process_grenades()
        self._process_bullets(game)

    def _process_effects(self):
        for effect in self.effects[:]:
            if not effect.is_alive:
                self.effects.remove(effect)

    def _process_grenades(self):
        for grenade in self.grenades[:]:
            if not grenade.exploded:
                # проверка на столкнокение со стеной
                for wall in self.walls:
                    if grenade.rect.colliderect(wall):
                        grenade.is_moving = False
                        break
            else: self._grenade_is_boom(grenade)
                
    def _grenade_is_boom(self, grenade):
        # эффекты оставляемые гранатой
        for _ in range(5): self.effects.append(SparkEffect(grenade.rect.centerx, grenade.rect.centery, (255, 100, 50)))
        
        # убийство врагов
        for enemy in self.enemies[:]:
            enemy_pos = pygame.math.Vector2(enemy.rect.center)
            if grenade.pos.distance_to(enemy_pos) <= grenade.blast_radius:
                enemy.get_damage(200) 
                if enemy.hp <= 0: self.enemies.remove(enemy)
    
        self.grenades.remove(grenade)

    def _process_bullets(self, game):
        for bullet in self.bullets[:]:               
            if not bullet.is_alive or abs(bullet.pos.x) > MAP_WIDTH * TILE_SIZE or abs(bullet.pos.y) > MAP_HEIGHT * TILE_SIZE: 
                self.bullets.remove(bullet)
                continue

            # Столкновение со стенами
            for wall in self.walls:
                if bullet.rect.colliderect(wall):
                    self.effects.append(SparkEffect(bullet.rect.centerx, bullet.rect.centery, bullet.color))
                    self.bullets.remove(bullet)
                    break

            if bullet not in self.bullets: continue    

            if bullet.player_bullet: self._procces_hit_player_bullet(bullet)
            else: self._procces_hit_enemy_bullet(game, bullet)
                
    def _procces_hit_player_bullet(self, bullet):
        for enemy in self.enemies[:]: 
            if bullet.rect.colliderect(enemy.rect):
                enemy.get_damage(bullet.damage)
                if enemy.hp <= 0: self.enemies.remove(enemy)
                
                if bullet in self.bullets:
                    self.effects.append(SparkEffect(bullet.rect.centerx, bullet.rect.centery, bullet.color))
                    self.bullets.remove(bullet)
                break

    def _procces_hit_enemy_bullet(self, game, bullet):
        if bullet.rect.colliderect(self.player.rect):
            damage = bullet.damage
            self.player.get_damage(damage)
            if self.player.hp <= 0: game.death_player()
            
            self.effects.append(SparkEffect(bullet.rect.centerx, bullet.rect.centery, bullet.color))
            self.bullets.remove(bullet)

    def process_player_damage(self, game):
        for enemy in self.enemies:
            damage = enemy.damage

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
        if weapon.name == DEFRAG and weapon.is_firing:
            start_pos = self.player.rect.center
            end_pos = self.get_laser_end_pos(weapon)

            for enemy in self.enemies[:]:
                if enemy.rect.clipline(start_pos, end_pos):
                    enemy.get_damage(weapon.damage) 
                    if enemy.hp <= 0: self.enemies.remove(enemy)

    def process_melee_damage(self):
        weapon = self.player.inventory[self.player.current_weapon_idx]

        if weapon.name == MELEE and weapon.is_swinging:
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