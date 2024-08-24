import pygame
import mediapipe as mp
import cv2
import numpy as np
import random
from profile_manager import ProfileManager
import time

# Initialize Pygame
pygame.init()
profile_manager =ProfileManager()

# Screen Dimensions
WIDTH, HEIGHT = 1280, 720
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

# Font
FONT = pygame.font.Font("Anton-Regular.ttf", 48)  # Adjusted font size
SMALL_FONT = pygame.font.Font("Anton-Regular.ttf", 32)  # Smaller font size for status

# Background Music and Sound Effects
pygame.mixer.music.load("cvgamesound.wav")
pygame.mixer.music.play(-1, 0.0)
destroying_virus = pygame.mixer.Sound("collect.wav")

# Game assets
doctor = pygame.image.load("doctor.png")
doctor_coordinate_1 = doctor.get_rect()
doctor_coordinate_2 = doctor.get_rect()

virus = pygame.image.load("virus.png")
virus_coordinate = virus.get_rect()
virus_coordinate.center = (250, 250)

falling_virus = pygame.image.load("falling_virus.png")
falling_virus_coordinates = []
falling_virus_speed = 5  # Falling speed for the new virus

# Split Virus assets
split_virus = pygame.image.load("split_virus.png")
split_virus = pygame.transform.scale(split_virus, (80, 80))
small_split_virus = pygame.transform.scale(split_virus, (40, 40))

split_virus_list = []  # List to track split viruses
split_happened_dict = {}  # Dictionary to track if a split has occurred for each virus
small_split_virus_coordinates_dict = {}  # Dictionary to track small viruses for each split virus


# Initialize x and y to prevent NameError
x, y = WIDTH // 2, HEIGHT // 2  # Defaults to center of the screen

# Game States
state = "menu"  # Possible states: "menu", "game", "pause", "quit", "select", "create", "delete", "rankings"

# Webcam Setup
webcam = cv2.VideoCapture(0)
webcam.set(3, 1280)
webcam.set(4, 720)

# Button Rects
pause_button_rect = pygame.Rect(WIDTH - 100, 20, 80, 80)
resume_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 100)
quit_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 60, 300, 100)
back_button_rect = pygame.Rect(WIDTH - 180, 20, 160, 50)  # Back button


# Main Game Loop
running = True
hand = None  # Initialize hand to None
SCORE = 0
input_text = ""  # To capture player name input
game_paused = False  # To track if the game is paused
game_start_time = None  # To track when the game starts
pause_resume_time = None  # To track when the game was resumed

# Flag to control refreshing in create state
refresh_create_screen = True

game_duration = 90  # Game duration in seconds (1 minute 30 seconds)
virus_start_time = None

def draw_text_input_box(surface, text, rect):
    pygame.draw.rect(surface, BLACK, rect, 2)
    font = pygame.font.Font(None, 48)
    txt_surface = font.render(text, True, BLACK)
    surface.blit(txt_surface, (rect.x+5, rect.y+5))
    pygame.display.flip()

def display_back_button():
    back_text = FONT.render("Back", True, WHITE)
    pygame.draw.rect(window, BLUE, back_button_rect)
    window.blit(back_text, back_button_rect)

