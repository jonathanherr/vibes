import pygame
import random
import math
import time # For hurricane/rain duration

# --- Constants ---
TOOLBAR_WIDTH = 100
SIMULATION_WIDTH = 800
SCREEN_WIDTH = SIMULATION_WIDTH + TOOLBAR_WIDTH
SCREEN_HEIGHT = 600

FIELD_COLOR = (50, 150, 50)  # Greenish field
TOOLBAR_COLOR = (100, 100, 100) # Grey
ICON_SIZE = 60
ICON_PADDING = 10
ICON_SELECTED_COLOR = (255, 255, 0) # Yellow highlight
ICON_DEFAULT_COLOR = (150, 150, 150) # Darker grey

NUM_MEEPLES = 50

# Meeple Appearance (as before)
BODY_RADIUS = 10
HEAD_RADIUS_RATIO = 0.6
HEAD_V_OFFSET_RATIO = 0.8
MEEPLE_BODY_COLOR = (200, 50, 50)
MEEPLE_HEAD_COLOR = (220, 70, 70)
MEEPLE_SHADOW_COLOR = (30, 80, 30)
OUTLINE_COLOR = (20, 20, 20)
OUTLINE_WIDTH = 1
SHADOW_OFFSET = 3

# Simulation Parameters
MEEPLE_BASE_SPEED = 1.0 # Base speed
WANDER_STRENGTH = 0.1
COLLISION_PUSH_FORCE = 0.5
OBSTACLE_PUSH_FORCE = 1.0 # How strongly meeples are pushed from obstacles

# Tool Specific Constants
HOLE_RADIUS = 30
HOLE_COLOR = (0, 0, 0)

BUILDING_SIZE = (60, 80) # Width, Height
BUILDING_COLOR = (120, 120, 140)
BUILDING_OUTLINE_COLOR = (40, 40, 50)

TREE_RADIUS = 15 # Collision radius for trunk
TREE_CANOPY_COLOR = (30, 100, 30)
TREE_TRUNK_COLOR = (100, 60, 20)
TREE_TRUNK_WIDTH = 6

HURRICANE_RADIUS = 100
HURRICANE_STRENGTH = 0.8 # Force applied
HURRICANE_DURATION = 8 # Seconds
HURRICANE_VISUAL_COLOR = (150, 150, 200, 100) # Semi-transparent blueish

RAIN_DURATION = 10 # Seconds
RAIN_SPEED_MULTIPLIER = 0.6 # Slowdown factor
RAIN_DROP_COLOR = (100, 100, 200)
RAIN_DROP_LENGTH = 5
NUM_RAIN_DROPS = 200

# --- Tool Definitions ---
TOOLS = ["hole", "building", "hurricane", "tree", "rain"]
TOOL_ICONS = {
    "hole": {"color": (10, 10, 10), "shape": "circle"},
    "building": {"color": (110, 110, 130), "shape": "rect"},
    "hurricane": {"color": (100, 100, 180), "shape": "swirl"}, # Placeholder
    "tree": {"color": (40, 110, 40), "shape": "tree"}, # Placeholder
    "rain": {"color": (80, 80, 150), "shape": "drops"} # Placeholder
}

# --- Classes ---

