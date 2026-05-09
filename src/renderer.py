import pygame
import math

from config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, BLUE_WALL, MAP_WIDTH, MAP_HEIGHT, MELEE, DEFRAG

from entity.weapon import LaserWeapon

class Renderer:
    def __init__(self, screen, player, world):
        self.screen = screen
        self.player = player

        self.walls = world.walls
        self.bullets = world.bullets
        self.effects = world.effects
        self.grenades = world.grenades
        self.enemies = world.enemies

        self.FONT = pygame.font.SysFont("Arial", 32, bold=True)
        self.map_surface = pygame.Surface((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE), pygame.SRCALPHA)

        self.init_map_surface()

    def init_map_surface(self):
        surface_width = MAP_WIDTH * TILE_SIZE
        surface_height = MAP_HEIGHT * TILE_SIZE

        # временная сетка
        for x in range(0, surface_width, TILE_SIZE):
            pygame.draw.line(self.map_surface, (100, 50, 150), (x, 0), (x, surface_height))
        for y in range(0, surface_height, TILE_SIZE):
            pygame.draw.line(self.map_surface, (100, 50, 150), (0, y), (surface_width, y))

        """ стены """
        for wall in self.walls:
            pygame.draw.rect(self.map_surface, BLUE_WALL, wall)

    def draw_hp(self):
        pygame.draw.rect(self.screen, (50, 50, 50), (10, 10, 180, 50))

        health_text = self.FONT.render(f"HP: {self.player.hp}", True, (255, 0, 0))
        self.screen.blit(health_text, (20, 15))

        if self.player.hp <= 1:
            pygame.draw.rect(self.screen, (255, 0, 0), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 5)

    def draw_death_screen(self):
        self.screen.fill((0, 0, 0))

        death_msg = self.FONT.render("GAME OVER", True, (255, 255, 255))
        self.screen.blit(death_msg, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
        pygame.display.flip()

        pygame.time.wait(3000)

    def draw_weapon_hud(self):
        start_x = SCREEN_WIDTH - 220
        start_y = SCREEN_HEIGHT - 80
        
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

    def draw_laser(self, weapon, camera_x, camera_y):
        start_p = (self.player.rect.centerx - camera_x, self.player.rect.centery - camera_y)
            
        if weapon.is_charging:
            pulse = math.sin(pygame.time.get_ticks() * 0.03) * 5
            radius = int(8 + pulse)
            pygame.draw.circle(self.screen, weapon.color, start_p, radius)
            pygame.draw.circle(self.screen, (255, 255, 255), start_p, max(1, radius - 4))
            
        elif weapon.is_firing:
            world_end = self.get_laser_end_pos(weapon)
            end_p = (world_end.x - camera_x, world_end.y - camera_y)

            pygame.draw.line(self.screen, weapon.color, start_p, end_p, weapon.beam_width)
            pygame.draw.line(self.screen, (255, 255, 255), start_p, end_p, max(1, weapon.beam_width // 3))
            
            spark_radius = int(weapon.beam_width * 1.5 + math.sin(pygame.time.get_ticks() * 0.05) * 3)
            pygame.draw.circle(self.screen, weapon.color, (int(end_p[0]), int(end_p[1])), spark_radius)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(end_p[0]), int(end_p[1])), max(2, spark_radius // 2))

    def draw_melee(self, weapon, camera_x, camera_y):
        start_p = (self.player.rect.centerx - camera_x, self.player.rect.centery - camera_y)
            
        time_left = weapon.swing_timer - pygame.time.get_ticks()
        alpha = max(0, int(255 * (time_left / weapon.swing_duration)))
        
        if alpha > 0:
            swing_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            points = [start_p]
            start_angle = math.radians(weapon.locked_angle - weapon.arc_degrees / 2)
            end_angle = math.radians(weapon.locked_angle + weapon.arc_degrees / 2)
            
            steps = 10
            for i in range(steps + 1):
                angle = start_angle + (end_angle - start_angle) * (i / steps)
                x = start_p[0] + math.cos(angle) * weapon.reach
                y = start_p[1] + math.sin(angle) * weapon.reach
                points.append((x, y))
                
            pygame.draw.polygon(swing_surf, (*weapon.color, alpha // 2), points)
            pygame.draw.polygon(swing_surf, (*weapon.color, alpha), points, 2)
            
            self.screen.blit(swing_surf, (0, 0))

    def draw_weapon(self, camera_x, camera_y):
        weapon = self.player.inventory[self.player.current_weapon_idx]
        if weapon.name == DEFRAG: self.draw_laser(weapon, camera_x, camera_y)
        elif weapon.name == MELEE and weapon.is_swinging: self.draw_melee(weapon, camera_x, camera_y)


    def draw(self, camera_x, camera_y):
        """ карта """
        self.screen.fill("purple")
        self.screen.blit(self.map_surface, (-camera_x, -camera_y))

        """ ентити """
        self.player.draw(self.screen, camera_x, camera_y)
        
        """ атака оружия игрока """
        self.draw_weapon(camera_x, camera_y)

        for bullet in self.bullets: 
            bullet.draw(self.screen, camera_x, camera_y)
        
        for grenade in self.grenades:
            grenade.draw(self.screen, camera_x, camera_y)

        for effect in self.effects:
            effect.draw(self.screen, camera_x, camera_y)

        for enemy in self.enemies:
            enemy.draw(self.screen, camera_x, camera_y)
    
        """ интерфейс """
        self.draw_hp()
        self.draw_weapon_hud() 

        pygame.display.flip()