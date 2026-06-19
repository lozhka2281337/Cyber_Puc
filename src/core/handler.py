import pygame

class Handler:
    def __init__(self, player, world):
        self.player = player

        self.world = world
        self.walls = world.walls
        self.bullets = world.bullets
        self.enemies = world.enemies
        self.effects = world.effects
        self.grenades = world.grenades
        self.pings = world.pings

    def game_process_events(self, game, camera_x: float, camera_y: float):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    game.toggle_inventory()

                if event.key == pygame.K_ESCAPE:
                    if game.player.inventory.is_open:
                        game.toggle_inventory()
                    else:
                        game.running = False

                if not game.player.inventory.is_open:
                    if event.key == pygame.K_q:
                        self.player.ping(self.world)

            if event.type == pygame.MOUSEBUTTONDOWN and not game.player.inventory.is_open:
                if event.button == 4:
                    self.player.switch_weapon(forward=False)
                if event.button == 5:
                    self.player.switch_weapon(forward=True)
                if event.button == 1:
                    self.player.shot(camera_x, camera_y, game.world)

    def menu_process_events(self, game) -> str | None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False

            # Наведение мыши автоматически меняет выбранный пункт
            if event.type == pygame.MOUSEMOTION:
                game.menu.update_selection_by_mouse()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                    game.menu.update_selection_by_keyboard(event)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return game.menu.handle_space()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
               return game.menu.handle_left_mouse_button()

        return None