class Meeple:
    def __init__(self, x, y, screen_width, screen_height):
        self.x = float(x)
        self.y = float(y)
        self.body_radius = BODY_RADIUS
        self.head_radius = int(self.body_radius * HEAD_RADIUS_RATIO)
        self.head_v_offset = -int(self.body_radius * HEAD_V_OFFSET_RATIO)
        self.collision_radius = self.body_radius
        self.sim_width = screen_width # Store simulation area width
        self.sim_height = screen_height

        angle = random.uniform(0, 2 * math.pi)
        self.speed_multiplier = 1.0 # For effects like rain
        self.dx = math.cos(angle) * MEEPLE_BASE_SPEED * self.speed_multiplier
        self.dy = math.sin(angle) * MEEPLE_BASE_SPEED * self.speed_multiplier

        self.body_color = MEEPLE_BODY_COLOR
        self.head_color = MEEPLE_HEAD_COLOR
        self.shadow_color = MEEPLE_SHADOW_COLOR
        self.outline_color = OUTLINE_COLOR

        # Add a force accumulator for effects like hurricane
        self.force_x = 0.0
        self.force_y = 0.0

    def apply_force(self, fx, fy):
        self.force_x += fx
        self.force_y += fy

    def wander(self):
        angle_change = random.uniform(-WANDER_STRENGTH, WANDER_STRENGTH)
        current_angle = math.atan2(self.dy, self.dx)
        new_angle = current_angle + angle_change
        current_speed = MEEPLE_BASE_SPEED * self.speed_multiplier
        self.dx = math.cos(new_angle) * current_speed
        self.dy = math.sin(new_angle) * current_speed

    def move(self):
        # Apply accumulated forces (like from hurricane)
        self.dx += self.force_x
        self.dy += self.force_y
        # Reset forces for next frame
        self.force_x = 0.0
        self.force_y = 0.0

        # Simple speed limit after applying force (optional)
        speed_sq = self.dx**2 + self.dy**2
        max_speed = MEEPLE_BASE_SPEED * self.speed_multiplier * 1.5 # Allow boost from force
        if speed_sq > max_speed**2:
           speed = math.sqrt(speed_sq)
           self.dx = (self.dx / speed) * max_speed
           self.dy = (self.dy / speed) * max_speed


        self.x += self.dx
        self.y += self.dy

        # Boundary check (using SIMULATION_WIDTH now)
        buffer = self.collision_radius + OUTLINE_WIDTH
        head_top_y = self.y + self.head_v_offset - self.head_radius

        if self.x - buffer < 0:
            self.dx = abs(self.dx) # Bounce right
            self.x = buffer
        elif self.x + buffer > self.sim_width:
            self.dx = -abs(self.dx) # Bounce left
            self.x = self.sim_width - buffer

        if head_top_y - buffer < 0:
             self.dy = abs(self.dy) # Bounce down
             self.y = buffer - (self.head_v_offset - self.head_radius)
        elif (self.y + SHADOW_OFFSET + self.body_radius + buffer) > self.sim_height:
             self.dy = -abs(self.dy) # Bounce up
             self.y = self.sim_height - (SHADOW_OFFSET + self.body_radius) - buffer


    def draw(self, screen):
        body_pos = (int(self.x), int(self.y))
        head_pos = (int(self.x), int(self.y + self.head_v_offset))
        shadow_pos = (int(self.x), int(self.y + SHADOW_OFFSET))

        pygame.draw.circle(screen, self.shadow_color, shadow_pos, self.body_radius)
        if OUTLINE_WIDTH > 0:
            pygame.draw.circle(screen, self.outline_color, body_pos, self.body_radius + OUTLINE_WIDTH)
            pygame.draw.circle(screen, self.outline_color, head_pos, self.head_radius + OUTLINE_WIDTH)
        pygame.draw.circle(screen, self.body_color, body_pos, self.body_radius)
        pygame.draw.circle(screen, self.head_color, head_pos, self.head_radius)

class Hole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = HOLE_RADIUS
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, screen):
        pygame.draw.circle(screen, HOLE_COLOR, (self.x, self.y), self.radius)