def reset_game():
    global SCORE, doctor_coordinate_1,doctor_coordinate_2, virus_coordinate, hand, game_paused, game_start_time, pause_resume_time, virus_start_time, falling_virus_coordinates
    SCORE = 0
    doctor_coordinate_1.center = (WIDTH // 2, HEIGHT // 2)
    doctor_coordinate_2.center = (WIDTH // 2, HEIGHT // 2)
    virus_coordinate.center = (250, 250)
    hand = mp.solutions.hands.Hands(min_tracking_confidence=0.5, min_detection_confidence=0.5)
    game_paused = False
    game_start_time = time.time()
    pause_resume_time = None
    virus_start_time = time.time()
    falling_virus_coordinates = []

def handle_score_and_return_to_menu():
    global SCORE, selected_profile, profiles, state
    # Compare current score with high score and update if needed
    if selected_profile and SCORE > selected_profile["high_score"]:
        selected_profile["high_score"] = SCORE
        profile_manager.save_profiles()
    # Return to menu
    state = "menu"

def render_create_screen():
    window.fill(WHITE)
    create_text = FONT.render("Enter Profile Name:", True, BLACK)
    create_text_rect = create_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 50)
    window.blit(create_text, create_text_rect)
    draw_text_input_box(window, input_text, input_box)
    display_back_button()
    pygame.display.update()

def handle_score_and_return_to_menu():
    global SCORE, selected_profile, profiles, state
    if selected_profile and SCORE > selected_profile["high_score"]:
        selected_profile["high_score"] = SCORE
        profile_manager.save_profiles()
    state = "menu"

def handle_game_end():
    handle_score_and_return_to_menu()

def generate_falling_virus():
    return pygame.Rect(random.randint(0, WIDTH-50), 0, 50, 50)

def generate_split_virus():
    rect = split_virus.get_rect(center=(random.randint(100, WIDTH-100), random.randint(130, HEIGHT-100)))
    split_happened_dict[id(rect)] = False  # Initialize split state for this virus using id as the key
    small_split_virus_coordinates_dict[id(rect)] = []  # Initialize an empty list for small split viruses
    return rect

def generate_small_split_viruses(center_x, center_y):
    return [
        pygame.Rect(center_x - 40, center_y - 40, 40, 40),
        pygame.Rect(center_x, center_y - 40, 40, 40),
        pygame.Rect(center_x - 20, center_y + 20, 40, 40),
    ]

def generate_small_split_viruses(center_x, center_y):
    return [
        pygame.Rect(center_x - 40, center_y - 40, 40, 40),
        pygame.Rect(center_x, center_y - 40, 40, 40),
        pygame.Rect(center_x - 20, center_y + 20, 40, 40),
    ]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if start_rect.collidepoint(mouse_x, mouse_y):
                    state = "select"
                elif quit_rect.collidepoint(mouse_x, mouse_y):
                    running = False
                elif create_profile_button_rect.collidepoint(mouse_x, mouse_y):
                    if len(profile_manager.profiles["profiles"]) < 8:
                        state = "create"
                        refresh_create_screen = True  # Set flag to true to render screen on first entry
                    else:
                        print("Profile limit reached.")
                elif delete_profile_button_rect.collidepoint(mouse_x, mouse_y):
                    state = "delete"
                elif rankings_button_rect.collidepoint(mouse_x, mouse_y):
                    state = "rankings"

        elif state == "create":
            if refresh_create_screen:
                render_create_screen()  # Render screen only once on entry
                refresh_create_screen = False  # Disable further refreshing

            # Handle text input for creating a profile
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if profile_manager.create_profile(input_text):
                        profile_manager.save_profiles()
                    input_text = ""  # Reset input text
                    state = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                    render_create_screen()  # Re-render the screen only when text changes
                else:
                    input_text += event.unicode
                    render_create_screen()  # Re-render the screen only when text changes

            # Handle back button in create state
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if back_button_rect.collidepoint(mouse_x, mouse_y):
                    state = "menu"

        elif state == "delete" or state == "select":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                for i, profile_name in enumerate(profile_manager.profiles["profiles"].keys()):
                    profile_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50 + i * 60, 300, 50)
                    if profile_button_rect.collidepoint(mouse_x, mouse_y):
                        if state == "delete":
                            profile_manager.delete_profile(profile_name)
                            profile_manager.save_profiles()
                        else:
                            selected_profile_name = profile_name
                            selected_profile = profile_manager.select_profile(selected_profile_name)
                            reset_game()  # Reset the game state before starting
                            state = "game"
                        break
            # Handle back button
            elif back_button_rect.collidepoint(mouse_x, mouse_y):
                state = "menu"

        elif state == "rankings":
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle back button
                mouse_x, mouse_y = event.pos
                if back_button_rect.collidepoint(mouse_x, mouse_y):
                    state = "menu"

        elif state == "pause":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if resume_button_rect.collidepoint(mouse_x, mouse_y):
                    state = "game"
                    game_paused = False  # Unpause the game
                    pause_resume_time = time.time()  # Record the time when the game was resumed
                elif quit_button_rect.collidepoint(mouse_x, mouse_y):
                    handle_score_and_return_to_menu()

    if state == "menu":
        # Render Menu
        window.fill(WHITE)
        title_text = FONT.render("Welcome to the Game", True, BLACK)
        start_button = FONT.render("Start Game", True, RED)
        quit_button = FONT.render("Quit", True, RED)
        create_profile_button = FONT.render("Create Profile", True, GREEN)
        delete_profile_button = FONT.render("Delete Profile", True, RED)
        rankings_button = FONT.render("Score Rankings", True, GRAY)

        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        start_rect = start_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        quit_rect = quit_button.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        create_profile_button_rect = create_profile_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        delete_profile_button_rect = delete_profile_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 200))
        rankings_button_rect = rankings_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 300))

        window.blit(title_text, title_rect)
        window.blit(start_button, start_rect)
        window.blit(quit_button, quit_rect)
        window.blit(create_profile_button, create_profile_button_rect)
        window.blit(delete_profile_button, delete_profile_button_rect)
        window.blit(rankings_button, rankings_button_rect)

        pygame.display.update()

    elif state == "delete" or state == "select":
        # Render Delete or Select Profile Menu
        window.fill(WHITE)
        if state == "delete":
            menu_text = FONT.render("Delete Profile", True, BLACK)
        else:
            menu_text = FONT.render("Select Profile", True, BLACK)
        window.blit(menu_text, menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

        for i, profile_name in enumerate(profile_manager.profiles["profiles"].keys()):
            profile_button = FONT.render(profile_name, True, BLACK)
            profile_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50 + i * 60, 300, 50)
            window.blit(profile_button, profile_button_rect)

        display_back_button()
        pygame.display.update()

    elif state == "rankings":
        # Render Rankings
        window.fill(WHITE)
        rankings_text = FONT.render("Score Rankings", True, BLACK)
        window.blit(rankings_text, rankings_text.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

        sorted_profiles = sorted(profile_manager.profiles["profiles"].items(), key=lambda item: item[1]["high_score"], reverse=True)
        for i, (profile_name, data) in enumerate(sorted_profiles):
            profile_rank_text = FONT.render(f"{profile_name}: {data['high_score']}", True, BLACK)
            window.blit(profile_rank_text, (WIDTH // 2 - 150, HEIGHT // 2 - 50 + i * 60))

        display_back_button()
        pygame.display.update()

    elif state == "game":
        if not game_paused:
            control, frame = webcam.read()
            if control:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = hand.process(rgb)
                if result.multi_hand_landmarks:
                    # Process the landmarks for both hands (if present)
                    if len(result.multi_hand_landmarks) >= 1:
                        handLandmark_1 = result.multi_hand_landmarks[0]
                        index_finger_coordinate_1 = handLandmark_1.landmark[8]
                        x1 = int(index_finger_coordinate_1.x * WIDTH)
                        y1 = int(index_finger_coordinate_1.y * HEIGHT)
                        doctor_coordinate_1.center = (x1, y1)

                    if len(result.multi_hand_landmarks) >= 2:
                        handLandmark_2 = result.multi_hand_landmarks[1]
                        index_finger_coordinate_2 = handLandmark_2.landmark[8]
                        x2 = int(index_finger_coordinate_2.x * WIDTH)
                        y2 = int(index_finger_coordinate_2.y * HEIGHT)
                        doctor_coordinate_2.center = (x2, y2)

                rgb = np.rot90(rgb)
                background = pygame.surfarray.make_surface(rgb).convert()
                background = pygame.transform.flip(background, True, False)
                window.blit(background, (0, 0))
                window.blit(doctor, doctor_coordinate_1)
                window.blit(doctor, doctor_coordinate_2)
                window.blit(virus, virus_coordinate)

                # Handle virus disappearing after 5 seconds
                if time.time() - virus_start_time > 5:
                    virus_coordinate.center = (random.randint(0, 1000), random.randint(130, 500))
                    virus_start_time = time.time()

                # Generate a falling virus occasionally
                if random.random() < 0.1:
                    falling_virus_coordinates.append(generate_falling_virus())


                # Handle falling viruses
                for falling_virus_rect in falling_virus_coordinates[:]:
                    falling_virus_rect.y += falling_virus_speed
                    window.blit(falling_virus, falling_virus_rect)

                    if doctor_coordinate_1.colliderect(falling_virus_rect) or doctor_coordinate_2.colliderect(falling_virus_rect):
                        destroying_virus.play()
                        SCORE += 1
                        falling_virus_coordinates.remove(falling_virus_rect)
                    elif falling_virus_rect.y > 500:
                        falling_virus_coordinates.remove(falling_virus_rect)

                # Generate a split virus occasionally
                if random.random() < 0.01:  # Lower probability for split virus
                    split_virus_rect = generate_split_virus()
                    split_virus_list.append(split_virus_rect)

                # Handle split virus logic
                for split_virus_rect in split_virus_list[:]:
                    split_virus_id = id(split_virus_rect)
                    if not split_happened_dict[split_virus_id]:
                        window.blit(split_virus, split_virus_rect)
                        if doctor_coordinate_1.colliderect(split_virus_rect) or doctor_coordinate_2.colliderect(
                                split_virus_rect):
                            small_split_virus_coordinates = generate_small_split_viruses(split_virus_rect.centerx,
                                                                                         split_virus_rect.centery)
                            small_split_virus_coordinates_dict[split_virus_id] = small_split_virus_coordinates
                            split_happened_dict[split_virus_id] = True
                    else:
                        for small_split_virus_rect in small_split_virus_coordinates_dict[split_virus_id][:]:
                            window.blit(small_split_virus, small_split_virus_rect)
                            if doctor_coordinate_1.colliderect(
                                    small_split_virus_rect) or doctor_coordinate_2.colliderect(small_split_virus_rect):
                                destroying_virus.play()
                                small_split_virus_coordinates_dict[split_virus_id].remove(small_split_virus_rect)
                                SCORE += 1

                        # Remove split virus when all small viruses are cleared
                        if not small_split_virus_coordinates_dict[split_virus_id]:
                            split_virus_list.remove(split_virus_rect)
                            del split_happened_dict[split_virus_id]
                            del small_split_virus_coordinates_dict[split_virus_id]

                TEXT = FONT.render("Score: " + str(SCORE), True, (255, 255, 204), (0, 51, 102))
                TEXT_COORDINATE = TEXT.get_rect(topleft=(20, 20))
                window.blit(TEXT, TEXT_COORDINATE)

                # Display remaining time
                remaining_time = int(game_duration - (time.time() - game_start_time))
                time_text = FONT.render(f"Time: {remaining_time}s", True, (255, 255, 204), (0, 51, 102))
                time_text_coordinate = time_text.get_rect(center=(WIDTH // 2, 20))
                window.blit(time_text, time_text_coordinate)

                # Draw the pause button
                pygame.draw.rect(window, GRAY, pause_button_rect)
                pause_text = FONT.render("||", True, BLACK)
                window.blit(pause_text, pause_button_rect)

                # Handle pause
                current_time = time.time()
                if current_time - game_start_time > 10 and (pause_resume_time is None or current_time - pause_resume_time > 10):
                    if pause_button_rect.collidepoint(x1, y1) or pause_button_rect.collidepoint(x2, y2):
                        state = "pause"
                        game_paused = True

                if doctor_coordinate_1.colliderect(virus_coordinate) or doctor_coordinate_2.colliderect(
                        virus_coordinate):
                    destroying_virus.play()
                    virus_coordinate.center = (random.randint(0, 1000), random.randint(130, 500))
                    SCORE += 5

                # Check if time limit has been reached
                if remaining_time <= 0:
                    handle_game_end()

                pygame.display.update()


    elif state == "pause":
        print(f"Entered pause state: game_paused = {game_paused}, state = {state}")
        # Pause Menu
        window.fill(WHITE)
        pause_text = FONT.render("Paused", True, BLACK)
        resume_button = FONT.render("Resume Game", True, GREEN)
        quit_button = FONT.render("Quit to Menu", True, RED)

        pause_text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        resume_button_rect = resume_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        quit_button_rect = quit_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))

        window.blit(pause_text, pause_text_rect)
        window.blit(resume_button, resume_button_rect)
        window.blit(quit_button, quit_button_rect)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if resume_button_rect.collidepoint(mouse_x, mouse_y):
                state = "game"
                game_paused = False  # Unpause the game
                pause_resume_time = time.time()  # Record the time when the game was resumed
            elif quit_button_rect.collidepoint(mouse_x, mouse_y):
                handle_score_and_return_to_menu()

        pygame.display.update()

pygame.quit()