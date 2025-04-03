import pygame
import random
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FIELD_COLOR = (50, 150, 50)  # Greenish field
NUM_MEEPLES = 50

# Meeple Appearance
BODY_RADIUS = 10 # Radius for collision and main body part
HEAD_RADIUS_RATIO = 0.6 # Head radius relative to body radius
HEAD_V_OFFSET_RATIO = 0.8 # How much the head overlaps/sits above the body center
MEEPLE_BODY_COLOR = (200, 50, 50) # Reddish body
MEEPLE_HEAD_COLOR = (220, 70, 70) # Slightly lighter head
MEEPLE_SHADOW_COLOR = (30, 80, 30) # Darker green/grey for shadow/base
OUTLINE_COLOR = (20, 20, 20)
OUTLINE_WIDTH = 1 # Set to 0 to disable outline
SHADOW_OFFSET = 3 # How far the shadow is offset below the body base

# Simulation Parameters
MEEPLE_SPEED = 1.0 # Max pixels per frame
WANDER_STRENGTH = 0.1 # How much randomness in direction change
COLLISION_PUSH_FORCE = 0.5 # How strongly meeples push each other apart

# --- Meeple Class ---
class Meeple:
    def __init__(self, x, y, screen_width, screen_height):
        self.x = float(x)
        self.y = float(y) # Represents the center of the BODY circle
        self.body_radius = BODY_RADIUS
        self.head_radius = int(self.body_radius * HEAD_RADIUS_RATIO)
        self.head_v_offset = -int(self.body_radius * HEAD_V_OFFSET_RATIO) # Negative for upwards

        # Collision radius (based on the main body)
        self.collision_radius = self.body_radius

        self.screen_width = screen_width
        self.screen_height = screen_height

        # Movement vector
        angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(angle) * MEEPLE_SPEED
        self.dy = math.sin(angle) * MEEPLE_SPEED

        # Store colors (could be randomized later)
        self.body_color = MEEPLE_BODY_COLOR
        self.head_color = MEEPLE_HEAD_COLOR
        self.shadow_color = MEEPLE_SHADOW_COLOR
        self.outline_color = OUTLINE_COLOR


    def wander(self):
        """Applies a small random change to the direction vector."""
        angle_change = random.uniform(-WANDER_STRENGTH, WANDER_STRENGTH)
        current_angle = math.atan2(self.dy, self.dx)
        new_angle = current_angle + angle_change
        self.dx = math.cos(new_angle) * MEEPLE_SPEED
        self.dy = math.sin(new_angle) * MEEPLE_SPEED

    def move(self):
        """Updates position based on velocity and handles boundaries."""
        self.x += self.dx
        self.y += self.dy

        # Boundary check - use collision_radius for consistency
        buffer = self.collision_radius + OUTLINE_WIDTH # Account for outline too
        head_top_y = self.y + self.head_v_offset - self.head_radius

        if self.x - buffer < 0 or self.x + buffer > self.screen_width:
            self.dx *= -1
            self.x = max(buffer, min(self.x, self.screen_width - buffer))
        # Check boundaries based on the lowest (shadow) and highest (head) points
        if (self.y + SHADOW_OFFSET + self.body_radius) > self.screen_height or head_top_y - buffer < 0:
             self.dy *= -1
             # Clamp position to prevent sticking fully
             self.y = max(buffer - (self.head_v_offset - self.head_radius),
                          min(self.y, self.screen_height - (SHADOW_OFFSET + self.body_radius) - buffer))


    def draw(self, screen):
        """Draws the meeple with a body, head, shadow, and outline."""
        # Calculate positions
        body_pos = (int(self.x), int(self.y))
        head_pos = (int(self.x), int(self.y + self.head_v_offset))
        shadow_pos = (int(self.x), int(self.y + SHADOW_OFFSET))

        # --- Draw order matters for layering ---

        # 1. Shadow (widest part at the bottom)
        pygame.draw.circle(screen, self.shadow_color, shadow_pos, self.body_radius)

        # 2. Outlines (optional)
        if OUTLINE_WIDTH > 0:
            # Body Outline (drawn slightly larger)
            pygame.draw.circle(screen, self.outline_color, body_pos, self.body_radius + OUTLINE_WIDTH)
            # Head Outline
            pygame.draw.circle(screen, self.outline_color, head_pos, self.head_radius + OUTLINE_WIDTH)

        # 3. Body Fill
        pygame.draw.circle(screen, self.body_color, body_pos, self.body_radius)

        # 4. Head Fill
        pygame.draw.circle(screen, self.head_color, head_pos, self.head_radius)