class Building:
    def __init__(self, center_x, center_y):
        self.width, self.height = BUILDING_SIZE
        self.rect = pygame.Rect(center_x - self.width // 2, center_y - self.height // 2, self.width, self.height)
        self.color = BUILDING_COLOR
        self.outline_color = BUILDING_OUTLINE_COLOR

    def draw(self, screen):
        pygame.draw.rect(screen, self.outline_color, self.rect.inflate(OUTLINE_WIDTH*2, OUTLINE_WIDTH*2))
        pygame.draw.rect(screen, self.color, self.rect)

class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y # Base of the trunk
        self.trunk_radius = TREE_TRUNK_WIDTH // 2 # For collision
        self.collision_radius = self.trunk_radius # Collide only with trunk base for simplicity
        self.canopy_radius = TREE_RADIUS
        self.canopy_color = TREE_CANOPY_COLOR
        self.trunk_color = TREE_TRUNK_COLOR
        # Collision rect centered on the trunk base for obstacle checks
        self.collision_rect = pygame.Rect(x - self.collision_radius, y - self.collision_radius,
                                          self.collision_radius * 2, self.collision_radius * 2)


    def draw(self, screen):
        # Draw canopy higher up
        canopy_y = self.y - self.canopy_radius // 2
        pygame.draw.circle(screen, self.canopy_color, (self.x, canopy_y), self.canopy_radius)
        # Draw trunk
        trunk_height = self.canopy_radius # Make trunk reach bottom of canopy roughly
        pygame.draw.line(screen, self.trunk_color, (self.x, self.y), (self.x, canopy_y), TREE_TRUNK_WIDTH)

class Hurricane:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = HURRICANE_RADIUS
        self.strength = HURRICANE_STRENGTH
        self.end_time = time.time() + HURRICANE_DURATION
        self.max_radius_sq = self.radius * self.radius

    def is_active(self):
        return time.time() < self.end_time

    def apply_effect(self, meeple):
        dist_x = meeple.x - self.x
        dist_y = meeple.y - self.y
        dist_sq = dist_x**2 + dist_y**2

        if dist_sq < self.max_radius_sq and dist_sq > 0.01:
            distance = math.sqrt(dist_sq)
            # Normalized direction vector from center to meeple
            norm_x = dist_x / distance
            norm_y = dist_y / distance

            # Tangential force (rotate normalized vector 90 degrees: (-y, x))
            force_x = -norm_y * self.strength
            force_y = norm_x * self.strength

            # Optional: Add a slight outward push
            force_x += norm_x * self.strength * 0.1
            force_y += norm_y * self.strength * 0.1

            meeple.apply_force(force_x, force_y)

    def draw(self, screen):
        # Draw a semi-transparent circle as a visual indicator
        # Need a surface for transparency
        surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, HURRICANE_VISUAL_COLOR, (self.radius, self.radius), self.radius)
        screen.blit(surface, (self.x - self.radius, self.y - self.radius))

# --- Global State ---
meeples = []
holes = []
buildings = []
trees = []
active_effects = [] # For hurricanes, maybe other timed effects
is_raining = False
rain_end_time = 0
rain_drop_positions = []

selected_tool = None

# --- Helper Functions ---

