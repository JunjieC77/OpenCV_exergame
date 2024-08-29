import pygame
import mediapipe as mp
import cv2
import numpy as np
import random
from profile_manager import ProfileManager
from UI_manager import UIManager
import time

WIDTH, HEIGHT = 1280, 720
class GameLogic:
    def __init__(self):
        # Screen Dimensions
        #WIDTH, HEIGHT = 1280, 720
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))

        # Initialize Pygame
        pygame.init()
        self.profile_manager = ProfileManager()
        self.UI_manager = UIManager(self.window)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.GRAY = (200, 200, 200)
        self.BLUE = (0, 0, 255)

        # Font
        self.FONT = pygame.font.Font("Anton-Regular.ttf", 48)  # Adjusted font size
        self.SMALL_FONT = pygame.font.Font("Anton-Regular.ttf", 32)  # Smaller font size for status

        # Background Music and Sound Effects
        pygame.mixer.music.load("cvgamesound.wav")
        pygame.mixer.music.play(-1, 0.0)
        self.destroying_virus = pygame.mixer.Sound("collect.wav")

        # Game assets
        self.doctor = pygame.image.load("doctor.png")
        self.doctor_coordinate_1 = self.doctor.get_rect()
        self.doctor_coordinate_2 = self.doctor.get_rect()

        self.virus = pygame.image.load("virus.png")
        self.virus_coordinate = self.virus.get_rect()
        self.virus_coordinate.center = (250, 250)

        self.falling_virus = pygame.image.load("falling_virus.png")
        self.falling_virus_coordinates = []
        self.falling_virus_speed = 5  # Falling speed for the new virus

        # Split Virus assets
        self.split_virus = pygame.image.load("split_virus.png")
        self.split_virus = pygame.transform.scale(self.split_virus, (80, 80))
        self.small_split_virus = pygame.transform.scale(self.split_virus, (40, 40))

        self.split_virus_list = []  # List to track split viruses
        self.split_happened_dict = {}  # Dictionary to track if a split has occurred for each virus
        self.small_split_virus_coordinates_dict = {}  # Dictionary to track small viruses for each split virus

        # Initialize x and y to prevent NameError
        self.x, self.y = WIDTH // 2, HEIGHT // 2  # Defaults to center of the screen

        # Game States
        self.state = "menu"  # Possible states: "menu", "game", "pause", "quit", "select", "create", "delete", "rankings"

        # Webcam Setup
        self.webcam = cv2.VideoCapture(0)
        self.webcam.set(3, 1280)
        self.webcam.set(4, 720)

        # Main Game Loop
        self.running = True
        self.hand = None  # Initialize hand to None
        self.SCORE = 0
        self.input_text = ""  # To capture player name input
        self.game_paused = False  # To track if the game is paused
        self.game_start_time = None  # To track when the game starts
        self.pause_resume_time = None  # To track when the game was resumed
        self.selected_profile = None

        # Flag to control refreshing in create state
        self.refresh_create_screen = True

        self.game_duration = 90  # Game duration in seconds (1 minute 30 seconds)
        self.virus_start_time = None

    def reset_game(self):
        #global SCORE, doctor_coordinate_1, doctor_coordinate_2, virus_coordinate, hand, game_paused, game_start_time, pause_resume_time, virus_start_time, falling_virus_coordinates
        self.SCORE = 0
        self.doctor_coordinate_1.center = (WIDTH // 2, HEIGHT // 2)
        self.doctor_coordinate_2.center = (WIDTH // 2, HEIGHT // 2)
        self.virus_coordinate.center = (250, 250)
        self.hand = mp.solutions.hands.Hands(min_tracking_confidence=0.5, min_detection_confidence=0.5)
        self.game_paused = False
        self.game_start_time = time.time()
        self.pause_resume_time = None
        self.virus_start_time = time.time()
        self.falling_virus_coordinates = []

    def handle_score_and_return_to_menu(self):
        #global SCORE, selected_profile, profiles, state
        # Compare current score with high score and update if needed
        if self.selected_profile and self.SCORE > self.selected_profile["high_score"]:
            self.selected_profile["high_score"] = self.SCORE
            self.profile_manager.save_profiles()
        # Return to menu
        self.state = "menu"

    def handle_score_and_return_to_menu(self):
        #global SCORE, selected_profile, profiles, state
        if self.selected_profile and self.SCORE > self.selected_profile["high_score"]:
            self.selected_profile["high_score"] = self.SCORE
            self.profile_manager.save_profiles()
        self.state = "menu"

    def handle_game_end(self):
        self.handle_score_and_return_to_menu()

    def generate_falling_virus(self):
        return pygame.Rect(random.randint(0, WIDTH - 50), 0, 50, 50)

    def generate_split_virus(self):
        rect = self.split_virus.get_rect(center=(random.randint(100, WIDTH - 100), random.randint(130, HEIGHT - 100)))
        self.split_happened_dict[id(rect)] = False  # Initialize split state for this virus using id as the key
        self.small_split_virus_coordinates_dict[id(rect)] = []  # Initialize an empty list for small split viruses
        return rect

    def generate_small_split_viruses(self, center_x, center_y):
        return [
            pygame.Rect(center_x - 40, center_y - 40, 40, 40),
            pygame.Rect(center_x, center_y - 40, 40, 40),
            pygame.Rect(center_x - 20, center_y + 20, 40, 40),
        ]

    def generate_small_split_viruses(self, center_x, center_y):
        return [
            pygame.Rect(center_x - 40, center_y - 40, 40, 40),
            pygame.Rect(center_x, center_y - 40, 40, 40),
            pygame.Rect(center_x - 20, center_y + 20, 40, 40),
        ]

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos
                        if self.UI_manager.start_rect.collidepoint(mouse_x, mouse_y):
                            self.state = "select"
                        elif self.UI_manager.quit_rect.collidepoint(mouse_x, mouse_y):
                            self.running = False
                        elif self.UI_manager.create_profile_button_rect.collidepoint(mouse_x, mouse_y):
                            if len(self.profile_manager.profiles["profiles"]) < 8:
                                self.state = "create"
                                self.refresh_create_screen = True  # Set flag to true to render screen on first entry
                            else:
                                print("Profile limit reached.")
                        elif self.UI_manager.delete_profile_button_rect.collidepoint(mouse_x, mouse_y):
                            self.state = "delete"
                        elif self.UI_manager.rankings_button_rect.collidepoint(mouse_x, mouse_y):
                            self.state = "rankings"

                elif self.state == "create":
                    if self.refresh_create_screen:
                        self.UI_manager.render_create_screen(self.input_text)  # Render screen only once on entry
                        self.refresh_create_screen = False  # Disable further refreshing

                    # Handle text input for creating a profile
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if self.profile_manager.create_profile(self.input_text):
                                self.profile_manager.save_profiles()
                            input_text = ""  # Reset input text
                            self.state = "menu"
                        elif event.key == pygame.K_BACKSPACE:
                            input_text = self.input_text[:-1]
                            self.UI_manager.render_create_screen(input_text)  # Re-render the screen only when text changes
                        else:
                            self.input_text += event.unicode
                            self.UI_manager.render_create_screen(self.input_text)  # Re-render the screen only when text changes

                    # Handle back button in create state
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos
                        if self.UI_manager.back_button_rect.collidepoint(mouse_x, mouse_y):
                            self.state = "menu"

                elif self.state == "delete" or self.state == "select":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos
                        for i, profile_name in enumerate(self.profile_manager.profiles["profiles"].keys()):
                            profile_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50 + i * 60, 300, 50)
                            if profile_button_rect.collidepoint(mouse_x, mouse_y):
                                if self.state == "delete":
                                    self.profile_manager.delete_profile(profile_name)
                                    self.profile_manager.save_profiles()
                                else:
                                    selected_profile_name = profile_name
                                    self.selected_profile = self.profile_manager.select_profile(selected_profile_name)
                                    self.reset_game()  # Reset the game state before starting
                                    self.state = "game"
                                break
                    # Handle back button
                    elif self.UI_manager.back_button_rect.collidepoint(mouse_x, mouse_y):
                        self.state = "menu"

                elif self.state == "rankings":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Handle back button
                        mouse_x, mouse_y = event.pos
                        if self.UI_manager.back_button_rect.collidepoint(mouse_x, mouse_y):
                            self.state = "menu"

                elif self.state == "pause":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos
                        if resume_button_rect.collidepoint(mouse_x, mouse_y):
                            self.state = "game"
                            self.game_paused = False  # Unpause the game
                            self.pause_resume_time = time.time()  # Record the time when the game was resumed
                        elif quit_button_rect.collidepoint(mouse_x, mouse_y):
                            self.handle_score_and_return_to_menu()

            if self.state == "menu":
                # Render Menu
                self.UI_manager.render_menu()

            elif self.state == "delete" or self.state == "select":
                # Render Delete or Select Profile Menu
                self.window.fill(self.WHITE)
                if self.state == "delete":
                    menu_text = self.FONT.render("Delete Profile", True, self.BLACK)
                else:
                    menu_text = self.FONT.render("Select Profile", True, self.BLACK)
                self.window.blit(menu_text, menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

                self.UI_manager.render_select_and_delete_screen(self.profile_manager)


            elif self.state == "rankings":
                # Render Rankings menu
                self.UI_manager.render_ranking_screen(self.profile_manager)
                # pygame.display.update()

            elif self.state == "game":
                if not self.game_paused:
                    control, frame = self.webcam.read()
                    if control:
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        result = self.hand.process(rgb)
                        if result.multi_hand_landmarks:
                            # Process the landmarks for both hands (if present)
                            if len(result.multi_hand_landmarks) >= 1:
                                handLandmark_1 = result.multi_hand_landmarks[0]
                                index_finger_coordinate_1 = handLandmark_1.landmark[8]
                                x1 = int(index_finger_coordinate_1.x * WIDTH)
                                y1 = int(index_finger_coordinate_1.y * HEIGHT)
                                self.doctor_coordinate_1.center = (x1, y1)

                            if len(result.multi_hand_landmarks) >= 2:
                                handLandmark_2 = result.multi_hand_landmarks[1]
                                index_finger_coordinate_2 = handLandmark_2.landmark[8]
                                x2 = int(index_finger_coordinate_2.x * WIDTH)
                                y2 = int(index_finger_coordinate_2.y * HEIGHT)
                                self.doctor_coordinate_2.center = (x2, y2)

                        rgb = np.rot90(rgb)
                        background = pygame.surfarray.make_surface(rgb).convert()
                        background = pygame.transform.flip(background, True, False)
                        self.window.blit(background, (0, 0))
                        self.window.blit(self.doctor, self.doctor_coordinate_1)
                        self.window.blit(self.doctor, self.doctor_coordinate_2)
                        self.window.blit(self.virus, self.virus_coordinate)

                        # Handle virus disappearing after 5 seconds
                        if time.time() - self.virus_start_time > 5:
                            self.virus_coordinate.center = (random.randint(0, 1000), random.randint(130, 500))
                            self.virus_start_time = time.time()

                        # Generate a falling virus occasionally
                        if random.random() < 0.1:
                            self.falling_virus_coordinates.append(self.generate_falling_virus())

                        # Handle falling viruses
                        for falling_virus_rect in self.falling_virus_coordinates[:]:
                            falling_virus_rect.y += self.falling_virus_speed
                            self.window.blit(self.falling_virus, falling_virus_rect)

                            if self.doctor_coordinate_1.colliderect(falling_virus_rect) or self.doctor_coordinate_2.colliderect(
                                    falling_virus_rect):
                                self.destroying_virus.play()
                                self.SCORE += 1
                                self.falling_virus_coordinates.remove(falling_virus_rect)
                            elif falling_virus_rect.y > 500:
                                self.falling_virus_coordinates.remove(falling_virus_rect)

                        # Generate a split virus occasionally
                        if random.random() < 0.01:  # Lower probability for split virus
                            split_virus_rect = self.generate_split_virus()
                            self.split_virus_list.append(split_virus_rect)

                        # Handle split virus logic
                        for split_virus_rect in self.split_virus_list[:]:
                            split_virus_id = id(split_virus_rect)
                            if not self.split_happened_dict[split_virus_id]:
                                self.window.blit(self.split_virus, split_virus_rect)
                                if self.doctor_coordinate_1.colliderect(split_virus_rect) or self.doctor_coordinate_2.colliderect(
                                        split_virus_rect):
                                    small_split_virus_coordinates = self.generate_small_split_viruses(
                                        split_virus_rect.centerx,
                                        split_virus_rect.centery)
                                    self.small_split_virus_coordinates_dict[split_virus_id] = small_split_virus_coordinates
                                    self.split_happened_dict[split_virus_id] = True
                            else:
                                for small_split_virus_rect in self.small_split_virus_coordinates_dict[split_virus_id][:]:
                                    self.window.blit(self.small_split_virus, small_split_virus_rect)
                                    if self.doctor_coordinate_1.colliderect(
                                            small_split_virus_rect) or self.doctor_coordinate_2.colliderect(
                                        small_split_virus_rect):
                                        self.destroying_virus.play()
                                        self.small_split_virus_coordinates_dict[split_virus_id].remove(
                                            small_split_virus_rect)
                                        self.SCORE += 1

                                # Remove split virus when all small viruses are cleared
                                if not self.small_split_virus_coordinates_dict[split_virus_id]:
                                    self.split_virus_list.remove(split_virus_rect)
                                    del self.split_happened_dict[split_virus_id]
                                    del self.small_split_virus_coordinates_dict[split_virus_id]

                        TEXT = self.FONT.render("Score: " + str(self.SCORE), True, (255, 255, 204), (0, 51, 102))
                        TEXT_COORDINATE = TEXT.get_rect(topleft=(20, 20))
                        self.window.blit(TEXT, TEXT_COORDINATE)

                        # Display remaining time
                        remaining_time = int(self.game_duration - (time.time() - self.game_start_time))
                        time_text = self.FONT.render(f"Time: {remaining_time}s", True, (255, 255, 204), (0, 51, 102))
                        time_text_coordinate = time_text.get_rect(center=(WIDTH // 2, 20))
                        self.window.blit(time_text, time_text_coordinate)

                        # Draw the pause button
                        pygame.draw.rect(self.window, self.GRAY, self.UI_manager.pause_button_rect)
                        pause_text = self.FONT.render("||", True, self.BLACK)
                        self.window.blit(pause_text, self.UI_manager.pause_button_rect)

                        # Handle pause
                        current_time = time.time()
                        if current_time - self.game_start_time > 10 and (
                                self.pause_resume_time is None or current_time - self.pause_resume_time > 10):
                            if self.UI_manager.pause_button_rect.collidepoint(x1,
                                                                         y1) or self.UI_manager.pause_button_rect.collidepoint(
                                    x2, y2):
                                self.state = "pause"
                                game_paused = True

                        if self.doctor_coordinate_1.colliderect(self.virus_coordinate) or self.doctor_coordinate_2.colliderect(
                                self.virus_coordinate):
                            self.destroying_virus.play()
                            self.virus_coordinate.center = (random.randint(0, 1000), random.randint(130, 500))
                            self.SCORE += 5

                        # Check if time limit has been reached
                        if remaining_time <= 0:
                            self.handle_game_end()

                        pygame.display.update()


            elif self.state == "pause":
                print(f"Entered pause state: game_paused = {self.game_paused}, state = {self.state}")
                # Pause Menu
                self.window.fill(self.WHITE)
                pause_text = self.FONT.render("Paused", True, self.BLACK)
                resume_button = self.FONT.render("Resume Game", True, self.GREEN)
                quit_button = self.FONT.render("Quit to Menu", True, self.RED)

                pause_text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
                resume_button_rect = resume_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                quit_button_rect = quit_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))

                self.window.blit(pause_text, pause_text_rect)
                self.window.blit(resume_button, resume_button_rect)
                self.window.blit(quit_button, quit_button_rect)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if resume_button_rect.collidepoint(mouse_x, mouse_y):
                        self.state = "game"
                        self.game_paused = False  # Unpause the game
                        self.pause_resume_time = time.time()  # Record the time when the game was resumed
                    elif quit_button_rect.collidepoint(mouse_x, mouse_y):
                        self.handle_score_and_return_to_menu()

                pygame.display.update()

        pygame.quit()
