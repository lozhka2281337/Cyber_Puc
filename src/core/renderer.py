import pygame

import config as cfg


class Renderer:
    def __init__(self, screen, player, world):
        self.screen = screen
        self.player = player

        self.world = world

        self.walls = world.walls
        self.bullets = world.bullets
        self.effects = world.effects
        self.grenades = world.grenades
        self.enemies = world.enemies
        self.pings = world.pings
        self.items = world.items
        self.matrix = world.matrix

        self.FONT = pygame.font.SysFont("Arial", 32, bold=True)
        self.map_surface = pygame.Surface((cfg.MAP_WIDTH * cfg.TILE_SIZE, cfg.MAP_HEIGHT * cfg.TILE_SIZE), pygame.SRCALPHA)


        #Загружаем спрайт для пола
        floor_lvl1 = pygame.image.load("assets/FloorLvl1.png").convert_alpha()
        self.floor_lvl1 = pygame.transform.scale(floor_lvl1, (cfg.TILE_SIZE, cfg.TILE_SIZE))

        #Загружаем спрайт для стен
        wall_lvl1 = pygame.image.load("assets/WallLvl1.png").convert_alpha()
        self.wall_lvl1 = pygame.transform.scale(wall_lvl1, (cfg.TILE_SIZE, cfg.TILE_SIZE))

        # Загружаем спрайт для отображения HP
        self.hp_sprite = pygame.image.load("assets/Hp.png").convert_alpha()
        self.hp_width = self.hp_sprite.get_width()

        self._init_map_surface()

        # маска для темноты
        self.darkness_mask = self._create_darkness_mask()

    def _init_map_surface(self):
        for y in range(cfg.MAP_HEIGHT):
            for x in range(cfg.MAP_WIDTH):
                if self.matrix[y][x] == 0:
                    self.map_surface.blit(self.floor_lvl1, (x * cfg.TILE_SIZE, y * cfg.TILE_SIZE))

        """ стены """
        for wall in self.walls:
            self.map_surface.blit(self.wall_lvl1, (wall.x, wall.y))


    def _draw_hp(self):
        """Рисуем столько спрайтов HP, сколько здоровья у игрока"""
        margin_x = 10  # отступ слева
        margin_y = 10  # отступ сверху
        spacing = 5  # расстояние между иконками

        for i in range(self.player.hp):
            x = margin_x + i * (self.hp_width + spacing)
            y = margin_y
            self.screen.blit(self.hp_sprite, (x, y))


    def draw_death_screen(self):
        self.screen.fill((0, 0, 0))

        death_msg = self.FONT.render("GAME OVER", True, (255, 255, 255))
        self.screen.blit(death_msg, (cfg.SCREEN_WIDTH // 2 - 100, cfg.SCREEN_HEIGHT // 2))
        pygame.display.flip()

        pygame.time.wait(3000)

    def _draw_weapon_hud(self):
        start_x = cfg.SCREEN_WIDTH - 220
        start_y = cfg.SCREEN_HEIGHT - 80

        for i in range(len(self.player.inventory.weapons)):
            weapon = self.player.inventory.weapons[i]
            is_active = (i == self.player.inventory.current_idx)
            offset_y = (i - self.player.inventory.current_idx) * -35
            w_color = getattr(weapon, 'b_color', getattr(weapon, 'color', (255, 255, 255)))

            if is_active:
                text_surf = self.FONT.render(f"> {weapon.name}", True, w_color)
            else:
                text_surf = self.FONT.render(weapon.name, True, (120, 120, 120))
                text_surf.set_alpha(150)
            self.screen.blit(text_surf, (start_x, start_y + offset_y))

    def _draw_weapon(self, camera_x, camera_y):
        weapon = self.player.inventory.get_current()
        if hasattr(weapon, 'draw'):
            weapon.draw(self.screen, camera_x, camera_y, self.player.rect, self.walls)

    def _draw_ping_interface(self):
        font = pygame.font.SysFont(None, 24)

        status_text = "PING ГОТОВ [Q]"
        text_color = cfg.PING_COLOR

        if self.player.ping_timer > 0:

            status_text = f"СКАНИРОВАНИЕ... {round(self.player.ping_timer * 10 / cfg.FPS, 2)}"
            text_color = (100, 100, 100)

        self.screen.blit(font.render(status_text, True, text_color), (10, 60))

    def _create_darkness_mask(self, width=cfg.SCREEN_WIDTH, height=cfg.SCREEN_HEIGHT, radius=cfg.DARKNESS_RADIUS) -> pygame.Surface:
        # Создаем поверхность размером с экран с поддержкой прозрачности 
        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        # Заливаем всю маску полностью черным цветом
        mask.fill((0, 0, 0, cfg.DARKNESS_DEGREE)) 

        for r in range(radius, 0, -2):
            alpha = int(cfg.DARKNESS_DEGREE * (r / radius))
            pygame.draw.circle(mask, (0, 0, 0, alpha), (width // 2, height // 2), r)
            
        return mask

    def draw(self, camera_x, camera_y):
        """ карта """
        self.screen.fill(cfg.FLOOR_COLOR)
        self.screen.blit(self.map_surface, (-camera_x, -camera_y))

        """ атака оружия игрока """
        self._draw_weapon(camera_x, camera_y)

        """ ентити """
        for item in self.items:
            item.draw(self.screen, camera_x, camera_y)

        for bullet in self.bullets:
            bullet.draw(self.screen, camera_x, camera_y)

        for grenade in self.grenades:
            grenade.draw(self.screen, camera_x, camera_y)

        for enemy in self.enemies:
            if enemy.visible_timer <= 0:
                enemy.draw(self.screen, camera_x, camera_y)

        self.player.draw(self.screen, camera_x, camera_y)

        for effect in self.effects:
            effect.draw(self.screen, camera_x, camera_y)

        if self.world.mod == cfg.DARK_MOD:
            for ping in self.pings:
                ping.draw(self.screen, camera_x, camera_y)

            # рисуем темноту вокруг игрока
            self.screen.blit(self.darkness_mask, (0, 0))

            # рисуем врагов, которые попали под пинг
            for enemy in self.enemies:
                if enemy.visible_timer > 0.0:
                    enemy.draw(self.screen, camera_x, camera_y)

            self._draw_ping_interface()

        """ интерфейс """
        self._draw_hp()
        self._draw_weapon_hud()

        pygame.display.flip()