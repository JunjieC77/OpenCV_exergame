import pygame
WIDTH, HEIGHT = 1280, 720

class UIManager:
    def __init__(self, window):
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.GRAY = (200, 200, 200)
        self.BLUE = (0, 0, 255)
        self.window = window
        self.FONT = pygame.font.Font("Anton-Regular.ttf", 48)  # Adjusted font size
        self.SMALL_FONT = pygame.font.Font("Anton-Regular.ttf", 32)  # Smaller font size for status
        self.pause_button_rect = pygame.Rect(WIDTH - 100, 20, 80, 80)
        self.resume_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 100)
        self.quit_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 60, 300, 100)
        self.back_button_rect = pygame.Rect(WIDTH - 180, 20, 160, 50)  # Back button
        self.title_rect = None
        self.start_rect = None
        self.quit_rect = None
        self.create_profile_button_rect = None
        self.delete_profile_button_rect = None
        self.rankings_button_rect = None


    def draw_text_input_box(self, surface, text, rect):
        pygame.draw.rect(surface, self.BLACK, rect, 2)
        font = pygame.font.Font(None, 48)
        txt_surface = font.render(text, True, self.BLACK)
        surface.blit(txt_surface, (rect.x + 5, rect.y + 5))
        pygame.display.flip()

    def display_back_button(self):
        back_text = self.FONT.render("Back", True, self.WHITE)
        pygame.draw.rect(self.window, self.BLUE, self.back_button_rect)
        self.window.blit(back_text, self.back_button_rect)

    def render_create_screen(self,input_text):
        self.window.fill(self.WHITE)
        create_text = self.FONT.render("Enter Profile Name:", True, self.BLACK)
        create_text_rect = create_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 50)
        self.window.blit(create_text, create_text_rect)
        self.draw_text_input_box(self.window, input_text, input_box)
        self.display_back_button()
        pygame.display.update()

    def render_menu(self):
        self.window.fill(self.WHITE)
        title_text = self.FONT.render("Welcome to the Game", True, self.BLACK)
        start_button = self.FONT.render("Start Game", True, self.RED)
        quit_button = self.FONT.render("Quit", True, self.RED)
        create_profile_button = self.FONT.render("Create Profile", True, self.GREEN)
        delete_profile_button = self.FONT.render("Delete Profile", True, self.RED)
        rankings_button = self.FONT.render("Score Rankings", True, self.GRAY)

        self.title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        self.start_rect = start_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        self.quit_rect = quit_button.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.create_profile_button_rect = create_profile_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        self.delete_profile_button_rect = delete_profile_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 200))
        self.rankings_button_rect = rankings_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 300))

        self.window.blit(title_text, self.title_rect)
        self.window.blit(start_button, self.start_rect)
        self.window.blit(quit_button, self.quit_rect)
        self.window.blit(create_profile_button, self.create_profile_button_rect)
        self.window.blit(delete_profile_button, self.delete_profile_button_rect)
        self.window.blit(rankings_button, self.rankings_button_rect)

        pygame.display.update()