# --- Collision Detection & Resolution ---
def handle_collisions(meeples):
    """Checks for collisions based on body radius and pushes meeples apart."""
    for i in range(len(meeples)):
        for j in range(i + 1, len(meeples)):
            m1 = meeples[i]
            m2 = meeples[j]

            dist_x = m1.x - m2.x
            dist_y = m1.y - m2.y # Collision based on body centers
            dist_sq = dist_x**2 + dist_y**2
            # Use collision_radius (which is body_radius here)
            min_dist = m1.collision_radius + m2.collision_radius
            min_dist_sq = min_dist**2

            if dist_sq < min_dist_sq and dist_sq > 0.001 :
                distance = math.sqrt(dist_sq)
                # Add a small buffer to push them apart slightly more than touching
                overlap = (min_dist - distance + (OUTLINE_WIDTH * 2)) / 2.0 # Account for outlines
                overlap = max(0, overlap) # Ensure overlap is not negative

                push_x = dist_x / distance
                push_y = dist_y / distance

                # Apply push force
                m1.x += push_x * overlap * COLLISION_PUSH_FORCE
                m1.y += push_y * overlap * COLLISION_PUSH_FORCE
                m2.x -= push_x * overlap * COLLISION_PUSH_FORCE
                m2.y -= push_y * overlap * COLLISION_PUSH_FORCE


# --- Main Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Meeple Population Simulation (3D Look)")
clock = pygame.time.Clock()

# --- Create Meeples ---
meeples = []
center_x = SCREEN_WIDTH // 2
center_y = SCREEN_HEIGHT // 2
spawn_radius = 70 # Increase spawn radius slightly

for _ in range(NUM_MEEPLES):
    placed = False
    attempts = 0
    while not placed and attempts < 100:
        angle = random.uniform(0, 2 * math.pi)
        radius_offset = random.uniform(0, spawn_radius)
        x = center_x + math.cos(angle) * radius_offset
        y = center_y + math.sin(angle) * radius_offset

        # Check initial position against screen bounds (using approx bounds)
        buffer = BODY_RADIUS + OUTLINE_WIDTH
        head_top_y_approx = y - int(BODY_RADIUS * HEAD_V_OFFSET_RATIO) - int(BODY_RADIUS * HEAD_RADIUS_RATIO)
        if x - buffer < 0 or x + buffer > SCREEN_WIDTH or \
           y + SHADOW_OFFSET + BODY_RADIUS > SCREEN_HEIGHT or head_top_y_approx - buffer < 0:
            attempts += 1
            continue # Try a different spot if it's potentially out of bounds

        new_meeple = Meeple(x, y, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Check for overlap with existing meeples (using collision radius)
        overlapping = False
        for existing_meeple in meeples:
            dist_x = new_meeple.x - existing_meeple.x
            dist_y = new_meeple.y - existing_meeple.y
            dist_sq = dist_x**2 + dist_y**2
            min_dist_sq = (new_meeple.collision_radius + existing_meeple.collision_radius)**2
            if dist_sq < min_dist_sq:
                overlapping = True
                break

        if not overlapping:
            meeples.append(new_meeple)
            placed = True
        attempts += 1

    if attempts >= 100:
        print(f"Warning: Could not place meeple {_ + 1} without overlap after 100 attempts.")


# --- Game Loop ---
running = True
while running:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update Meeples
    for meeple in meeples:
        meeple.wander()
        meeple.move()

    # Handle Collisions
    for _ in range(2): # Multiple passes help stability
        handle_collisions(meeples)

    # Drawing
    screen.fill(FIELD_COLOR)
    # Sort by body's Y position for correct drawing order
    meeples_sorted = sorted(meeples, key=lambda m: m.y)
    for meeple in meeples_sorted:
        meeple.draw(screen)

    pygame.display.flip()
    clock.tick(60)

# --- Cleanup ---
pygame.quit()