def draw_toolbar(screen, selected_tool):
    pygame.draw.rect(screen, TOOLBAR_COLOR, (SIMULATION_WIDTH, 0, TOOLBAR_WIDTH, SCREEN_HEIGHT))
    
    icon_y = ICON_PADDING
    for i, tool_name in enumerate(TOOLS):
        icon_rect = pygame.Rect(SIMULATION_WIDTH + ICON_PADDING, icon_y, ICON_SIZE, ICON_SIZE)

        # Draw selection highlight
        if tool_name == selected_tool:
            pygame.draw.rect(screen, ICON_SELECTED_COLOR, icon_rect.inflate(4, 4), border_radius=5)

        # Draw simple placeholder icon
        icon_info = TOOL_ICONS[tool_name]
        icon_center = icon_rect.center

        # Simple shape drawing for icons (replace with images later if desired)
        if icon_info["shape"] == "circle":
             pygame.draw.circle(screen, icon_info["color"], icon_center, ICON_SIZE // 2 - 4)
        elif icon_info["shape"] == "rect":
             pygame.draw.rect(screen, icon_info["color"], icon_rect.inflate(-8, -8))
        elif icon_info["shape"] == "swirl": # Placeholder swirl
             pygame.draw.circle(screen, icon_info["color"], icon_center, ICON_SIZE // 2 - 4, 3)
             pygame.draw.circle(screen, icon_info["color"], icon_center, ICON_SIZE // 3 - 4, 3)
        elif icon_info["shape"] == "tree": # Placeholder tree
             pygame.draw.rect(screen, (100,60,20), (icon_center[0]-3, icon_center[1], 6, ICON_SIZE//2 - 4))
             pygame.draw.circle(screen, icon_info["color"], (icon_center[0], icon_center[1]-ICON_SIZE//4), ICON_SIZE // 3)
        elif icon_info["shape"] == "drops": # Placeholder rain
            for _ in range(3):
                rx = random.randint(icon_rect.left + 5, icon_rect.right - 5)
                ry = random.randint(icon_rect.top + 5, icon_rect.bottom - 10)
                pygame.draw.line(screen, icon_info["color"], (rx, ry), (rx, ry+5), 2)


        icon_y += ICON_SIZE + ICON_PADDING


def handle_collisions(meeples, buildings, trees):
    meeples_to_remove = []

    # Meeple-Meeple Collisions
    for i in range(len(meeples)):
        if meeples[i] in meeples_to_remove: continue
        for j in range(i + 1, len(meeples)):
            if meeples[j] in meeples_to_remove: continue

            m1 = meeples[i]
            m2 = meeples[j]
            dist_x = m1.x - m2.x
            dist_y = m1.y - m2.y
            dist_sq = dist_x**2 + dist_y**2
            min_dist = m1.collision_radius + m2.collision_radius
            min_dist_sq = min_dist**2

            if dist_sq < min_dist_sq and dist_sq > 0.001 :
                distance = math.sqrt(dist_sq)
                overlap = (min_dist - distance + (OUTLINE_WIDTH * 1)) / 2.0 # Adjusted buffer
                overlap = max(0, overlap)

                push_x = dist_x / distance
                push_y = dist_y / distance

                m1.x += push_x * overlap * COLLISION_PUSH_FORCE
                m1.y += push_y * overlap * COLLISION_PUSH_FORCE
                m2.x -= push_x * overlap * COLLISION_PUSH_FORCE
                m2.y -= push_y * overlap * COLLISION_PUSH_FORCE

    # Meeple-Obstacle Collisions
    obstacles = buildings + trees # Combine obstacle lists for easier iteration

    for meeple in meeples:
        if meeple in meeples_to_remove: continue

        meeple_rect = pygame.Rect(meeple.x - meeple.collision_radius,
                                  meeple.y - meeple.collision_radius,
                                  meeple.collision_radius * 2,
                                  meeple.collision_radius * 2)

        for obstacle in obstacles:
            # Use specific collision shape for each obstacle type
            if isinstance(obstacle, Building):
                obstacle_col_rect = obstacle.rect
            elif isinstance(obstacle, Tree):
                 obstacle_col_rect = obstacle.collision_rect # Use the smaller trunk rect for collision
            else:
                 continue # Should not happen

            if meeple_rect.colliderect(obstacle_col_rect):
                # Simple push away from obstacle center
                center_x_obs, center_y_obs = obstacle_col_rect.center
                dist_x = meeple.x - center_x_obs
                dist_y = meeple.y - center_y_obs
                dist = math.hypot(dist_x, dist_y)

                if dist < 0.01: # Avoid division by zero if perfectly centered
                    dist = 0.01
                    dist_x = 0.01

                # Calculate push vector (normalized)
                push_x = dist_x / dist
                push_y = dist_y / dist

                # Push slightly beyond the collision radius
                # This part is tricky with rectangles; simplified push:
                push_magnitude = OBSTACLE_PUSH_FORCE # Constant push force when colliding

                meeple.x += push_x * push_magnitude
                meeple.y += push_y * push_magnitude

                # Optional: Dampen velocity component towards obstacle
                dot_product = meeple.dx * push_x + meeple.dy * push_y
                if dot_product < 0: # If moving towards obstacle center
                    meeple.dx -= dot_product * push_x * 0.5 # Reduce velocity towards obstacle
                    meeple.dy -= dot_product * push_y * 0.5


    # Meeple-Hole Collisions (Check for removal)
    for hole in holes:
        for meeple in meeples:
            if meeple in meeples_to_remove: continue
            dist_x = meeple.x - hole.x
            dist_y = meeple.y - hole.y
            dist_sq = dist_x**2 + dist_y**2
            if dist_sq < (hole.radius * 0.8)**2: # Fall in if center gets close enough
                if meeple not in meeples_to_remove:
                    meeples_to_remove.append(meeple)

    # Remove meeples marked for removal
    # Important: Iterate safely or create a new list
    original_count = len(meeples)
    meeples[:] = [m for m in meeples if m not in meeples_to_remove]
    #if original_count > len(meeples):
    #    print(f"Removed {original_count - len(meeples)} meeples.") # Debugging


def initialize_rain_drops():
    global rain_drop_positions
    rain_drop_positions = []
    for _ in range(NUM_RAIN_DROPS):
        x = random.randint(0, SIMULATION_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        rain_drop_positions.append([x, y])

def update_and_draw_rain(screen):
    global rain_drop_positions
    if not is_raining:
        return

    for i in range(len(rain_drop_positions)):
        # Move drop down
        rain_drop_positions[i][1] += 4 # Rain speed
        # Reset drop if it goes off screen
        if rain_drop_positions[i][1] > SCREEN_HEIGHT:
            rain_drop_positions[i][0] = random.randint(0, SIMULATION_WIDTH)
            rain_drop_positions[i][1] = random.randint(-20, -5) # Start off screen top

        # Draw drop
        start_pos = (rain_drop_positions[i][0], rain_drop_positions[i][1])
        end_pos = (rain_drop_positions[i][0], rain_drop_positions[i][1] + RAIN_DROP_LENGTH)
        pygame.draw.line(screen, RAIN_DROP_COLOR, start_pos, end_pos, 1)

# --- Main Setup ---
pygame.init()
# Adjust display flags if needed for transparency (e.g. hurricane)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Meeple Population Simulation - Interactive")
clock = pygame.time.Clock()

# --- Create Initial Meeples ---
center_x = SIMULATION_WIDTH // 2
center_y = SCREEN_HEIGHT // 2
spawn_radius = 70

for _ in range(NUM_MEEPLES):
    placed = False
    attempts = 0
    while not placed and attempts < 100:
        angle = random.uniform(0, 2 * math.pi)
        radius_offset = random.uniform(0, spawn_radius)
        x = center_x + math.cos(angle) * radius_offset
        y = center_y + math.sin(angle) * radius_offset

        buffer = BODY_RADIUS + OUTLINE_WIDTH
        head_top_y_approx = y - int(BODY_RADIUS * HEAD_V_OFFSET_RATIO) - int(BODY_RADIUS * HEAD_RADIUS_RATIO)
        if x - buffer < 0 or x + buffer > SIMULATION_WIDTH or \
           y + SHADOW_OFFSET + BODY_RADIUS > SCREEN_HEIGHT or head_top_y_approx - buffer < 0:
            attempts += 1
            continue

        # Use Meeple class constructor directly now
        new_meeple = Meeple(x, y, SIMULATION_WIDTH, SCREEN_HEIGHT)

        overlapping = False
        # Check overlap with existing meeples
        for existing_meeple in meeples:
            dist_x = new_meeple.x - existing_meeple.x
            dist_y = new_meeple.y - existing_meeple.y
            dist_sq = dist_x**2 + dist_y**2
            min_dist_sq = (new_meeple.collision_radius + existing_meeple.collision_radius)**2
            if dist_sq < min_dist_sq:
                overlapping = True
                break
        # Check overlap with initial obstacles if any (none here yet)

        if not overlapping:
            meeples.append(new_meeple)
            placed = True
        attempts += 1
    # Warning if placement failed is omitted for brevity but good to have


# --- Game Loop ---
running = True
while running:
    current_time = time.time()

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Check for Toolbar Click
            if mouse_x >= SIMULATION_WIDTH:
                icon_y = ICON_PADDING
                for tool_name in TOOLS:
                    icon_rect = pygame.Rect(SIMULATION_WIDTH + ICON_PADDING, icon_y, ICON_SIZE, ICON_SIZE)
                    if icon_rect.collidepoint(mouse_x, mouse_y):
                        if selected_tool == tool_name:
                             selected_tool = None # Click again to deselect
                        else:
                            selected_tool = tool_name
                        print(f"Selected tool: {selected_tool}")
                        break # Found clicked icon
                    icon_y += ICON_SIZE + ICON_PADDING
            # Check for Simulation Area Click (Tool Use)
            elif selected_tool is not None:
                print(f"Using tool {selected_tool} at ({mouse_x}, {mouse_y})")
                if selected_tool == "hole":
                    holes.append(Hole(mouse_x, mouse_y))
                elif selected_tool == "building":
                    buildings.append(Building(mouse_x, mouse_y))
                elif selected_tool == "tree":
                     # Place tree base at mouse y
                    trees.append(Tree(mouse_x, mouse_y))
                elif selected_tool == "hurricane":
                    # Only allow one hurricane at a time for simplicity
                    active_effects = [e for e in active_effects if not isinstance(e, Hurricane)]
                    active_effects.append(Hurricane(mouse_x, mouse_y))
                elif selected_tool == "rain":
                    if not is_raining:
                        is_raining = True
                        rain_end_time = current_time + RAIN_DURATION
                        initialize_rain_drops()
                        print("Started raining.")
                    else:
                        is_raining = False # Click again to stop early? Or let it time out.
                        print("Stopped raining.")

                # Optional: Deselect tool after use?
                # selected_tool = None

    # --- Update Phase ---

    # Update timed effects (Rain, Hurricane)
    if is_raining and current_time > rain_end_time:
        is_raining = False
        print("Rain stopped.")

    active_effects = [e for e in active_effects if e.is_active()] # Remove expired effects

    # Apply effects and update meeples
    current_speed_multiplier = RAIN_SPEED_MULTIPLIER if is_raining else 1.0
    for meeple in meeples:
        meeple.speed_multiplier = current_speed_multiplier # Set speed based on rain
        # Apply forces from active effects (e.g., hurricane)
        for effect in active_effects:
            if hasattr(effect, 'apply_effect'):
                effect.apply_effect(meeple)

        meeple.wander()
        meeple.move()

    # --- Collision Handling ---
    handle_collisions(meeples, buildings, trees) # Also handles hole removal

    # --- Drawing Phase ---
    # Draw Field
    screen.fill(FIELD_COLOR)

    # Draw Environment Objects (drawn first, below meeples)
    for hole in holes:
        hole.draw(screen)
    for building in buildings:
        building.draw(screen)
    # Draw trees sorted by Y base for correct overlap
    trees_sorted = sorted(trees, key=lambda t: t.y)
    for tree in trees_sorted:
        tree.draw(screen)

    # Draw Meeples (sorted by Y for depth illusion)
    meeples_sorted = sorted(meeples, key=lambda m: m.y)
    for meeple in meeples_sorted:
        meeple.draw(screen)

    # Draw Active Effects Visuals (e.g., hurricane swirls)
    for effect in active_effects:
        if hasattr(effect, 'draw'):
            effect.draw(screen)

    # Draw Rain (on top)
    if is_raining:
        update_and_draw_rain(screen)


    # Draw Toolbar (on top of everything else)
    draw_toolbar(screen, selected_tool)

    # Update Display
    pygame.display.flip()

    # Frame Rate Control
    clock.tick(60)

# --- Cleanup ---
pygame.quit()
