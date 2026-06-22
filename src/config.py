import pygame

""" общие настройки """
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080

FPS = 60
BLACK = (20, 20, 25)
WHITE = (255, 255, 255)
BLUE_WALL = (100, 150, 200)

MAP_WIDTH = 80
MAP_HEIGHT = 60

SPAWN_ENEMY_EVENT = pygame.event.custom_type()
SPAWN_ENEMY_TIME = 1800

""" шрифты """
title_font = pygame.font.SysFont("Courier New", 50, bold=True)
menu_font = pygame.font.SysFont("Courier New", 24, bold=True)
info_font = pygame.font.SysFont("Courier New", 20)
font_terminal = pygame.font.SysFont("Courier New", 18, bold=True)
arial_font = pygame.font.SysFont("Arial", 32, bold=True)
none_font = pygame.font.SysFont(None, 32, bold=True)


""" музыка """
MENU_MUSIC = "music/Crowbar_-_To_Touch_The_Hand_Of_God_(SkySound.cc).mp3"
ACTION_MUSIC = "music/doom_02.Rip_and_Tear.mp3"


""" состояния игры """
NORMAL_MOD = "normal"
DARK_MOD = "stels"
INTRO_MOD = "intro"


""" карта """
TILE_SIZE = 40

FLOOR_COLOR = (0, 0, 0)


""" степень темноты """
DARKNESS_DEGREE = 240
DARKNESS_RADIUS = 250


""" BSP генерация """
MIN_LEAF_SIZE = 20
MAX_LEAF_SIZE = 30

MIN_ROOM_SIZE = 10
MAX_ROOM_SIZE = 20
HALL_WIDTH = 3

PARTIES_RELATIONSHIP = 1.25
SPLIT_BIG_LEAF_RELATIONSHIP = 0.25


""" игрок """
PLAYER_SPEED = 350
PLAYER_HP = 5
PLAYER_SIZE = 32
PLAYER_COLOR = (0, 255, 100)
SHOT_DELAY = 300
INVULNERABLE_TIMER = 3.0


""" оружие """
SCANNER = "Scanner"
FIREWALL = "Firewall"
DEFRAG = "Defrag" 
MELEE = "USB-Katana" 
ZIP_BOMB = "Zip-Bomb"


""" пинг """
PING_TIMER = 2.0 
PING_COLOR = (0, 200, 255)
PING_START_RADIUS = 10
PING_MAX_RADIUS = 500 
PING_SPEED = 450

""" враги """
ENEMY_SIZE = 32
ENEMY_VISIBLE_TIME = 2.0 # время видимости после активации пинга

# 1. Swarm (Бегун)
ENEMY_SWARM_HP = 50
ENEMY_SWARM_SPEED = 250
ENEMY_SWARM_COLOR = (0, 255, 0)
ENEMY_SWARM_ATTACK_RANGE = 35

# 2. Tank (Танк) 
ENEMY_TANK_HP = 500
ENEMY_TANK_SPEED = 150
ENEMY_TANK_COLOR = (200, 0, 50) 
ENEMY_TANK_ATTACK_RANGE = 50    
ENEMY_TANK_DAMAGE = 3      

# 3. Shooter (Стрелок)
ENEMY_SHOOTER_HP = 100
ENEMY_SHOOTER_SPEED = 100
ENEMY_SHOOTER_COLOR = (0, 255, 255)
ENEMY_SHOOTER_ATTACK_RANGE = 250   
ENEMY_SHOOTER_DAMAGE = 1

# рядовые 
ENEMY_NORMAL_HP = 150
ENEMY_NORMAL_COLOR = (255, 50, 50)


""" айтемы """
HEALTH_PACK_SIZE = 20
HEALTH_PACK_COLOR = (255, 50, 50)


""" пули """
BULLET_SIZE = 10
BULLET_SPEED = 800
BULLET_COLOR = (255, 255, 0) 


""" ИИ Врагов """
AGRO_DISTANCE = 350         # Дистанция, с которой видит игрока
LOSE_AGRO_DISTANCE = 600    # Дистанция, на которой забывает игрока
WAYPOINT_TOLERANCE = 10     # Погрешность прибытия на точку (в пикселях)

INITIAL_ENEMY_COUNT = 15    # Точное количество врагов при генерации уровня 


""" меню """
COLOR_BG = (10, 12, 18)
COLOR_TEXT_MUTED = (70, 80, 95)
COLOR_NEON_GREEN = (0, 255, 120)
COLOR_NEON_BLUE = (0, 200, 255)
COLOR_NEON_RED = (255, 50, 80)

GAME_TITLE = "CYBER_PUK: 2067"
START_GAME_BUTTON = "НАЧАТЬ"
SETTINGS_BUTTON = "НАСТРОЙКИ"
EXIT_BUTTON = "ВЫЙТИ"
DEFAULT_MENU_BUTTON = "МЕНЮ"
VOLUME_BUTTON = "ГРОМКОСТЬ"
BACK_BUTTON = "НАЗАД"
CONTINUE_BUTTON = "ПРОДОЛЖИТЬ"