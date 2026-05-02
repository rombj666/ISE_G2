import pygame

from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    platforms = [
        pygame.Rect(120, 620, 360, 40),
        pygame.Rect(560, 520, 260, 35),
        pygame.Rect(900, 430, 240, 35),
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((18, 20, 30))

        for platform in platforms:
            pygame.draw.rect(screen, (120, 120, 130), platform)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
