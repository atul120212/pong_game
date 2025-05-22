import pygame
import sys
import random
import time
import math
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NEON_GREEN = (57, 255, 20)
NEON_BLUE = (30, 144, 255)
NEON_PINK = (255, 20, 147)
NEON_PURPLE = (138, 43, 226)
NEON_RED = (255, 0, 60)
NEON_YELLOW = (255, 255, 0)
PADDLE_SPEED = 7

# Ball speed settings for different difficulty levels
DIFFICULTY_SETTINGS = {
    'Easy': {
        'INITIAL_BALL_SPEED': 4,
        'MAX_BALL_SPEED': 8,
        'BALL_ACCELERATION': 0.00002,
        'AI_SPEED': 5
    },
    'Medium': {
        'INITIAL_BALL_SPEED': 5,
        'MAX_BALL_SPEED': 10,
        'BALL_ACCELERATION': 0.00002,
        'AI_SPEED': 6
    },
    'Hard': {
        'INITIAL_BALL_SPEED': 6,
        'MAX_BALL_SPEED': 12,
        'BALL_ACCELERATION': 0.00002,
        'AI_SPEED': 7
    }
}

# Create sounds directory if it doesn't exist
sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
os.makedirs(sounds_dir, exist_ok=True)

# Sound effects
try:
    # Load sound effects if they exist, otherwise create placeholder sounds
    bounce_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "bounce.wav"))
    hit_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "hit.wav"))
    score_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "score.wav"))
    win_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "win.wav"))
    powerup_sound = pygame.mixer.Sound(os.path.join(sounds_dir, "powerup.wav"))
except:
    # Create silent sounds as placeholders
    bounce_sound = pygame.mixer.Sound(pygame.sndarray.array([0] * 44100))
    hit_sound = pygame.mixer.Sound(pygame.sndarray.array([0] * 44100))
    score_sound = pygame.mixer.Sound(pygame.sndarray.array([0] * 44100))
    win_sound = pygame.mixer.Sound(pygame.sndarray.array([0] * 44100))
    powerup_sound = pygame.mixer.Sound(pygame.sndarray.array([0] * 44100))
    print("Sound files not found. Using silent placeholders.")

# Default to Medium difficulty
current_difficulty = 'Medium'
INITIAL_BALL_SPEED = DIFFICULTY_SETTINGS[current_difficulty]['INITIAL_BALL_SPEED']
MAX_BALL_SPEED = DIFFICULTY_SETTINGS[current_difficulty]['MAX_BALL_SPEED']
BALL_ACCELERATION = DIFFICULTY_SETTINGS[current_difficulty]['BALL_ACCELERATION']
AI_SPEED = DIFFICULTY_SETTINGS[current_difficulty]['AI_SPEED']
FPS = 60
WINNING_SCORE = 10
TRAIL_LENGTH = 10  # Number of positions to remember for the trail

# Power-up settings
POWERUP_TYPES = ['speed_boost', 'paddle_grow', 'paddle_shrink', 'ball_size']
POWERUP_DURATION = 5  # seconds
POWERUP_SPAWN_CHANCE = 0.002  # Chance per frame to spawn a powerup
MAX_POWERUPS = 1  # Maximum number of powerups on screen at once

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Retro Pong")
clock = pygame.time.Clock()

# Create game objects
player1_paddle = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
player2_paddle = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Game variables
ball_speed_x = INITIAL_BALL_SPEED * random.choice((1, -1))
ball_speed_y = INITIAL_BALL_SPEED * random.choice((1, -1))
current_ball_speed = INITIAL_BALL_SPEED
player1_score = 0
player2_score = 0
last_score_time = time.time()
two_player_mode = False  # Default to AI opponent
game_over = False
winner = 0
control_type = "keyboard"  # Default control type: keyboard or mouse
game_paused = False
show_fps = False  # FPS counter toggle
last_frame_time = time.time()
delta_time = 0

# Power-up variables
active_powerups = []  # List to store active powerups
powerup_effects = {
    'player1': {'paddle_grow': 0, 'paddle_shrink': 0, 'speed_boost': 0},
    'player2': {'paddle_grow': 0, 'paddle_shrink': 0, 'speed_boost': 0},
    'ball': {'size': 0, 'speed': 0}
}
powerup_timers = []  # List to track active powerup timers

# Animation variables
ball_trail = []  # Store previous ball positions for trail effect
hit_animations = []  # Store hit animation data
stars = []  # Background stars

# Create stars for background
for _ in range(100):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.randint(1, 3)
    brightness = random.randint(100, 255)
    pulse_speed = random.uniform(0.02, 0.05)
    stars.append([x, y, size, brightness, pulse_speed, 0])

# Font for text display
try:
    # Try to use a retro-style font if available
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    tiny_font = pygame.font.Font(None, 24)
except:
    # Fall back to default font
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    tiny_font = pygame.font.Font(None, 24)

