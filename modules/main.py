import os
import sys
import pygame
import settings
from pipboy import PipBoy
from input_manager import InputManager

def main():
    """Main entry point for the Pip-Boy application."""
    if settings.RASPI:
        os.environ["SDL_VIDEODRIVER"] = "x11"
        os.environ["DISPLAY"] = ":0"
        os.environ["SDL_AUDIODRIVER"] = "alsa"
    
    pygame.init()
    pygame.mixer.init(
        frequency=44100,
        size=-16,
        channels=2,
        buffer=4096,
        devicename='bcm2835 HDMI 1'
    )
    
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.FULLSCREEN if settings.RASPI else 0)
    print(pygame.display.get_driver())
    pygame.mouse.set_visible(False)
    pygame.display.set_caption("Pip-Boy")
    
    clock = pygame.time.Clock()
    input_manager = InputManager()
    pipboy = PipBoy(screen, clock, input_manager)
    
    # Appel direct, pas de thread !
    pipboy.run()

if __name__ == "__main__":
    main()
