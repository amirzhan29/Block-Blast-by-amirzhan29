import pygame
import sys
import random
try:
    import winsound
except:
    winsound = None

# Инициализация Pygame
pygame.init()

# Константы
GRID_SIZE = 8
CELL_SIZE = 45
MARGIN = 4
BOARD_OFFSET_X = 50
BOARD_OFFSET_Y = 50

# Размеры окна
WIDTH = 550
HEIGHT = 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Blast by Amirzhan")

# Цвета
BG_COLOR = (24, 24, 37)
GRID_BG = (35, 35, 50)
EMPTY_CELL = (45, 45, 65)
TEXT_COLOR = (240, 240, 240)
ACCENT_COLOR = (0, 200, 255)
BUTTON_COLOR = (80, 150, 255)
BUTTON_HOVER = (100, 180, 255)
FLASH_COLOR = (255, 255, 255)
CONGRAT_COLOR = (255, 220, 50)
GAMEOVER_BG = (20, 20, 30, 220)

# Палитра ярких цветов для фигур
SHAPE_COLORS = [
    (255, 80, 80),    # Красный
    (80, 200, 120),   # Зеленый
    (80, 150, 255),   # Синий
    (255, 200, 50),   # Желтый
    (200, 80, 255),   # Фиолетовый
    (255, 120, 50)    # Оранжевый
]

# Полный набор фигур
SHAPES = [
    [[1]],
    [[1]],
    [[1, 1]],
    [[1, 1, 1]],
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
    [[1, 0], [1, 1]],
    [[0, 1], [1, 1]],
    [[1, 1], [1, 0]],
    [[1, 1], [0, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 0], [1, 1], [0, 1]],
    [[0, 1], [1, 1], [1, 0]]
]

# Разнообразные комплименты по уровням (количеству линий)
COMPLIMENTS = {
    1: ["Great!", "Nice!", "Good!", "Cool!", "Sweet!"],
    2: ["Awesome!", "Super!", "Brilliant!", "Nice Combo!", "Well Done!"],
    3: ["Fantastic!", "Incredible!", "Amazing!", "Unbelievable!", "Masterpiece!"],
    4: ["GODLIKE!", "Legendary!", "Unstoppable!", "Mind Blowing!", "Epic!"]
}

# Заставка в консоли
STARTUP_LOGO = """
Block Blast by Amirzhan

              |\ 
              |/
"""

