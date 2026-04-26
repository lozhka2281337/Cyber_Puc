import pygame
from .bullet import Bullet

#БАЗОВЫЙ КЛАСС (Родитель) 
class Weapon:
    def __init__(self, name, damage, radius, clip, shot_delay):
        self.name = name          
        self.damage = damage
        self.radius = radius
        self.clip = clip     
        self.shot_delay = shot_delay
        self.last_shot_time = 0

    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:

        return []

    def update(self):

        pass


#НАСЛЕДНИК: ОГНЕСТРЕЛЬНОЕ ОРУЖИЕ (Пистолет, Дробовик)
class GunWeapon(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, b_speed, b_color, spread=0, count=1, b_range=None):
        super().__init__(name, damage, radius, clip, shot_delay)
        
        self.b_speed = b_speed    
        self.b_color = b_color   
        self.spread = spread      
        self.count = count        
        self.b_range = b_range   

    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < self.shot_delay:
            return [] 

        self.last_shot_time = current_time

        mx, my = pygame.mouse.get_pos()
        target_x, target_y = mx + camera_x, my + camera_y
        start_x, start_y = player_pos.x + 16, player_pos.y + 16

        bullets = []
        for i in range(self.count):
            angle = 0
            if self.count > 1:
                angle = (i - (self.count - 1) / 2) * self.spread

            b = Bullet(start_x, start_y, target_x, target_y, 
                       self.b_speed, self.b_color, self.damage, angle, self.b_range)
    
            bullets.append(b)

        return bullets


# НАСЛЕДНИК: ЛАЗЕРНОЕ ОРУЖИЕ 
class LaserWeapon(Weapon):
    def __init__(self, name, damage, radius, clip, shot_delay, duration, beam_width, color, charge_time=400):
        super().__init__(name, damage, radius, clip, shot_delay)
        
        self.duration = duration      
        self.beam_width = beam_width  
        self.color = color            
        self.charge_time = charge_time 
        
        self.is_charging = False
        self.is_firing = False
        self.active_timer = 0
        
        self.locked_dir = pygame.math.Vector2(0, 0)

    def shot(self, player_pos, camera_x: float, camera_y: float) -> list:
        current_time = pygame.time.get_ticks()
        
        if self.is_firing or self.is_charging or current_time - self.last_shot_time < self.shot_delay:
            return []

        self.last_shot_time = current_time
        
        self.is_charging = True
        self.active_timer = current_time + self.charge_time
        
        mx, my = pygame.mouse.get_pos()
        target_world = (mx + camera_x, my + camera_y)
        start_center = (player_pos.x + 16, player_pos.y + 16)
        dir_vec = pygame.math.Vector2(target_world[0] - start_center[0], target_world[1] - start_center[1])
        
        if dir_vec.magnitude() > 0:
            self.locked_dir = dir_vec.normalize()
        else:
            self.locked_dir = pygame.math.Vector2(1, 0)
            
        return []

    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.is_charging:
            if current_time > self.active_timer:
                self.is_charging = False
                self.is_firing = True
                self.active_timer = current_time + self.duration 
                
        elif self.is_firing:
            if current_time > self.active_timer:
                self.is_firing = False