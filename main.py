import pygame

from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE
from src.player import Player


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    player = Player(100, 500)

    platforms = [
        pygame.Rect(0, 650, 1280, 70),
        pygame.Rect(300, 520, 200, 30),
        pygame.Rect(650, 430, 220, 30),
    ]

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update(dt, platforms)

        screen.fill((18, 20, 30))

        for platform in platforms:
            pygame.draw.rect(screen, (120, 120, 130), platform)

        pygame.draw.rect(screen, (180, 220, 255), player.rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
