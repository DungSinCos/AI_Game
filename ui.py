# ui.py
import pygame
import sys
from pygame.locals import *
from game_logic import GameState
from ai import bfs, dfs, astar, hint, get_solution_info
import json
import os


class Button:
    """Lớp Button cho Pygame"""

    def __init__(self, x, y, width, height, text, color, hover_color, text_color, font, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.callback = callback
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class GameUI:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.clock = pygame.time.Clock()

        # Load level data
        self.load_levels()

        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 36)
        self.info_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.DARK_GRAY = (100, 100, 100)
        self.GREEN = (100, 200, 100)
        self.DARK_GREEN = (50, 150, 50)
        self.BLUE = (100, 150, 255)
        self.DARK_BLUE = (50, 100, 200)
        self.RED = (255, 100, 100)
        self.DARK_RED = (200, 50, 50)
        self.ORANGE = (255, 200, 100)
        self.PURPLE = (200, 100, 255)
        self.BROWN = (139, 69, 19)
        self.LIGHT_BROWN = (205, 133, 63)

        # Game state
        self.current_screen = "start"  # start, level_menu, game
        self.current_level = 1
        self.game_state = None
        self.selected_characters = []
        self.boat_x = 0
        self.boat_y = 0
        self.steps = 0
        self.start_time = 0
        self.time_elapsed = 0

        # Animation
        self.animating = False
        self.animation_target_x = 0
        self.animation_step = 0

        # Images
        self.images = {}
        self.load_images()

        # Buttons
        self.buttons = []

    def load_levels(self):
        """Load level data từ level.py"""
        try:
            from level import levels
            self.levels = levels
        except:
            print("Error loading levels")
            self.levels = []

    def load_images(self):
        """Load images từ thư mục assets"""
        image_files = {
            "bg": "bg.png",
            "boat": "boat.png",
            "person": "person.png",
            "human": "person.png",
            "scientist": "scientist.png",
            "robot": "robot.png",
            "wolf": "wolf.png",
            "tiger": "tiger.png",
            "sheep": "sheep.png",
            "cabbage": "cabbage.png",
            "bomb": "bomb.png",
            "bomb1": "bomb.png",
            "bomb2": "bomb.png",
            "start_bg": "start.png"
        }

        # Kích thước ảnh
        char_size = (80, 80)
        boat_size = (200, 120)

        for key, filename in image_files.items():
            try:
                path = os.path.join("assets", filename)
                img = pygame.image.load(path)
                if key == "boat":
                    img = pygame.transform.scale(img, boat_size)
                elif key in ["bg", "start_bg"]:
                    img = pygame.transform.scale(img, (self.screen_width, self.screen_height))
                else:
                    img = pygame.transform.scale(img, char_size)
                self.images[key] = img
            except:
                print(f"Could not load image: {filename}")
                # Tạo hình chữ nhật thay thế
                surf = pygame.Surface(char_size if key != "boat" else boat_size)
                surf.fill(self.GRAY)
                self.images[key] = surf

    def handle_event(self, event):
        """Xử lý sự kiện"""
        if self.current_screen == "start":
            self.handle_start_event(event)
        elif self.current_screen == "level_menu":
            self.handle_level_menu_event(event)
        elif self.current_screen == "game":
            self.handle_game_event(event)

    def handle_start_event(self, event):
        """Xử lý sự kiện màn hình start"""
        for button in self.buttons:
            button.handle_event(event)

    def handle_level_menu_event(self, event):
        """Xử lý sự kiện màn hình chọn level"""
        for button in self.buttons:
            button.handle_event(event)

    def handle_game_event(self, event):
        """Xử lý sự kiện trong game"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.animating:
            mouse_pos = pygame.mouse.get_pos()

            # Kiểm tra click vào nhân vật
            self.check_character_click(mouse_pos)

        # Xử lý button
        for button in self.buttons:
            button.handle_event(event)

    def check_character_click(self, mouse_pos):
        """Kiểm tra click vào nhân vật"""
        if not self.game_state:
            return

        boat_side = self.game_state.get_boat_side()
        characters = self.game_state.characters

        # Vị trí các nhân vật trên màn hình
        char_positions = self.get_character_positions()

        for char in characters:
            if char in char_positions:
                x, y = char_positions[char]
                char_rect = pygame.Rect(x - 40, y - 40, 80, 80)

                if char_rect.collidepoint(mouse_pos):
                    char_idx = self.game_state.name_to_idx[char]

                    # Kiểm tra nhân vật có ở cùng bờ với thuyền không
                    if self.game_state.state[char_idx] == boat_side:
                        if char in self.selected_characters:
                            self.selected_characters.remove(char)
                        elif len(self.selected_characters) < self.game_state.boat_config.get("capacity", 2):
                            self.selected_characters.append(char)

    def get_character_positions(self):
        """Lấy vị trí các nhân vật trên màn hình"""
        positions = {}

        if not self.game_state:
            return positions

        boat_side = self.game_state.get_boat_side()
        state = self.game_state.state
        characters = self.game_state.characters

        # Vị trí bờ trái và phải
        left_x = self.screen_width * 0.2
        right_x = self.screen_width * 0.8

        # Các vị trí y cho từng nhân vật
        y_positions = [self.screen_height * 0.2 + i * 100 for i in range(len(characters))]

        for i, char in enumerate(characters):
            side = state[i]
            x = left_x if side == 0 else right_x

            # Nếu nhân vật đang được chọn và ở cùng bờ thuyền
            if char in self.selected_characters:
                # Vẽ trên thuyền
                x = self.boat_x + (self.selected_characters.index(char) - 0.5) * 60
                y = self.boat_y + 30
            else:
                y = y_positions[i % len(y_positions)]

            positions[char] = (x, y)

        return positions

    def update(self):
        """Cập nhật game state"""
        mouse_pos = pygame.mouse.get_pos()

        # Cập nhật button states
        for button in self.buttons:
            button.update(mouse_pos)

        # Cập nhật animation
        if self.animating:
            self.update_animation()

        # Cập nhật timer
        if self.current_screen == "game" and self.game_state and not self.animating:
            self.time_elapsed = pygame.time.get_ticks() // 1000 - self.start_time

    def update_animation(self):
        """Cập nhật animation di chuyển thuyền"""
        if self.animation_step > 0:
            self.boat_x += self.animation_step
            if (self.animation_step > 0 and self.boat_x >= self.animation_target_x) or \
                    (self.animation_step < 0 and self.boat_x <= self.animation_target_x):
                self.boat_x = self.animation_target_x
                self.animating = False
                self.finish_move()

    def draw(self):
        """Vẽ toàn bộ màn hình"""
        if self.current_screen == "start":
            self.draw_start()
        elif self.current_screen == "level_menu":
            self.draw_level_menu()
        elif self.current_screen == "game":
            self.draw_game()

        pygame.display.flip()

    def draw_start(self):
        """Vẽ màn hình start"""
        # Background
        if "start_bg" in self.images:
            self.screen.blit(self.images["start_bg"], (0, 0))
        else:
            self.screen.fill(self.LIGHT_BROWN)

        # Title
        title_text = self.title_font.render("RIVER CROSSING GAME", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        self.screen.blit(title_text, title_rect)

        # Buttons
        self.buttons = []
        play_button = Button(
            self.screen_width // 2 - 100,
            self.screen_height // 2,
            200, 60,
            "PLAY GAME",
            self.GREEN, self.DARK_GREEN, self.WHITE,
            self.button_font,
            self.show_level_menu
        )
        self.buttons.append(play_button)

        for button in self.buttons:
            button.draw(self.screen)

    def draw_level_menu(self):
        """Vẽ màn hình chọn level"""
        self.screen.fill(self.LIGHT_BROWN)

        # Title
        title_text = self.title_font.render("SELECT LEVEL", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title_text, title_rect)

        # Level buttons
        self.buttons = []
        level_colors = [
            (143, 188, 143), (152, 251, 152), (0, 250, 154), (60, 179, 113), (46, 139, 87),
            (32, 178, 170), (102, 205, 170), (95, 158, 160), (70, 130, 180), (30, 144, 255)
        ]

        start_x = self.screen_width // 2 - 300
        start_y = 150
        button_width = 120
        button_height = 80
        spacing = 20

        for i in range(10):
            row = i // 5
            col = i % 5
            x = start_x + col * (button_width + spacing)
            y = start_y + row * (button_height + spacing)

            def make_callback(level):
                return lambda: self.start_game(level)

            btn = Button(
                x, y, button_width, button_height,
                f"Level {i + 1}",
                level_colors[i], self.DARK_GRAY, self.WHITE,
                self.button_font,
                make_callback(i + 1)
            )
            self.buttons.append(btn)

        # Back button
        back_button = Button(
            self.screen_width // 2 - 50,
            self.screen_height - 80,
            100, 50,
            "BACK",
            self.RED, self.DARK_RED, self.WHITE,
            self.button_font,
            self.show_start
        )
        self.buttons.append(back_button)

        for button in self.buttons:
            button.draw(self.screen)

    def draw_game(self):
        """Vẽ màn hình game"""
        if not self.game_state:
            return

        # Background
        if "bg" in self.images:
            self.screen.blit(self.images["bg"], (0, 0))
        else:
            self.screen.fill((135, 206, 235))  # Sky blue
            # Vẽ sông
            pygame.draw.rect(self.screen, (100, 149, 237),
                             (0, self.screen_height // 2 - 50,
                              self.screen_width, 100))

        # Vẽ bờ trái và phải
        left_shore = pygame.Rect(0, 0, self.screen_width * 0.25, self.screen_height)
        right_shore = pygame.Rect(self.screen_width * 0.75, 0,
                                  self.screen_width * 0.25, self.screen_height)
        pygame.draw.rect(self.screen, (139, 69, 19), left_shore)
        pygame.draw.rect(self.screen, (139, 69, 19), right_shore)

        # Vẽ thuyền
        boat_rect = self.images["boat"].get_rect(center=(self.boat_x, self.boat_y))
        self.screen.blit(self.images["boat"], boat_rect)

        # Vẽ các nhân vật
        char_positions = self.get_character_positions()
        for char, pos in char_positions.items():
            if char in self.images:
                char_rect = self.images[char].get_rect(center=pos)
                self.screen.blit(self.images[char], char_rect)

                # Vẽ khung chọn
                if char in self.selected_characters:
                    pygame.draw.rect(self.screen, self.RED, char_rect, 3)

        # Vẽ panel điều khiển bên phải
        control_panel = pygame.Rect(self.screen_width - 250, 0, 250, self.screen_height)
        pygame.draw.rect(self.screen, (200, 200, 200), control_panel)
        pygame.draw.rect(self.screen, (100, 100, 100), control_panel, 2)

        # Vẽ các button
        self.buttons = []
        button_y = 80
        button_spacing = 60

        buttons_config = [
            ("MOVE", self.GREEN, self.DARK_GREEN, self.move_boat),
            ("HINT", self.ORANGE, (200, 150, 50), self.use_hint),
            ("BFS", self.BLUE, self.DARK_BLUE, self.solve_bfs),
            ("DFS", self.PURPLE, (150, 50, 200), self.solve_dfs),
            ("A*", self.GREEN, self.DARK_GREEN, self.solve_astar),
            ("RESET", self.RED, self.DARK_RED, self.reset_game),
            ("MENU", self.BROWN, (100, 50, 20), self.show_start)
        ]

        for text, color, hover_color, callback in buttons_config:
            btn = Button(
                self.screen_width - 225, button_y,
                200, 45,
                text, color, hover_color, self.WHITE,
                self.button_font,
                callback
            )
            self.buttons.append(btn)
            button_y += button_spacing

        # Vẽ thông tin
        info_y = button_y + 20

        # Timer
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        timer_text = self.info_font.render(f"Time: {minutes:02d}:{seconds:02d}",
                                           True, self.BLACK)
        self.screen.blit(timer_text, (self.screen_width - 225, info_y))
        info_y += 35

        # Steps
        steps_text = self.info_font.render(f"Steps: {self.steps}", True, self.BLACK)
        self.screen.blit(steps_text, (self.screen_width - 225, info_y))
        info_y += 35

        # Level
        level_text = self.info_font.render(f"Level: {self.game_state.level}",
                                           True, self.BLACK)
        self.screen.blit(level_text, (self.screen_width - 225, info_y))
        info_y += 35

        # Trạng thái các nhân vật
        state_text = self.info_font.render("Characters:", True, self.BLACK)
        self.screen.blit(state_text, (self.screen_width - 225, info_y))
        info_y += 25

        for char in self.game_state.characters:
            side = self.game_state.state[self.game_state.name_to_idx[char]]
            side_text = "RIGHT" if side == 1 else "LEFT"
            char_text = self.small_font.render(f"{char}: {side_text}",
                                               True, self.BLACK)
            self.screen.blit(char_text, (self.screen_width - 225, info_y))
            info_y += 25

        # Vẽ các button
        for button in self.buttons:
            button.draw(self.screen)

    def show_start(self):
        """Hiển thị màn hình start"""
        self.current_screen = "start"
        self.selected_characters = []

    def show_level_menu(self):
        """Hiển thị màn hình chọn level"""
        self.current_screen = "level_menu"
        self.selected_characters = []

    def start_game(self, level):
        """Bắt đầu game với level được chọn"""
        try:
            level_data = self.levels[level - 1]
            self.game_state = GameState(level_data)
            self.current_level = level
            self.current_screen = "game"
            self.selected_characters = []
            self.steps = 0
            self.start_time = pygame.time.get_ticks() // 1000
            self.time_elapsed = 0

            # Cập nhật vị trí thuyền
            boat_side = self.game_state.get_boat_side()
            self.boat_x = self.screen_width * 0.35 if boat_side == 0 else self.screen_width * 0.65
            self.boat_y = self.screen_height * 0.6

        except Exception as e:
            print(f"Error starting game: {e}")

    def reset_game(self):
        """Reset game về trạng thái ban đầu"""
        self.start_game(self.current_level)

    def move_boat(self):
        """Di chuyển thuyền"""
        if self.animating:
            return

        # Kiểm tra có người lái không
        drivers = self.game_state.boat_config.get("drivers", [])
        requires_driver = self.game_state.boat_config.get("requires_driver", False)

        if requires_driver:
            if not any(driver in self.selected_characters for driver in drivers):
                self.show_message("Need a driver!", self.RED)
                return

        # Chuyển selected characters sang indices
        move_indices = [self.game_state.name_to_idx[char]
                        for char in self.selected_characters]

        # Thử di chuyển
        new_state = self.game_state.move(move_indices)

        if new_state:
            # Bắt đầu animation
            self.animating = True
            current_side = self.game_state.get_boat_side()
            self.animation_target_x = self.screen_width * 0.65 if current_side == 0 else self.screen_width * 0.35
            self.animation_step = 10 if self.animation_target_x > self.boat_x else -10
            self.game_state = new_state
            self.steps += 1
        else:
            self.show_message("Invalid move!", self.RED)
            self.selected_characters = []

    def finish_move(self):
        """Kết thúc animation và kiểm tra win/lose"""
        self.selected_characters = []

        # Kiểm tra win
        if self.game_state.is_goal():
            self.show_message(f"Congratulations! You completed Level {self.current_level}!",
                              self.GREEN)
            self.show_level_menu()

        # Kiểm tra bomb timer
        if self.game_state.bomb_timer is not None and self.game_state.bomb_timer <= 0:
            self.show_message("BOOM! The bomb exploded!", self.RED)
            self.reset_game()

    def use_hint(self):
        """Sử dụng hint"""
        if self.animating:
            return

        next_state = hint(self.game_state)
        if next_state:
            self.game_state = next_state
            self.steps += 1
            self.draw()

            if self.game_state.is_goal():
                self.show_message(f"Congratulations! You completed Level {self.current_level}!",
                                  self.GREEN)
                self.show_level_menu()
        else:
            self.show_message("No hint available!", self.RED)

    def solve_bfs(self):
        """Giải bằng BFS"""
        if self.animating:
            return

        solution = bfs(self.game_state)
        if solution:
            self.animate_solution(solution)
        else:
            self.show_message("No solution found with BFS!", self.RED)

    def solve_dfs(self):
        """Giải bằng DFS"""
        if self.animating:
            return

        solution = dfs(self.game_state)
        if solution:
            self.animate_solution(solution)
        else:
            self.show_message("No solution found with DFS!", self.RED)

    def solve_astar(self):
        """Giải bằng A*"""
        if self.animating:
            return

        solution = astar(self.game_state)
        if solution:
            self.animate_solution(solution)
        else:
            self.show_message("No solution found with A*!", self.RED)

    def animate_solution(self, solution, index=1):
        """Animate solution từ AI"""
        if index >= len(solution):
            self.animating = False
            return

        prev_state = solution[index - 1]
        curr_state = solution[index]

        # Tìm các nhân vật đã di chuyển
        moved_chars = []
        for i, (prev, curr) in enumerate(zip(prev_state.state, curr_state.state)):
            if prev != curr:
                moved_chars.append(curr_state.idx_to_name[i])

        # Đảm bảo có người lái
        drivers = self.game_state.boat_config.get("drivers", [])
        if not any(driver in moved_chars for driver in drivers):
            for driver in drivers:
                if driver in curr_state.name_to_idx:
                    moved_chars.append(driver)
                    break

        self.selected_characters = moved_chars

        def after_move():
            self.animate_solution(solution, index + 1)

        self.move_boat_with_callback(after_move)

    def move_boat_with_callback(self, callback):
        """Di chuyển thuyền với callback sau khi hoàn thành"""
        if self.animating:
            return

        move_indices = [self.game_state.name_to_idx[char]
                        for char in self.selected_characters]

        new_state = self.game_state.move(move_indices)

        if new_state:
            self.animating = True
            current_side = self.game_state.get_boat_side()
            self.animation_target_x = self.screen_width * 0.65 if current_side == 0 else self.screen_width * 0.35
            self.animation_step = 10 if self.animation_target_x > self.boat_x else -10
            self.game_state = new_state
            self.steps += 1

            # Lưu callback để gọi sau khi animation kết thúc
            self.animation_callback = callback
        else:
            self.selected_characters = []
            callback()

    def finish_move(self):
        """Kết thúc animation"""
        self.selected_characters = []

        # Gọi callback nếu có
        if hasattr(self, 'animation_callback') and self.animation_callback:
            callback = self.animation_callback
            self.animation_callback = None
            callback()

    def show_message(self, message, color):
        """Hiển thị thông báo tạm thời"""
        # Tạo surface cho message
        font = pygame.font.Font(None, 36)
        text_surface = font.render(message, True, color)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 100))

        # Vẽ background
        pygame.draw.rect(self.screen, (0, 0, 0, 128), text_rect.inflate(20, 10))
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()

        # Chờ 2 giây
        pygame.time.wait(2000)