def reset_ball():
    """Reset the ball to the center of the screen with random direction."""
    global ball_speed_x, ball_speed_y, current_ball_speed, last_score_time, ball_trail
    ball.center = (WIDTH // 2, HEIGHT // 2)
    
    # Reset ball speed to initial value after scoring
    current_ball_speed = DIFFICULTY_SETTINGS[current_difficulty]['INITIAL_BALL_SPEED']
    
    # Randomize direction but ensure it's not too vertical
    angle = random.uniform(-0.5, 0.5)  # Limit the angle
    ball_speed_x = current_ball_speed * random.choice((1, -1))
    ball_speed_y = current_ball_speed * random.choice((0.7, -0.7))
    
    # Update the last score time
    last_score_time = time.time()
    
    # Clear the ball trail
    ball_trail = []

def reset_game():
    """Reset the entire game state."""
    global player1_score, player2_score, game_over, winner, hit_animations, active_powerups, powerup_timers
    global powerup_effects
    
    player1_score = 0
    player2_score = 0
    game_over = False
    winner = 0
    hit_animations = []
    active_powerups = []
    powerup_timers = []
    
    # Reset powerup effects
    powerup_effects = {
        'player1': {'paddle_grow': 0, 'paddle_shrink': 0, 'speed_boost': 0},
        'player2': {'paddle_grow': 0, 'paddle_shrink': 0, 'speed_boost': 0},
        'ball': {'size': 0, 'speed': 0}
    }
    
    # Reset paddle sizes
    player1_paddle.height = PADDLE_HEIGHT
    player2_paddle.height = PADDLE_HEIGHT
    
    reset_ball()
    player1_paddle.centery = HEIGHT // 2
    player2_paddle.centery = HEIGHT // 2

def move_paddle(paddle, up=True, player='player1'):
    """Move the paddle up or down within screen boundaries."""
    # Apply speed boost if active
    speed_boost = 1
    if player == 'player1' and powerup_effects['player1']['speed_boost'] > 0:
        speed_boost = 1.5
    elif player == 'player2' and powerup_effects['player2']['speed_boost'] > 0:
        speed_boost = 1.5
        
    speed = PADDLE_SPEED * speed_boost * (delta_time * 60)  # Scale by delta time for consistent speed
    
    if up and paddle.top > 0:
        paddle.y -= speed
    if not up and paddle.bottom < HEIGHT:
        paddle.y += speed

def move_paddle_mouse(paddle, mouse_y):
    """Move the paddle to follow mouse position."""
    # Ensure paddle stays within screen boundaries
    if mouse_y - paddle.height // 2 > 0 and mouse_y + paddle.height // 2 < HEIGHT:
        paddle.centery = mouse_y

def move_ai_opponent():
    """AI to move the opponent paddle towards the ball with some imperfection."""
    # Add some "thinking" delay and imperfection to make the AI beatable
    if ball_speed_x > 0:  # Only move if ball is coming towards the AI
        # Predict where the ball will be
        target_y = ball.centery
        
        # Add some randomness to make the AI imperfect
        # More randomness on Easy, less on Hard
        if current_difficulty == 'Easy':
            mistake_chance = 0.2
            mistake_amount = random.randint(-70, 70)
        elif current_difficulty == 'Medium':
            mistake_chance = 0.1
            mistake_amount = random.randint(-50, 50)
        else:  # Hard
            mistake_chance = 0.05
            mistake_amount = random.randint(-30, 30)
            
        if random.random() < mistake_chance:
            target_y += mistake_amount
        
        # Apply speed boost if active
        speed = AI_SPEED
        if powerup_effects['player2']['speed_boost'] > 0:
            speed *= 1.5
            
        speed *= (delta_time * 60)  # Scale by delta time
        
        # Move towards the predicted position
        if player2_paddle.centery < target_y and player2_paddle.bottom < HEIGHT:
            player2_paddle.y += min(speed, target_y - player2_paddle.centery)
        elif player2_paddle.centery > target_y and player2_paddle.top > 0:
            player2_paddle.y -= min(speed, player2_paddle.centery - target_y)
    else:
        # When ball is moving away, return slowly to center
        if abs(player2_paddle.centery - HEIGHT // 2) > 10:
            speed = 2 * (delta_time * 60)
            if player2_paddle.centery > HEIGHT // 2:
                player2_paddle.y -= speed
            else:
                player2_paddle.y += speed

def create_hit_animation(x, y):
    """Create a new hit animation at the specified position."""
    hit_animations.append({
        'x': x,
        'y': y,
        'radius': 5,
        'max_radius': 30,
        'alpha': 255,
        'color': NEON_PINK
    })

def update_hit_animations():
    """Update all active hit animations."""
    global hit_animations
    new_animations = []
    
    for anim in hit_animations:
        anim['radius'] += 2 * (delta_time * 60)
        anim['alpha'] -= 10 * (delta_time * 60)
        
        if anim['alpha'] > 0:
            new_animations.append(anim)
    
    hit_animations = new_animations

def update_stars():
    """Update the twinkling stars in the background."""
    for star in stars:
        # Update the pulse phase
        star[5] += star[4] * (delta_time * 60)
        # Calculate brightness using sine wave for pulsing effect
        pulse_factor = (math.sin(star[5]) + 1) / 2  # Range 0 to 1
        star[3] = int(100 + 155 * pulse_factor)  # Range 100-255

def spawn_powerup():
    """Randomly spawn a powerup on the screen."""
    if len(active_powerups) < MAX_POWERUPS and random.random() < POWERUP_SPAWN_CHANCE:
        powerup_type = random.choice(POWERUP_TYPES)
        x = random.randint(WIDTH // 4, 3 * WIDTH // 4)
        y = random.randint(HEIGHT // 4, 3 * HEIGHT // 4)
        size = 20
        active_powerups.append({
            'rect': pygame.Rect(x - size // 2, y - size // 2, size, size),
            'type': powerup_type,
            'color': NEON_YELLOW,
            'pulse': 0
        })

def check_powerup_collision():
    """Check if the ball collides with any powerups."""
    global active_powerups, powerup_timers
    
    for powerup in active_powerups[:]:
        if ball.colliderect(powerup['rect']):
            # Determine which player gets the powerup based on ball direction
            player = 'player1' if ball_speed_x < 0 else 'player2'
            
            # Apply powerup effect
            apply_powerup(powerup['type'], player)
            
            # Remove the powerup
            active_powerups.remove(powerup)
            
            # Play powerup sound
            play_sound("powerup")

def apply_powerup(powerup_type, player):
    """Apply the effect of a powerup to the specified player."""
    global powerup_effects, powerup_timers, player1_paddle, player2_paddle
    
    # Add timer for the powerup
    powerup_timers.append({
        'type': powerup_type,
        'player': player,
        'time': time.time() + POWERUP_DURATION
    })
    
    # Apply immediate effects
    if powerup_type == 'paddle_grow':
        if player == 'player1':
            player1_paddle.height = int(PADDLE_HEIGHT * 1.5)
            powerup_effects['player1']['paddle_grow'] = POWERUP_DURATION
        else:
            player2_paddle.height = int(PADDLE_HEIGHT * 1.5)
            powerup_effects['player2']['paddle_grow'] = POWERUP_DURATION
    
    elif powerup_type == 'paddle_shrink':
        # Apply to opponent
        opponent = 'player2' if player == 'player1' else 'player1'
        if opponent == 'player1':
            player1_paddle.height = int(PADDLE_HEIGHT * 0.7)
            powerup_effects['player1']['paddle_shrink'] = POWERUP_DURATION
        else:
            player2_paddle.height = int(PADDLE_HEIGHT * 0.7)
            powerup_effects['player2']['paddle_shrink'] = POWERUP_DURATION
    
    elif powerup_type == 'speed_boost':
        powerup_effects[player]['speed_boost'] = POWERUP_DURATION
    
    elif powerup_type == 'ball_size':
        global ball, BALL_SIZE
        ball.width = ball.height = int(BALL_SIZE * 1.5)
        powerup_effects['ball']['size'] = POWERUP_DURATION

def update_powerups():
    """Update powerup timers and effects."""
    global powerup_timers, powerup_effects, player1_paddle, player2_paddle, ball
    
    current_time = time.time()
    
    # Update powerup timers
    for timer in powerup_timers[:]:
        if current_time >= timer['time']:
            # Remove expired powerup effect
            powerup_type = timer['type']
            player = timer['player']
            
            if powerup_type == 'paddle_grow':
                if player == 'player1':
                    player1_paddle.height = PADDLE_HEIGHT
                    powerup_effects['player1']['paddle_grow'] = 0
                else:
                    player2_paddle.height = PADDLE_HEIGHT
                    powerup_effects['player2']['paddle_grow'] = 0
            
            elif powerup_type == 'paddle_shrink':
                opponent = 'player2' if player == 'player1' else 'player1'
                if opponent == 'player1':
                    player1_paddle.height = PADDLE_HEIGHT
                    powerup_effects['player1']['paddle_shrink'] = 0
                else:
                    player2_paddle.height = PADDLE_HEIGHT
                    powerup_effects['player2']['paddle_shrink'] = 0
            
            elif powerup_type == 'speed_boost':
                powerup_effects[player]['speed_boost'] = 0
            
            elif powerup_type == 'ball_size':
                ball.width = ball.height = BALL_SIZE
                powerup_effects['ball']['size'] = 0
            
            # Remove the timer
            powerup_timers.remove(timer)
    
    # Update active powerups animation
    for powerup in active_powerups:
        powerup['pulse'] += 0.1 * (delta_time * 60)

def update_ball():
    """Update ball position, handle collisions, and increase speed over time."""
    global ball_speed_x, ball_speed_y, player1_score, player2_score, current_ball_speed, game_over, winner, ball_trail
    
    # Add current position to trail
    ball_trail.append((ball.centerx, ball.centery))
    
    # Keep trail at fixed length
    if len(ball_trail) > TRAIL_LENGTH:
        ball_trail.pop(0)
    
    # Move the ball with delta time for consistent speed
    ball.x += ball_speed_x * (delta_time * 60)
    ball.y += ball_speed_y * (delta_time * 60)
    
    # Gradually increase ball speed over time (capped at maximum)
    time_since_last_score = time.time() - last_score_time
    if time_since_last_score > 3 and current_ball_speed < DIFFICULTY_SETTINGS[current_difficulty]['MAX_BALL_SPEED']:
        speed_factor = abs(ball_speed_x) / current_ball_speed  # Preserve direction
        current_ball_speed = min(DIFFICULTY_SETTINGS[current_difficulty]['MAX_BALL_SPEED'], 
                                current_ball_speed + DIFFICULTY_SETTINGS[current_difficulty]['BALL_ACCELERATION'] * delta_time * 60)
        ball_speed_x = current_ball_speed * speed_factor * (1 if ball_speed_x > 0 else -1)
    
    # Ball collision with top and bottom walls
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1
        create_hit_animation(ball.centerx, ball.top if ball.top <= 0 else ball.bottom)
        play_sound("bounce")
    
    # Ball collision with paddles
    if ball.colliderect(player1_paddle):
        # Prevent ball from getting stuck inside paddle
        if ball.left < player1_paddle.right:
            ball.left = player1_paddle.right
            
        ball_speed_x *= -1
        create_hit_animation(player1_paddle.right, ball.centery)
        
        # Add a slight y-speed change based on where the ball hit the paddle
        relative_intersect_y = (player1_paddle.centery - ball.centery) / (player1_paddle.height / 2)
        ball_speed_y = -relative_intersect_y * (current_ball_speed * 0.75)
        
        play_sound("hit")
    
    elif ball.colliderect(player2_paddle):
        # Prevent ball from getting stuck inside paddle
        if ball.right > player2_paddle.left:
            ball.right = player2_paddle.left
            
        ball_speed_x *= -1
        create_hit_animation(player2_paddle.left, ball.centery)
        
        # Add a slight y-speed change based on where the ball hit the paddle
        relative_intersect_y = (player2_paddle.centery - ball.centery) / (player2_paddle.height / 2)
        ball_speed_y = -relative_intersect_y * (current_ball_speed * 0.75)
        
        play_sound("hit")
    
    # Ball out of bounds - scoring
    if ball.left <= 0:
        player2_score += 1
        create_hit_animation(0, ball.centery)
        play_sound("score")
        
        # Check for win condition
        if player2_score >= WINNING_SCORE:
            game_over = True
            winner = 2
            play_sound("win")
        else:
            reset_ball()
    
    if ball.right >= WIDTH:
        player1_score += 1
        create_hit_animation(WIDTH, ball.centery)
        play_sound("score")
        
        # Check for win condition
        if player1_score >= WINNING_SCORE:
            game_over = True
            winner = 1
            play_sound("win")
        else:
            reset_ball()

def play_sound(sound_type):
    """Play game sounds."""
    if sound_type == "bounce":
        bounce_sound.play()
    elif sound_type == "hit":
        hit_sound.play()
    elif sound_type == "score":
        score_sound.play()
    elif sound_type == "win":
        win_sound.play()
    elif sound_type == "powerup":
        powerup_sound.play()

def draw_background():
    """Draw the game background with a gradient and stars."""
    # Create a dark gradient background
    for y in range(0, HEIGHT, 2):
        # Calculate gradient color (dark blue to black)
        gradient_factor = y / HEIGHT
        r = int(0 * (1 - gradient_factor))
        g = int(10 * (1 - gradient_factor))
        b = int(30 * (1 - gradient_factor))
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y), 2)
    
    # Draw twinkling stars
    for star in stars:
        x, y, size, brightness, _, _ = star
        color = (brightness, brightness, brightness)
        pygame.draw.circle(screen, color, (x, y), size)

def draw_objects():
    """Draw all game objects on the screen."""
    # Draw background
    draw_background()
    
    if not game_over and not game_paused:
        # Draw powerups
        for powerup in active_powerups:
            # Create pulsing effect
            pulse_factor = (math.sin(powerup['pulse']) + 1) / 2
            size_factor = 1 + 0.2 * pulse_factor
            glow_size = int(powerup['rect'].width * size_factor)
            
            # Draw glow
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*powerup['color'][:3], 100), 
                              (glow_size, glow_size), glow_size)
            screen.blit(glow_surface, (powerup['rect'].centerx - glow_size, powerup['rect'].centery - glow_size))
            
            # Draw powerup
            pygame.draw.circle(screen, powerup['color'], powerup['rect'].center, powerup['rect'].width // 2)
            
            # Draw icon based on powerup type
            if powerup['type'] == 'speed_boost':
                # Draw lightning bolt
                points = [
                    (powerup['rect'].centerx - 5, powerup['rect'].centery - 7),
                    (powerup['rect'].centerx + 2, powerup['rect'].centery - 2),
                    (powerup['rect'].centerx - 2, powerup['rect'].centery + 2),
                    (powerup['rect'].centerx + 5, powerup['rect'].centery + 7)
                ]
                pygame.draw.lines(screen, BLACK, False, points, 2)
            elif powerup['type'] == 'paddle_grow':
                # Draw plus sign
                pygame.draw.line(screen, BLACK, 
                                (powerup['rect'].centerx, powerup['rect'].centery - 5),
                                (powerup['rect'].centerx, powerup['rect'].centery + 5), 2)
                pygame.draw.line(screen, BLACK, 
                                (powerup['rect'].centerx - 5, powerup['rect'].centery),
                                (powerup['rect'].centerx + 5, powerup['rect'].centery), 2)
            elif powerup['type'] == 'paddle_shrink':
                # Draw minus sign
                pygame.draw.line(screen, BLACK, 
                                (powerup['rect'].centerx - 5, powerup['rect'].centery),
                                (powerup['rect'].centerx + 5, powerup['rect'].centery), 2)
            elif powerup['type'] == 'ball_size':
                # Draw circle
                pygame.draw.circle(screen, BLACK, powerup['rect'].center, 3)
        
        # Draw ball trail
        for i, (x, y) in enumerate(ball_trail):
            # Calculate size and alpha based on position in trail
            size = int(BALL_SIZE * (i / TRAIL_LENGTH) * 0.8)
            alpha = int(200 * (i / TRAIL_LENGTH))
            
            # Create a surface for the trail circle with transparency
            trail_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (*NEON_BLUE[:3], alpha), (size, size), size)
            screen.blit(trail_surface, (x - size, y - size))
        
        # Draw hit animations
        for anim in hit_animations:
            # Create a surface for the hit animation with transparency
            anim_surface = pygame.Surface((anim['radius'] * 2, anim['radius'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(anim_surface, (*anim['color'][:3], anim['alpha']), 
                              (anim['radius'], anim['radius']), anim['radius'])
            screen.blit(anim_surface, (anim['x'] - anim['radius'], anim['y'] - anim['radius']))
        
        # Draw paddles with glow effect
        for i, paddle in enumerate([player1_paddle, player2_paddle]):
            player_key = 'player1' if i == 0 else 'player2'
            paddle_color = NEON_GREEN
            
            # Change color based on active powerups
            if powerup_effects[player_key]['paddle_grow'] > 0:
                paddle_color = NEON_BLUE
            elif powerup_effects[player_key]['paddle_shrink'] > 0:
                paddle_color = NEON_RED
            elif powerup_effects[player_key]['speed_boost'] > 0:
                paddle_color = NEON_YELLOW
            
            # Draw glow
            glow_surface = pygame.Surface((paddle.width + 10, paddle.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*paddle_color[:3], 100), 
                            pygame.Rect(5, 5, paddle.width, paddle.height), 
                            border_radius=3)
            screen.blit(glow_surface, (paddle.x - 5, paddle.y - 5))
            
            # Draw paddle
            pygame.draw.rect(screen, paddle_color, paddle, border_radius=3)
        
        # Draw ball with glow
        ball_color = NEON_PINK
        if powerup_effects['ball']['size'] > 0:
            ball_color = NEON_PURPLE
            
        glow_surface = pygame.Surface((ball.width * 2 + 10, ball.height * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*ball_color[:3], 100), (ball.width + 5, ball.height + 5), ball.width + 5)
        screen.blit(glow_surface, (ball.x - 5, ball.y - 5))
        pygame.draw.ellipse(screen, ball_color, ball)
        
        # Draw the center line (dashed)
        for y in range(0, HEIGHT, 20):
            pygame.draw.rect(screen, NEON_PURPLE, (WIDTH // 2 - 1, y, 2, 10))
        
        # Draw scores with glow effect
        player1_text = font.render(str(player1_score), True, NEON_BLUE)
        player2_text = font.render(str(player2_score), True, NEON_BLUE)
        
        # Create glow surfaces
        glow_surface1 = pygame.Surface((player1_text.get_width() + 10, player1_text.get_height() + 10), pygame.SRCALPHA)
        glow_surface2 = pygame.Surface((player2_text.get_width() + 10, player2_text.get_height() + 10), pygame.SRCALPHA)
        
        # Render text on glow surfaces with alpha
        glow_text1 = font.render(str(player1_score), True, (*NEON_BLUE[:3], 100))
        glow_text2 = font.render(str(player2_score), True, (*NEON_BLUE[:3], 100))
        
        # Position and blit glow text
        glow_surface1.blit(glow_text1, (5, 5))
        glow_surface2.blit(glow_text2, (5, 5))
        
        # Blit glow surfaces
        screen.blit(glow_surface1, (WIDTH // 4 - 5, 20 - 5))
        screen.blit(glow_surface2, (3 * WIDTH // 4 - 5, 20 - 5))
        
        # Blit actual text
        screen.blit(player1_text, (WIDTH // 4, 20))
        screen.blit(player2_text, (3 * WIDTH // 4, 20))
        
        # Draw ball speed indicator
        speed_text = small_font.render(f"Ball Speed: {current_ball_speed:.2f}", True, NEON_GREEN)
        screen.blit(speed_text, (WIDTH // 2 - 80, 20))
        
        # Draw game mode and difficulty indicators
        mode_text = small_font.render("Two Player Mode" if two_player_mode else "AI Opponent", True, NEON_GREEN)
        diff_text = small_font.render(f"Difficulty: {current_difficulty}", True, NEON_GREEN)
        control_text = small_font.render(f"Control: {control_type.capitalize()}", True, NEON_GREEN)
        
        screen.blit(mode_text, (WIDTH // 2 - 80, HEIGHT - 60))
        screen.blit(diff_text, (WIDTH // 2 - 80, HEIGHT - 30))
        if not two_player_mode:
            screen.blit(control_text, (WIDTH // 2 - 80, HEIGHT - 90))
            
        # Draw FPS counter if enabled
        if show_fps:
            fps = int(clock.get_fps())
            fps_text = tiny_font.render(f"FPS: {fps}", True, WHITE)
            screen.blit(fps_text, (10, 10))
            
    elif game_paused:
        # Draw paused screen
        paused_text = font.render("PAUSED", True, NEON_GREEN)
        resume_text = small_font.render("Press P to resume", True, NEON_PINK)
        menu_text = small_font.render("Press M for menu", True, NEON_PINK)
        
        # Create glow effect
        glow_surface = pygame.Surface((paused_text.get_width() + 20, paused_text.get_height() + 20), pygame.SRCALPHA)
        glow_paused = font.render("PAUSED", True, (*NEON_GREEN[:3], 100))
        glow_surface.blit(glow_paused, (10, 10))
        
        # Position and blit
        screen.blit(glow_surface, (WIDTH // 2 - paused_text.get_width() // 2 - 10, HEIGHT // 2 - 100 - 10))
        screen.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2))
        screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 + 50))
        
    else:
        # Draw game over screen with neon effect
        winner_text = font.render(f"Player {winner} Wins!", True, NEON_GREEN)
        score_text = font.render(f"{player1_score} - {player2_score}", True, NEON_BLUE)
        restart_text = small_font.render("Press SPACE to play again", True, NEON_PINK)
        menu_text = small_font.render("Press M to return to menu", True, NEON_PINK)
        
        # Create glow surfaces
        glow_surface1 = pygame.Surface((winner_text.get_width() + 10, winner_text.get_height() + 10), pygame.SRCALPHA)
        glow_surface2 = pygame.Surface((score_text.get_width() + 10, score_text.get_height() + 10), pygame.SRCALPHA)
        
        # Render text on glow surfaces with alpha
        glow_winner = font.render(f"Player {winner} Wins!", True, (*NEON_GREEN[:3], 100))
        glow_score = font.render(f"{player1_score} - {player2_score}", True, (*NEON_BLUE[:3], 100))
        
        # Position and blit glow text
        glow_surface1.blit(glow_winner, (5, 5))
        glow_surface2.blit(glow_score, (5, 5))
        
        # Blit glow surfaces
        screen.blit(glow_surface1, (WIDTH // 2 - winner_text.get_width() // 2 - 5, HEIGHT // 2 - 100 - 5))
        screen.blit(glow_surface2, (WIDTH // 2 - score_text.get_width() // 2 - 5, HEIGHT // 2 - 5))
        
        # Blit actual text
        screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))
        screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 + 150))

def show_control_type_menu():
    """Display the control type selection menu for single player mode."""
    global control_type
    
    menu_active = True
    menu_stars = stars.copy()  # Copy stars for menu background
    
    while menu_active:
        # Update star animation
        for star in menu_stars:
            star[5] += star[4]
            pulse_factor = (math.sin(star[5]) + 1) / 2
            star[3] = int(100 + 155 * pulse_factor)
        
        # Draw background
        screen.fill(BLACK)
        
        # Draw stars
        for star in menu_stars:
            x, y, size, brightness, _, _ = star
            color = (brightness, brightness, brightness)
            pygame.draw.circle(screen, color, (x, y), size)
        
        # Draw title with glow effect
        title_text = font.render("SELECT CONTROL TYPE", True, NEON_BLUE)
        glow_surface = pygame.Surface((title_text.get_width() + 20, title_text.get_height() + 20), pygame.SRCALPHA)
        glow_title = font.render("SELECT CONTROL TYPE", True, (*NEON_BLUE[:3], 100))
        glow_surface.blit(glow_title, (10, 10))
        screen.blit(glow_surface, (WIDTH // 2 - title_text.get_width() // 2 - 10, 100 - 10))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Draw options with neon effect
        option1_text = small_font.render("1. Keyboard (W/S or Up/Down)", True, NEON_GREEN)
        option2_text = small_font.render("2. Mouse", True, NEON_GREEN)
        instructions_text = small_font.render("Press 1 or 2 to select control type", True, NEON_BLUE)
        
        screen.blit(option1_text, (WIDTH // 2 - option1_text.get_width() // 2, 220))
        screen.blit(option2_text, (WIDTH // 2 - option2_text.get_width() // 2, 270))
        screen.blit(instructions_text, (WIDTH // 2 - instructions_text.get_width() // 2, 350))
        
        pygame.display.flip()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    control_type = "keyboard"
                    menu_active = False
                elif event.key == pygame.K_2:
                    control_type = "mouse"
                    menu_active = False
                elif event.key == pygame.K_ESCAPE:
                    menu_active = False
        
        clock.tick(FPS)

def show_difficulty_menu():
    """Display the difficulty selection menu."""
    global current_difficulty, INITIAL_BALL_SPEED, MAX_BALL_SPEED, BALL_ACCELERATION, AI_SPEED
    
    menu_active = True
    menu_stars = stars.copy()  # Copy stars for menu background
    
    while menu_active:
        # Update star animation
        for star in menu_stars:
            star[5] += star[4]
            pulse_factor = (math.sin(star[5]) + 1) / 2
            star[3] = int(100 + 155 * pulse_factor)
        
        # Draw background
        screen.fill(BLACK)
        
        # Draw stars
        for star in menu_stars:
            x, y, size, brightness, _, _ = star
            color = (brightness, brightness, brightness)
            pygame.draw.circle(screen, color, (x, y), size)
        
        # Draw title with glow effect
        title_text = font.render("SELECT DIFFICULTY", True, NEON_BLUE)
        glow_surface = pygame.Surface((title_text.get_width() + 20, title_text.get_height() + 20), pygame.SRCALPHA)
        glow_title = font.render("SELECT DIFFICULTY", True, (*NEON_BLUE[:3], 100))
        glow_surface.blit(glow_title, (10, 10))
        screen.blit(glow_surface, (WIDTH // 2 - title_text.get_width() // 2 - 10, 100 - 10))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Draw options with neon effect
        option1_text = small_font.render("1. Easy", True, NEON_GREEN)
        option2_text = small_font.render("2. Medium", True, NEON_GREEN)
        option3_text = small_font.render("3. Hard", True, NEON_GREEN)
        instructions_text = small_font.render("Press 1, 2, or 3 to select difficulty", True, NEON_BLUE)
        
        # Draw difficulty descriptions
        easy_desc = small_font.render("Slower ball, more forgiving AI", True, NEON_PINK)
        medium_desc = small_font.render("Balanced gameplay", True, NEON_PINK)
        hard_desc = small_font.render("Faster ball, smarter AI", True, NEON_PINK)
        
        screen.blit(option1_text, (WIDTH // 2 - option1_text.get_width() // 2, 220))
        screen.blit(easy_desc, (WIDTH // 2 - easy_desc.get_width() // 2, 250))
        
        screen.blit(option2_text, (WIDTH // 2 - option2_text.get_width() // 2, 300))
        screen.blit(medium_desc, (WIDTH // 2 - medium_desc.get_width() // 2, 330))
        
        screen.blit(option3_text, (WIDTH // 2 - option3_text.get_width() // 2, 380))
        screen.blit(hard_desc, (WIDTH // 2 - hard_desc.get_width() // 2, 410))
        
        screen.blit(instructions_text, (WIDTH // 2 - instructions_text.get_width() // 2, 480))
        
        pygame.display.flip()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_difficulty = 'Easy'
                    menu_active = False
                elif event.key == pygame.K_2:
                    current_difficulty = 'Medium'
                    menu_active = False
                elif event.key == pygame.K_3:
                    current_difficulty = 'Hard'
                    menu_active = False
                elif event.key == pygame.K_ESCAPE:
                    menu_active = False
        
        clock.tick(FPS)
    
    # Update game settings based on difficulty
    INITIAL_BALL_SPEED = DIFFICULTY_SETTINGS[current_difficulty]['INITIAL_BALL_SPEED']
    MAX_BALL_SPEED = DIFFICULTY_SETTINGS[current_difficulty]['MAX_BALL_SPEED']
    BALL_ACCELERATION = DIFFICULTY_SETTINGS[current_difficulty]['BALL_ACCELERATION']
    AI_SPEED = DIFFICULTY_SETTINGS[current_difficulty]['AI_SPEED']

def show_main_menu():
    """Display the main menu with options: Start Game, Difficulty, Quit."""
    menu_active = True
    menu_stars = stars.copy()  # Copy stars for menu background
    
    while menu_active:
        # Update star animation
        for star in menu_stars:
            star[5] += star[4]
            pulse_factor = (math.sin(star[5]) + 1) / 2
            star[3] = int(100 + 155 * pulse_factor)
        
        # Draw background
        screen.fill(BLACK)
        
        # Draw stars
        for star in menu_stars:
            x, y, size, brightness, _, _ = star
            color = (brightness, brightness, brightness)
            pygame.draw.circle(screen, color, (x, y), size)
        
        # Draw title with glow effect
        title_text = font.render("NEON PONG", True, NEON_PINK)
        glow_surface = pygame.Surface((title_text.get_width() + 20, title_text.get_height() + 20), pygame.SRCALPHA)
        glow_title = font.render("NEON PONG", True, (*NEON_PINK[:3], 100))
        glow_surface.blit(glow_title, (10, 10))
        screen.blit(glow_surface, (WIDTH // 2 - title_text.get_width() // 2 - 10, 100 - 10))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Draw options with neon effect
        option1_text = small_font.render("1. Start Game", True, NEON_GREEN)
        option2_text = small_font.render("2. Change Difficulty", True, NEON_GREEN)
        option3_text = small_font.render("3. Toggle FPS Display", True, NEON_GREEN)
        option4_text = small_font.render("4. Quit", True, NEON_GREEN)
        instructions_text = small_font.render("Press 1-4 to select an option", True, NEON_BLUE)
        difficulty_text = small_font.render(f"Current Difficulty: {current_difficulty}", True, NEON_BLUE)
        
        screen.blit(option1_text, (WIDTH // 2 - option1_text.get_width() // 2, 220))
        screen.blit(option2_text, (WIDTH // 2 - option2_text.get_width() // 2, 270))
        screen.blit(option3_text, (WIDTH // 2 - option3_text.get_width() // 2, 320))
        screen.blit(option4_text, (WIDTH // 2 - option4_text.get_width() // 2, 370))
        screen.blit(instructions_text, (WIDTH // 2 - instructions_text.get_width() // 2, 450))
        screen.blit(difficulty_text, (WIDTH // 2 - difficulty_text.get_width() // 2, 500))
        
        pygame.display.flip()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    show_game_mode_menu()
                    menu_active = False
                elif event.key == pygame.K_2:
                    show_difficulty_menu()
                elif event.key == pygame.K_3:
                    global show_fps
                    show_fps = not show_fps
                elif event.key == pygame.K_4 or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        clock.tick(FPS)

def show_game_mode_menu():
    """Display the game mode selection menu."""
    global two_player_mode
    
    menu_active = True
    menu_stars = stars.copy()  # Copy stars for menu background
    
    while menu_active:
        # Update star animation
        for star in menu_stars:
            star[5] += star[4]
            pulse_factor = (math.sin(star[5]) + 1) / 2
            star[3] = int(100 + 155 * pulse_factor)
        
        # Draw background
        screen.fill(BLACK)
        
        # Draw stars
        for star in menu_stars:
            x, y, size, brightness, _, _ = star
            color = (brightness, brightness, brightness)
            pygame.draw.circle(screen, color, (x, y), size)
        
        # Draw title with glow effect
        title_text = font.render("SELECT GAME MODE", True, NEON_PINK)
        glow_surface = pygame.Surface((title_text.get_width() + 20, title_text.get_height() + 20), pygame.SRCALPHA)
        glow_title = font.render("SELECT GAME MODE", True, (*NEON_PINK[:3], 100))
        glow_surface.blit(glow_title, (10, 10))
        screen.blit(glow_surface, (WIDTH // 2 - title_text.get_width() // 2 - 10, 100 - 10))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Draw options with neon effect
        option1_text = small_font.render("1. Single Player (vs AI)", True, NEON_GREEN)
        option2_text = small_font.render("2. Two Players", True, NEON_GREEN)
        option3_text = small_font.render("B. Back to Main Menu", True, NEON_GREEN)
        instructions_text = small_font.render("Press 1 or 2 to select mode, B for main menu", True, NEON_BLUE)
        win_condition_text = small_font.render(f"First to {WINNING_SCORE} points wins!", True, NEON_BLUE)
        difficulty_text = small_font.render(f"Current Difficulty: {current_difficulty}", True, NEON_BLUE)
        
        screen.blit(option1_text, (WIDTH // 2 - option1_text.get_width() // 2, 220))
        screen.blit(option2_text, (WIDTH // 2 - option2_text.get_width() // 2, 270))
        screen.blit(option3_text, (WIDTH // 2 - option3_text.get_width() // 2, 320))
        screen.blit(instructions_text, (WIDTH // 2 - instructions_text.get_width() // 2, 400))
        screen.blit(win_condition_text, (WIDTH // 2 - win_condition_text.get_width() // 2, 450))
        screen.blit(difficulty_text, (WIDTH // 2 - difficulty_text.get_width() // 2, 500))
        
        pygame.display.flip()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    two_player_mode = False
                    show_control_type_menu()  # Ask for control type in single player mode
                    menu_active = False
                    reset_game()  # Reset game state
                elif event.key == pygame.K_2:
                    two_player_mode = True
                    menu_active = False
                    reset_game()  # Reset game state
                elif event.key == pygame.K_b:
                    show_main_menu()
                    menu_active = False
                elif event.key == pygame.K_ESCAPE:
                    show_main_menu()
                    menu_active = False
        
        clock.tick(FPS)

# Show main menu before starting the game
show_main_menu()

# Main game loop
while True:
    # Calculate delta time for frame-rate independent movement
    current_time = time.time()
    delta_time = current_time - last_frame_time
    last_frame_time = current_time
    
    # Cap delta time to prevent large jumps
    if delta_time > 0.05:
        delta_time = 0.05
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:  # Press M to return to menu
                show_main_menu()
            elif event.key == pygame.K_p:  # Press P to pause/unpause
                game_paused = not game_paused
            elif event.key == pygame.K_SPACE and game_over:  # Press SPACE to restart after game over
                reset_game()
            elif event.key == pygame.K_f:  # Toggle FPS display
                show_fps = not show_fps
    
    if not game_over and not game_paused:
        # Get keyboard input for Player 1 (left paddle)
        keys = pygame.key.get_pressed()
        
        # Handle Player 1 controls based on control type
        if control_type == "keyboard":
            # Allow both WASD and arrow keys for single player mode
            if keys[pygame.K_w] or (not two_player_mode and keys[pygame.K_UP]):
                move_paddle(player1_paddle, up=True, player='player1')
            if keys[pygame.K_s] or (not two_player_mode and keys[pygame.K_DOWN]):
                move_paddle(player1_paddle, up=False, player='player1')
        elif control_type == "mouse" and not two_player_mode:
            # Mouse control for Player 1
            mouse_y = pygame.mouse.get_pos()[1]
            move_paddle_mouse(player1_paddle, mouse_y)
        
        # Handle Player 2 input or AI
        if two_player_mode:
            # Player 2 controls (right paddle)
            if keys[pygame.K_UP]:
                move_paddle(player2_paddle, up=True, player='player2')
            if keys[pygame.K_DOWN]:
                move_paddle(player2_paddle, up=False, player='player2')
        else:
            # AI controls the right paddle
            move_ai_opponent()
        
        # Update game state
        update_ball()
        update_hit_animations()
        update_powerups()
        
        # Chance to spawn powerups
        spawn_powerup()
        
        # Check for powerup collisions
        check_powerup_collision()
    
    # Update stars animation
    update_stars()
    
    # Draw everything
    draw_objects()
    
    # Update the display
    pygame.display.flip()
    clock.tick(FPS)
