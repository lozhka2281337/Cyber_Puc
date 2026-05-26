import pygame

from .bullet import Bullet
from .effects import SparkEffect


class Grenade(Bullet):
    def __init__(self, x, y, target_x, target_y, speed, color, blast_radius, fuse_time, max_range):
        super().__init__(x, y, target_x, target_y, speed, color, damage=0, max_dist=max_range)
        
        self.blast_radius = blast_radius
        self.fuse_time = fuse_time
        self.spawn_time = pygame.time.get_ticks()
        self.exploded = False
        self.is_moving = True

        target_pos = pygame.math.Vector2(target_x, target_y)
        dist_to_target = self.start_pos.distance_to(target_pos)
        self.target_dist = min(dist_to_target, max_range)

    def update(self, world, camera, dt):
        if self.is_moving:
            if self.pos.distance_to(self.start_pos) < self.target_dist:
                self.pos += self.direction * self.speed * dt
                self.rect.centerx = round(self.pos.x)
                self.rect.centery = round(self.pos.y)

                for wall in world.walls:
                    if self.rect.colliderect(wall):
                        self.is_moving = False
                        break 
            else:
                self.is_moving = False
                
        current_time = pygame.time.get_ticks()
        if current_time - self.spawn_time >= self.fuse_time:
            self._grenade_is_boom(world, camera)

    def draw(self, surface, cam_x, cam_y):
        offset_rect = self.rect.move(-cam_x, -cam_y)
        grenade_center = offset_rect.center
        
        time_alive = pygame.time.get_ticks() - self.spawn_time
        blink_rate = max(50, 200 - (time_alive // 4)) 

        is_bright_phase = (time_alive // blink_rate) % 2 == 0

        surf_size = (self.blast_radius * 2) + 10
        temp_surface = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        temp_center = surf_size // 2
        if is_bright_phase:
            outline_color = (255, 50, 50, 255) 
            fill_color = (255, 50, 50, 70)    
            grenade_body_color = (255, 50, 50)
        else:
            outline_color = (150, 50, 50, 255) 
            fill_color = (150, 50, 50, 30)   
            grenade_body_color = self.color    


        pygame.draw.circle(temp_surface, fill_color, (temp_center, temp_center), self.blast_radius)
        pygame.draw.circle(temp_surface, outline_color, (temp_center, temp_center), self.blast_radius, 2) 

        blit_pos = (grenade_center[0] - temp_center, grenade_center[1] - temp_center)
        surface.blit(temp_surface, blit_pos)
        
        pygame.draw.ellipse(surface, grenade_body_color, offset_rect)

    def _grenade_is_boom(self, world, camera):
        # эффекты оставляемые гранатой
        for _ in range(5): world.effects.append(SparkEffect(self.rect.centerx, self.rect.centery, (255, 100, 50)))
        camera.add_shake(25) 
        
        for enemy in world.enemies[:]:
            enemy_pos = pygame.math.Vector2(enemy.rect.center)
            
            if self.pos.distance_to(enemy_pos) <= self.blast_radius:
                enemy.get_damage(200)                
                push_dir = enemy_pos - self.pos
            
                if push_dir.magnitude() > 0:
                    enemy.knockback += push_dir.normalize() * 1500
        
        world.grenades.remove(self)
