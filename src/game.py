import pygame

from entity.enemy import Enemy
from entity.player import Player
from entity.weapon import LaserWeapon 

from config import (WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT, 
                    SPAWN_ENEMY_EVENT, SPAWN_ENEMY_TIME, 
                    FPS, SHOT_DELAY, BLUE_WALL)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Roguelike Prototype")

        self.font = pygame.font.SysFont("Arial", 32, bold = True)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.FONT = pygame.font.SysFont("Arial", 32, bold = True)

        self.clock = pygame.time.Clock()

        self.new_game()

    def new_game(self):
        self.player = Player(0, 0)
        
        self.bullets = []
        self.health_packs = []
        self.enemies = []
        self.walls = []

        self.running = True

        """ потом убрать"""
        self.enemies.append(Enemy(100, 100))
        self.enemies.append(Enemy(-200, 100))
        self.enemies.append(Enemy(-500, 100))
        self.walls.append(pygame.Rect(100, -250, 50, 500))
        self.walls.append(pygame.Rect(-200, -250, 50, 500))
        self.walls.append(pygame.Rect(-500, -250, 50, 500))

    def process_events(self, camera_x: float, camera_y: float):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.player.current_weapon_idx = (self.player.current_weapon_idx - 1) % len(self.player.inventory)
                
                if event.button == 5:
                    self.player.current_weapon_idx = (self.player.current_weapon_idx + 1) % len(self.player.inventory)

                if event.button == 1: 
                    new_bullets = self.player.shot(camera_x, camera_y)
                    if new_bullets:
                        self.bullets.extend(new_bullets)

    def process_bullets(self):
        for bullet in self.bullets[:]:
            
            if hasattr(bullet, 'is_alive') and not bullet.is_alive:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue

            hit_wall = False
            for wall in self.walls:
                if bullet.rect.colliderect(wall):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    hit_wall = True
                    break
            
            if hit_wall: continue

            if abs(bullet.pos.x) > MAP_WIDTH:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue

            for enemy in self.enemies[:]: 
                if bullet.rect.colliderect(enemy.rect):
                    if enemy in self.enemies:
                        enemy.get_damage(bullet.damage)
                        if enemy.hp <= 0: self.enemies.remove(enemy)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

    def process_player_damage(self):
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                self.player.get_damage()
                if self.player.hp <= 0: self.death_player()

    def death_player(self):
        self.screen.fill((0, 0, 0))

        death_msg = self.FONT.render("GAME OVER", True, (255, 255, 255))
        self.screen.blit(death_msg, (WIDTH//2 - 100, HEIGHT//2))
        pygame.display.flip()

        pygame.time.wait(3000)
        
        self.new_game()

    def draw_hp(self):
        pygame.draw.rect(self.screen, (50, 50, 50), (10, 10, 180, 50))
        health_text = self.FONT.render(f"HP: {self.player.hp}", True, (255, 0, 0))
        self.screen.blit(health_text, (20, 15))

        if self.player.hp <= 1:
            pygame.draw.rect(self.screen, (255, 0, 0), (0, 0, WIDTH, HEIGHT), 5)

    def draw_weapon_hud(self):
        start_x = WIDTH - 220
        start_y = HEIGHT - 80
        
        for i in range(len(self.player.inventory)):
            weapon = self.player.inventory[i]
            is_active = (i == self.player.current_weapon_idx)
            
            offset_y = (i - self.player.current_weapon_idx) * -35
            
            w_color = getattr(weapon, 'b_color', getattr(weapon, 'color', (255, 255, 255)))

            if is_active:
                text_surf = self.FONT.render(f"> {weapon.name}", True, w_color)
            else:
                text_surf = self.FONT.render(weapon.name, True, (120, 120, 120))
                text_surf.set_alpha(150) 
            
            self.screen.blit(text_surf, (start_x, start_y + offset_y))

    def process_laser_damage(self):
        weapon = self.player.inventory[self.player.current_weapon_idx]
        
        if isinstance(weapon, LaserWeapon) and weapon.is_firing:
            start_pos = self.player.rect.center
            
            end_pos = (start_pos[0] + weapon.locked_dir.x * 1500, start_pos[1] + weapon.locked_dir.y * 1500)
            
            for enemy in self.enemies[:]:
                if enemy.rect.clipline(start_pos, end_pos):
                    self.enemies.remove(enemy)

    """ три главные функции"""

    def update(self, dt: float):
        self.player.update(dt, self.walls)

        for weapon in self.player.inventory:
            weapon.update()

        for bullet in self.bullets:
            bullet.update(dt)

        for enemy in self.enemies:
            enemy.update(dt, self.player, self.walls)

        self.process_bullets()
        self.process_player_damage()
        
        #self.process_laser_damage()

    def draw(self, camera_x, camera_y):
        self.screen.fill("purple")

        # временная сетка
        for x in range(-2000, 2000, 50):
            pygame.draw.line(self.screen, (100, 50, 150), (x - camera_x, -2000-camera_y), (x - camera_x, 2000 - camera_y))
        for y in range(-2000, 2000, 50):
            pygame.draw.line(self.screen, (100, 50, 150), (-2000-camera_x, y - camera_y), (2000 - camera_x, y - camera_y))

        """ ентити """
        self.player.draw(self.screen, camera_x, camera_y)
        
        weapon = self.player.inventory[self.player.current_weapon_idx]
        if isinstance(weapon, LaserWeapon):
            start_p = (self.player.rect.centerx - camera_x, self.player.rect.centery - camera_y)
            
            if weapon.is_charging:
                import math 
                pulse = math.sin(pygame.time.get_ticks() * 0.03) * 5
                radius = int(8 + pulse)
                pygame.draw.circle(self.screen, weapon.color, start_p, radius)
                pygame.draw.circle(self.screen, (255, 255, 255), start_p, max(1, radius - 4))
                
            elif weapon.is_firing:
                end_p = (start_p[0] + weapon.locked_dir.x * 1500, start_p[1] + weapon.locked_dir.y * 1500)
                pygame.draw.line(self.screen, weapon.color, start_p, end_p, weapon.beam_width)
                pygame.draw.line(self.screen, (255, 255, 255), start_p, end_p, max(1, weapon.beam_width // 3))

        for bullet in self.bullets: 
            bullet.draw(self.screen, camera_x, camera_y)
        
        for enemy in self.enemies:
            enemy.draw(self.screen, camera_x, camera_y)
        
        """ стены """
        for wall in self.walls:
            screen_x = int(wall.x - camera_x)
            screen_y = int(wall.y - camera_y)
            pygame.draw.rect(self.screen, BLUE_WALL, (screen_x, screen_y, wall.width, wall.height))

        """ интерфейс """
        self.draw_hp()
        self.draw_weapon_hud() 

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  

            camera_x = int(self.player.rect.x + 16 - WIDTH / 2)
            camera_y = int(self.player.rect.y + 16 - HEIGHT / 2)
            
            self.process_events(camera_x, camera_y)
            
            self.update(dt)
            
            camera_x = int(self.player.rect.x + 16 - WIDTH / 2)
            camera_y = int(self.player.rect.y + 16 - HEIGHT / 2)
            
            self.draw(camera_x, camera_y)