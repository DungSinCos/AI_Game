
import pygame
import sys
from ui import GameUI


def main():
    # Khởi tạo Pygame
    pygame.init()

    # Lấy kích thước màn hình
    screen_info = pygame.display.Info()
    SCREEN_WIDTH = screen_info.current_w
    SCREEN_HEIGHT = screen_info.current_h

    # Tạo cửa sổ với kích thước fullscreen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("River Crossing Game")

    # Set icon (nếu có)
    try:
        icon = pygame.image.load("assets/icon.png")
        pygame.display.set_icon(icon)
    except:
        pass

    # Tạo đối tượng game UI
    game_ui = GameUI(screen)

    # Clock để kiểm soát FPS
    clock = pygame.time.Clock()
    FPS = 60

    # Biến điều khiển game loop
    running = True

    # Game loop
    while running:
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            # Chuyển event cho GameUI xử lý
            game_ui.handle_event(event)

        # Cập nhật game logic
        game_ui.update()

        # Vẽ màn hình
        game_ui.draw()

        # Cập nhật màn hình
        pygame.display.flip()

        # Giới hạn FPS
        clock.tick(FPS)

    # Thoát Pygame
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()