class Game:
    def __init__(self):
        self.state = "MENU"  # "MENU", "PLAYING", "GAMEOVER"
        self.reset_game()
        
        # Кнопки
        self.play_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 55)
        self.retry_button_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 30, 220, 50)
        self.menu_button_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 95, 220, 50)

    def reset_game(self):
        self.board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.spawn_figures()
        
        self.dragging_figure = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        self.flashing_cells = []
        self.flash_timer = 0
        
        self.current_message = ""
        self.message_timer = 0

    def spawn_figures(self):
        self.available_figures = []
        for i in range(3):
            shape = random.choice(SHAPES)
            color = random.choice(SHAPE_COLORS)
            pos_x = 40 + i * 165
            pos_y = 520
            self.available_figures.append({
                'shape': shape,
                'color': color,
                'x': pos_x,
                'y': pos_y
            })
        
        # После спавна новых фигур проверяем, есть ли вообще куда их ставить
        if not self.check_any_moves_left():
            self.state = "GAMEOVER"

    def check_any_moves_left(self):
        """Проверяет, можно ли поставить хотя бы одну из оставшихся фигур на поле"""
        for fig in self.available_figures:
            shape = fig['shape']
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if self.can_place(shape, r, c):
                        return True
        return False

    def can_place(self, shape, start_row, start_col):
        for r_idx, row in enumerate(shape):
            for c_idx, val in enumerate(row):
                if val == 1:
                    target_r = start_row + r_idx
                    target_c = start_col + c_idx
                    if target_r >= GRID_SIZE or target_c >= GRID_SIZE or target_r < 0 or target_c < 0:
                        return False
                    if self.board[target_r][target_c] != 0:
                        return False
        return True

    def draw(self, surface):
        surface.fill(BG_COLOR)
        
        if self.state == "MENU":
            self.draw_menu(surface)
        elif self.state == "PLAYING" or self.state == "GAMEOVER":
            self.draw_playing(surface)
            if self.state == "GAMEOVER":
                self.draw_game_over(surface)

    def draw_menu(self, surface):
        font_big = pygame.font.SysFont(None, 60, bold=True)
        logo_top = font_big.render("Block Blast", True, ACCENT_COLOR)
        logo_bottom = pygame.font.SysFont(None, 30).render("by Amirzhan", True, TEXT_COLOR)
        
        logo_top_rect = logo_top.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70))
        logo_bottom_rect = logo_bottom.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        
        surface.blit(logo_top, logo_top_rect)
        surface.blit(logo_bottom, logo_bottom_rect)
        
        mx, my = pygame.mouse.get_pos()
        button_color = BUTTON_HOVER if self.play_button_rect.collidepoint(mx, my) else BUTTON_COLOR
        pygame.draw.rect(surface, button_color, self.play_button_rect, border_radius=10)
        
        font_btn = pygame.font.SysFont(None, 38)
        btn_text = font_btn.render("Играть", True, TEXT_COLOR)
        btn_text_rect = btn_text.get_rect(center=self.play_button_rect.center)
        surface.blit(btn_text, btn_text_rect)

    def draw_playing(self, surface):
        if self.flash_timer > 0:
            self.flash_timer -= 1
        if self.message_timer > 0:
            self.message_timer -= 1

        # 1. Отрисовка игрового поля 8x8
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = BOARD_OFFSET_X + col * (CELL_SIZE + MARGIN)
                y = BOARD_OFFSET_Y + row * (CELL_SIZE + MARGIN)
                
                cell_val = self.board[row][col]
                
                if self.flash_timer > 0 and (row, col) in self.flashing_cells:
                    color = FLASH_COLOR
                else:
                    color = cell_val if cell_val != 0 else EMPTY_CELL
                
                pygame.draw.rect(surface, color, (x, y, CELL_SIZE, CELL_SIZE), border_radius=6)

        # 2. Отрисовка доступных фигур снизу
        for fig in self.available_figures:
            if fig != self.dragging_figure:
                self.draw_shape(surface, fig['shape'], fig['color'], fig['x'], fig['y'], scale=0.6)

        # 3. Перетаскиваемая фигура за курсором
        if self.dragging_figure:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            draw_x = mouse_x - self.drag_offset_x
            draw_y = mouse_y - self.drag_offset_y
            self.draw_shape(surface, self.dragging_figure['shape'], self.dragging_figure['color'], draw_x, draw_y, scale=1.0)

        # 4. Вывод счета
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Счет: {self.score}", True, TEXT_COLOR)
        surface.blit(score_text, (BOARD_OFFSET_X, 10))

        # 5. Вывод комплимента
        if self.message_timer > 0 and self.current_message:
            font_msg = pygame.font.SysFont(None, 48, bold=True)
            msg_surface = font_msg.render(self.current_message, True, CONGRAT_COLOR)
            msg_rect = msg_surface.get_rect(center=(WIDTH // 2, 460))
            surface.blit(msg_surface, msg_rect)

    def draw_game_over(self, surface):
        # Затемнение экрана
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 30, 210))
        surface.blit(overlay, (0, 0))

        # Текст "Проиграл"
        font_go = pygame.font.SysFont(None, 55, bold=True)
        go_text = font_go.render("ИГРА ОКОНЧЕНА", True, (255, 80, 80))
        go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 90))
        surface.blit(go_text, go_rect)

        # Итоговый счет
        font_sc = pygame.font.SysFont(None, 36)
        sc_text = font_sc.render(f"Ваш счет: {self.score}", True, TEXT_COLOR)
        sc_rect = sc_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 35))
        surface.blit(sc_text, sc_rect)

        mx, my = pygame.mouse.get_pos()

        # Кнопка "Играть еще"
        retry_color = BUTTON_HOVER if self.retry_button_rect.collidepoint(mx, my) else BUTTON_COLOR
        pygame.draw.rect(surface, retry_color, self.retry_button_rect, border_radius=10)
        font_btn = pygame.font.SysFont(None, 30)
        retry_text = font_btn.render("Играть еще", True, TEXT_COLOR)
        retry_rect = retry_text.get_rect(center=self.retry_button_rect.center)
        surface.blit(retry_text, retry_rect)

        # Кнопка "Главное меню"
        menu_color = BUTTON_HOVER if self.menu_button_rect.collidepoint(mx, my) else BUTTON_COLOR
        pygame.draw.rect(surface, menu_color, self.menu_button_rect, border_radius=10)
        menu_text = font_btn.render("Главное меню", True, TEXT_COLOR)
        menu_rect = menu_text.get_rect(center=self.menu_button_rect.center)
        surface.blit(menu_text, menu_rect)

    def draw_shape(self, surface, shape, color, start_x, start_y, scale=1.0):
        block_size = int(CELL_SIZE * scale)
        margin = int(MARGIN * scale)
        for r_idx, row in enumerate(shape):
            for c_idx, val in enumerate(row):
                if val == 1:
                    bx = start_x + c_idx * (block_size + margin)
                    by = start_y + r_idx * (block_size + margin)
                    pygame.draw.rect(surface, color, (bx, by, block_size, block_size), border_radius=4)

    def handle_mouse_down(self, pos):
        if self.state == "MENU":
            if self.play_button_rect.collidepoint(pos):
                self.state = "PLAYING"
                self.reset_game()
        
        elif self.state == "GAMEOVER":
            if self.retry_button_rect.collidepoint(pos):
                self.state = "PLAYING"
                self.reset_game()
            elif self.menu_button_rect.collidepoint(pos):
                self.state = "MENU"
        
        elif self.state == "PLAYING":
            mx, my = pos
            for fig in self.available_figures:
                shape = fig['shape']
                scale = 0.6
                block_size = int(CELL_SIZE * scale)
                margin = int(MARGIN * scale)
                width = len(shape[0]) * (block_size + margin)
                height = len(shape) * (block_size + margin)
                
                if fig['x'] <= mx <= fig['x'] + width and fig['y'] <= my <= fig['y'] + height:
                    self.dragging_figure = fig
                    
                    rel_x = (mx - fig['x']) / width
                    rel_y = (my - fig['y']) / height
                    
                    full_width = len(shape[0]) * (CELL_SIZE + MARGIN)
                    full_height = len(shape) * (CELL_SIZE + MARGIN)
                    
                    self.drag_offset_x = rel_x * full_width
                    self.drag_offset_y = rel_y * full_height
                    break

    def handle_mouse_up(self, pos):
        if self.state == "PLAYING" and self.dragging_figure:
            mx, my = pos
            board_width = GRID_SIZE * (CELL_SIZE + MARGIN)
            board_height = GRID_SIZE * (CELL_SIZE + MARGIN)
            
            shape_top_left_x = mx - self.drag_offset_x
            shape_top_left_y = my - self.drag_offset_y
            
            if (BOARD_OFFSET_X <= shape_top_left_x + CELL_SIZE/2 <= BOARD_OFFSET_X + board_width and 
                BOARD_OFFSET_Y <= shape_top_left_y + CELL_SIZE/2 <= BOARD_OFFSET_Y + board_height):
                
                col = round((shape_top_left_x - BOARD_OFFSET_X) / (CELL_SIZE + MARGIN))
                row = round((shape_top_left_y - BOARD_OFFSET_Y) / (CELL_SIZE + MARGIN))
                
                if self.can_place(self.dragging_figure['shape'], row, col):
                    self.place_figure(self.dragging_figure, row, col)
                    self.available_figures.remove(self.dragging_figure)
                    
                    if len(self.available_figures) == 0:
                        self.spawn_figures()
                    else:
                        # Проверяем, остались ли ходы для оставшихся фигур
                        if not self.check_any_moves_left():
                            self.state = "GAMEOVER"
            
            self.dragging_figure = None

    def place_figure(self, fig, start_row, start_col):
        shape = fig['shape']
        color = fig['color']
        for r_idx, row in enumerate(shape):
            for c_idx, val in enumerate(row):
                if val == 1:
                    self.board[start_row + r_idx][start_col + c_idx] = color
        
        self.score += 10
        self.check_lines()

    def check_lines(self):
        rows_to_clear = []
        cols_to_clear = []

        for r in range(GRID_SIZE):
            if all(self.board[r][c] != 0 for c in range(GRID_SIZE)):
                rows_to_clear.append(r)

        for c in range(GRID_SIZE):
            if all(self.board[r][c] != 0 for r in range(GRID_SIZE)):
                cols_to_clear.append(c)

        cleared_count = len(rows_to_clear) + len(cols_to_clear)
        if cleared_count > 0:
            self.flashing_cells = []
            for r in rows_to_clear:
                for c in range(GRID_SIZE):
                    self.flashing_cells.append((r, c))
            for c in cols_to_clear:
                for r in range(GRID_SIZE):
                    if (r, c) not in self.flashing_cells:
                        self.flashing_cells.append((r, c))
            
            self.flash_timer = 15
            
            # Выбор случайного комплимента из списка для соответствующего уровня линий (1, 2, 3 или 4+)
            level_key = min(cleared_count, 4)
            self.current_message = random.choice(COMPLIMENTS[level_key])
            self.message_timer = 45

            if winsound:
                try:
                    winsound.Beep(500 + cleared_count * 150, 120)
                except:
                    pass

            for r in rows_to_clear:
                for c in range(GRID_SIZE):
                    self.board[r][c] = 0
            for c in cols_to_clear:
                for r in range(GRID_SIZE):
                    self.board[r][c] = 0
            
            self.score += cleared_count * 100

def main():
    print(STARTUP_LOGO)
    
    game = Game()
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    game.handle_mouse_up(event.pos)

        game.draw(SCREEN)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
