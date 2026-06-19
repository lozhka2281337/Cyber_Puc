import pygame

if __name__ == "__main__":
    pygame.init()

    from core.game import Game
    
    game = Game()
    game.run_menu()