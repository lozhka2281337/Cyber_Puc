from weapon.grenade_launcher import GrenadeLauncher
from weapon.gun import Gun
from weapon.laser import Laser
from weapon.mele import Melee


class Inventory:
    def __init__(self):
        self.weapons = [
            Gun("Scanner", 50, 20, 10, 400, 800, (255, 255, 0)), 
            Gun("Firewall", 50, 20, 5, 1100, 550, (255, 100, 0), spread=15, count=5, b_range=280), 
            Laser("Defrag", 100, 20, 1, 2500, duration=800, beam_width=14, color=(0, 255, 255), charge_time=400),
            Melee("USB-Katana", 150, 20, 1, 400, reach=70, arc_degrees=140, color=(255, 255, 255)),
            GrenadeLauncher("Zip-Bomb", 20, 1, 1000, throw_speed=400, blast_radius=70, fuse_time=1000, max_range=350)
        ]
        self.current_idx = 0
        self.is_open = False



    def get_current(self):
        return self.weapons[self.current_idx]

    def next_weapon(self):
        self.current_idx = (self.current_idx + 1) % len(self.weapons)

    def prev_weapon(self):
        self.current_idx = (self.current_idx - 1) % len(self.weapons)
        
    def update_all(self):
        for weapon in self.weapons:
            weapon.update()


    def toggle(self):
        """Переключение состояния инвенторя"""
        self.is_open = not self.is_open