import pygame
import random
import math
import time

# --- Constants ---
TOOLBAR_WIDTH = 100
SIMULATION_WIDTH = 800
SCREEN_WIDTH = SIMULATION_WIDTH + TOOLBAR_WIDTH
SCREEN_HEIGHT = 600

FIELD_COLOR = (50, 150, 50)
TOOLBAR_COLOR = (100, 100, 100)
ICON_SIZE = 60
ICON_PADDING = 10
ICON_SELECTED_COLOR = (255, 255, 0)
ICON_DEFAULT_COLOR = (150, 150, 150)
INFO_TEXT_COLOR = (240, 240, 240)

# Initial Meeple Count
INITIAL_NUM_MEEPLES = 50 # Renamed from NUM_MEEPLES

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
MEEPLE_BASE_SPEED = 1.0
WANDER_STRENGTH = 0.1
COLLISION_PUSH_FORCE = 0.5
OBSTACLE_PUSH_FORCE = 1.0

# --- Speed Control ---
simulation_speed_multiplier = 1.0 # Global speed multiplier
SPEED_CHANGE_STEP = 0.2
MIN_SPEED_MULT = 0.2
MAX_SPEED_MULT = 5.0

# Tool Specific Constants
HOLE_RADIUS = 30
HOLE_COLOR = (0, 0, 0)

# --- Building/Hut Appearance ---
HUT_BASE_SIZE = (60, 40) # Width, Height of base rectangle
HUT_ROOF_HEIGHT = 40
HUT_WALL_COLOR = (180, 140, 100) # Beige/Brown
HUT_ROOF_COLOR = (139, 69, 19) # Saddle Brown (for thatch)
HUT_THATCH_LINE_COLOR = (80, 40, 10) # Darker brown
HUT_OUTLINE_COLOR = (40, 40, 20)

TREE_RADIUS = 15
TREE_CANOPY_COLOR = (30, 100, 30)
TREE_TRUNK_COLOR = (100, 60, 20)
TREE_TRUNK_WIDTH = 6

HURRICANE_RADIUS = 100
HURRICANE_STRENGTH = 0.8
HURRICANE_DURATION = 8
HURRICANE_VISUAL_COLOR = (150, 150, 200, 100)

RAIN_DURATION = 10
RAIN_SPEED_MULTIPLIER = 0.6 # Meeple slowdown factor
RAIN_DROP_COLOR = (100, 100, 200)
RAIN_DROP_LENGTH = 5
NUM_RAIN_DROPS = 200
RAIN_DROP_BASE_SPEED = 4 # Pixels per frame base speed

# --- Tool Definitions ---
# Added 'add_meeple'
TOOLS = ["hole", "building", "hurricane", "tree", "rain", "add_meeple"]
TOOL_ICONS = {
    "hole": {"color": (10, 10, 10), "shape": "circle"},
    "building": {"color": HUT_WALL_COLOR, "shape": "hut"}, # Updated icon placeholder
    "hurricane": {"color": (100, 100, 180), "shape": "swirl"},
    "tree": {"color": (40, 110, 40), "shape": "tree"},
    "rain": {"color": (80, 80, 150), "shape": "drops"},
    "add_meeple": {"color": MEEPLE_BODY_COLOR, "shape": "meeple_plus"} # New icon placeholder
}

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Meeple Population Simulation - Interactive")
clock = pygame.time.Clock()
# Font for displaying info
info_font = pygame.font.SysFont(None, 24)

# --- Classes ---

class Meeple:
    def __init__(self, x, y, sim_width, sim_height): # Pass sim area dimensions
        self.x = float(x)
        self.y = float(y)
        self.body_radius = BODY_RADIUS
        self.head_radius = int(self.body_radius * HEAD_RADIUS_RATIO)
        self.head_v_offset = -int(self.body_radius * HEAD_V_OFFSET_RATIO)
        self.collision_radius = self.body_radius
        self.sim_width = sim_width
        self.sim_height = sim_height

        self.speed_multiplier = 1.0 # For effects like rain
        self._update_velocity_vector() # Initialize dx/dy based on current speed settings

        self.body_color = MEEPLE_BODY_COLOR
        self.head_color = MEEPLE_HEAD_COLOR
        self.shadow_color = MEEPLE_SHADOW_COLOR
        self.outline_color = OUTLINE_COLOR

        self.force_x = 0.0
        self.force_y = 0.0

    def _update_velocity_vector(self, current_angle=None):
        """Sets dx/dy based on current speed state and an angle."""
        # Global simulation speed + individual multiplier (rain)
        effective_speed = MEEPLE_BASE_SPEED * simulation_speed_multiplier * self.speed_multiplier
        if current_angle is None:
            current_angle = random.uniform(0, 2 * math.pi) # Initial random angle

        self.dx = math.cos(current_angle) * effective_speed
        self.dy = math.sin(current_angle) * effective_speed

    def apply_force(self, fx, fy):
        # Scale applied force by simulation speed? No, let the resulting velocity change reflect speed.
        self.force_x += fx
        self.force_y += fy

    def wander(self):
        """Applies random direction change, respecting current speed."""
        angle_change = random.uniform(-WANDER_STRENGTH, WANDER_STRENGTH)
        # Calculate angle based on potentially force-modified velocity
        current_angle = math.atan2(self.dy, self.dx)
        new_angle = current_angle + angle_change
        # Update dx/dy based on the new angle and current effective speed
        self._update_velocity_vector(new_angle)


    def move(self):
        # Apply accumulated forces
        # The effect of the force scales naturally with the simulation speed multiplier
        # because it adds to dx/dy which are used over the (effectively shorter) time step.
        self.dx += self.force_x
        self.dy += self.force_y
        self.force_x = 0.0
        self.force_y = 0.0

        # Speed limit check (optional, scales with speed mult)
        effective_max_speed = MEEPLE_BASE_SPEED * simulation_speed_multiplier * self.speed_multiplier * 1.5
        speed_sq = self.dx**2 + self.dy**2
        if speed_sq > effective_max_speed**2:
           speed = math.sqrt(speed_sq)
           self.dx = (self.dx / speed) * effective_max_speed
           self.dy = (self.dy / speed) * effective_max_speed

        # Update position
        # The distance moved per frame is dx/dy, which are already scaled by simulation_speed_multiplier
        self.x += self.dx
        self.y += self.dy

        # Boundary check
        buffer = self.collision_radius + OUTLINE_WIDTH
        head_top_y = self.y + self.head_v_offset - self.head_radius

        # Reflect velocity AND clamp position if stuck
        if self.x - buffer < 0:
            self.x = buffer
            self.dx = abs(self.dx) * 0.9 # Dampen bounce slightly
        elif self.x + buffer > self.sim_width:
            self.x = self.sim_width - buffer
            self.dx = -abs(self.dx) * 0.9

        if head_top_y - buffer < 0:
             self.y = buffer - (self.head_v_offset - self.head_radius)
             self.dy = abs(self.dy) * 0.9
        elif (self.y + SHADOW_OFFSET + self.body_radius + buffer) > self.sim_height:
             self.y = self.sim_height - (SHADOW_OFFSET + self.body_radius) - buffer
             self.dy = -abs(self.dy) * 0.9

    def draw(self, screen):
        # Drawing code remains the same
        body_pos = (int(self.x), int(self.y))
        head_pos = (int(self.x), int(self.y + self.head_v_offset))
        shadow_pos = (int(self.x), int(self.y + SHADOW_OFFSET))

        pygame.draw.circle(screen, self.shadow_color, shadow_pos, self.body_radius)
        if OUTLINE_WIDTH > 0:
            pygame.draw.circle(screen, self.outline_color, body_pos, self.body_radius + OUTLINE_WIDTH)
            pygame.draw.circle(screen, self.outline_color, head_pos, self.head_radius + OUTLINE_WIDTH)
        pygame.draw.circle(screen, self.body_color, body_pos, self.body_radius)
        pygame.draw.circle(screen, self.head_color, head_pos, self.head_radius)


class Hole: # Unchanged
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = HOLE_RADIUS
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, screen):
        pygame.draw.circle(screen, HOLE_COLOR, (self.x, self.y), self.radius)


# Updated Building class for Hut appearance
class Building: # Renamed visually to Hut
    def __init__(self, center_x, center_y):
        self.width, self.base_height = HUT_BASE_SIZE
        self.roof_height = HUT_ROOF_HEIGHT
        self.total_height = self.base_height + self.roof_height
        # Collision rect remains the base
        self.rect = pygame.Rect(center_x - self.width // 2,
                                 center_y - self.base_height // 2, # Center the base vertically
                                 self.width, self.base_height)
        self.wall_color = HUT_WALL_COLOR
        self.roof_color = HUT_ROOF_COLOR
        self.thatch_color = HUT_THATCH_LINE_COLOR
        self.outline_color = HUT_OUTLINE_COLOR

    def draw(self, screen):
        # 1. Draw Base (Walls)
        base_rect = self.rect
        pygame.draw.rect(screen, self.wall_color, base_rect, border_radius=2)
        # Optional outline for base
        pygame.draw.rect(screen, self.outline_color, base_rect, width=OUTLINE_WIDTH, border_radius=2)

        # 2. Draw Roof (Triangle)
        roof_peak_y = base_rect.top - self.roof_height
        roof_points = [
            (base_rect.left - OUTLINE_WIDTH, base_rect.top), # Bottom-left corner (slight overhang)
            (base_rect.right + OUTLINE_WIDTH, base_rect.top),# Bottom-right corner (slight overhang)
            (base_rect.centerx, roof_peak_y)                # Peak
        ]
        pygame.draw.polygon(screen, self.roof_color, roof_points)

        # 3. Draw Thatch Lines on Roof
        num_thatch_lines = 5
        for i in range(1, num_thatch_lines + 1):
            lerp_factor = i / (num_thatch_lines + 1)
            # Interpolate points along the slopes
            left_y = base_rect.top - lerp_factor * self.roof_height
            right_y = left_y
            left_x = base_rect.left - OUTLINE_WIDTH + lerp_factor * (base_rect.width/2 + OUTLINE_WIDTH)
            right_x = base_rect.right + OUTLINE_WIDTH - lerp_factor * (base_rect.width/2 + OUTLINE_WIDTH)

            # Draw slightly curved or angled lines
            # Simple horizontal lines for now:
            line_y = base_rect.top - (lerp_factor * self.roof_height * 0.9) # Don't go quite to peak
            line_start_x = base_rect.left + (lerp_factor * self.width * 0.1)
            line_end_x = base_rect.right - (lerp_factor * self.width * 0.1)
            pygame.draw.line(screen, self.thatch_color, (line_start_x, line_y), (line_end_x, line_y), 2)


class Tree: # Unchanged
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.trunk_radius = TREE_TRUNK_WIDTH // 2
        self.collision_radius = self.trunk_radius
        self.canopy_radius = TREE_RADIUS
        self.canopy_color = TREE_CANOPY_COLOR
        self.trunk_color = TREE_TRUNK_COLOR
        self.collision_rect = pygame.Rect(x - self.collision_radius, y - self.collision_radius,
                                          self.collision_radius * 2, self.collision_radius * 2)

    def draw(self, screen):
        canopy_y = self.y - self.canopy_radius // 2
        pygame.draw.circle(screen, self.canopy_color, (self.x, canopy_y), self.canopy_radius)
        trunk_height = self.canopy_radius
        pygame.draw.line(screen, self.trunk_color, (self.x, self.y), (self.x, canopy_y), TREE_TRUNK_WIDTH)

class Hurricane: # Unchanged except duration/strength values if desired
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
            norm_x = dist_x / distance
            norm_y = dist_y / distance
            force_x = -norm_y * self.strength
            force_y = norm_x * self.strength
            force_x += norm_x * self.strength * 0.1
            force_y += norm_y * self.strength * 0.1
            meeple.apply_force(force_x, force_y)

    def draw(self, screen):
        surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, HURRICANE_VISUAL_COLOR, (self.radius, self.radius), self.radius)
        screen.blit(surface, (self.x - self.radius, self.y - self.radius))

# --- Global State ---
meeples = []
holes = []
buildings = [] # Will contain Hut objects now
trees = []
active_effects = []
is_raining = False
rain_end_time = 0
rain_drop_positions = []
selected_tool = None

# --- Helper Functions ---

def draw_toolbar(screen, selected_tool, speed_multiplier, meeple_count):
    # Toolbar Background
    pygame.draw.rect(screen, TOOLBAR_COLOR, (SIMULATION_WIDTH, 0, TOOLBAR_WIDTH, SCREEN_HEIGHT))

    # Draw Icons
    icon_y = ICON_PADDING
    for i, tool_name in enumerate(TOOLS):
        icon_rect = pygame.Rect(SIMULATION_WIDTH + ICON_PADDING, icon_y, ICON_SIZE, ICON_SIZE)

        if tool_name == selected_tool:
            pygame.draw.rect(screen, ICON_SELECTED_COLOR, icon_rect.inflate(4, 4), border_radius=5)

        icon_info = TOOL_ICONS[tool_name]
        icon_center = icon_rect.center

        # --- Draw Specific Icons ---
        pygame.draw.rect(screen, ICON_DEFAULT_COLOR, icon_rect, border_radius=5) # Icon background

        if icon_info["shape"] == "circle": # Hole
             pygame.draw.circle(screen, icon_info["color"], icon_center, ICON_SIZE // 2 - 4)
        elif icon_info["shape"] == "hut": # Building/Hut
             base_h = ICON_SIZE // 3
             roof_h = ICON_SIZE // 3
             wall_rect = pygame.Rect(icon_rect.left+10, icon_rect.bottom - 10 - base_h, icon_rect.width-20, base_h)
             pygame.draw.rect(screen, icon_info["color"], wall_rect)
             roof_points = [ (wall_rect.left, wall_rect.top), (wall_rect.right, wall_rect.top), (wall_rect.centerx, wall_rect.top-roof_h)]
             pygame.draw.polygon(screen, (139, 69, 19), roof_points)
        elif icon_info["shape"] == "swirl": # Hurricane
             pygame.draw.circle(screen, icon_info["color"], icon_center, ICON_SIZE // 2 - 4, 3)
             pygame.draw.circle(screen, icon_info["color"], icon_center, ICON_SIZE // 3 - 4, 3)
        elif icon_info["shape"] == "tree": # Tree
             pygame.draw.rect(screen, (100,60,20), (icon_center[0]-3, icon_center[1], 6, ICON_SIZE//2 - 4))
             pygame.draw.circle(screen, icon_info["color"], (icon_center[0], icon_center[1]-ICON_SIZE//4), ICON_SIZE // 3)
        elif icon_info["shape"] == "drops": # Rain
            for _ in range(3):
                rx = random.randint(icon_rect.left + 5, icon_rect.right - 5)
                ry = random.randint(icon_rect.top + 5, icon_rect.bottom - 10)
                pygame.draw.line(screen, icon_info["color"], (rx, ry), (rx, ry+5), 2)
        elif icon_info["shape"] == "meeple_plus": # Add Meeple
             # Draw a small meeple shape
             body_r = ICON_SIZE // 5
             head_r = int(body_r * HEAD_RADIUS_RATIO)
             pygame.draw.circle(screen, icon_info["color"], (icon_center[0], icon_center[1] + body_r//2), body_r)
             pygame.draw.circle(screen, MEEPLE_HEAD_COLOR, (icon_center[0], icon_center[1]-head_r), head_r )
             # Draw a plus sign
             pygame.draw.line(screen, (255,255,255), (icon_center[0] + body_r, icon_center[1]), (icon_center[0] + body_r+10, icon_center[1]), 2)
             pygame.draw.line(screen, (255,255,255), (icon_center[0] + body_r+5, icon_center[1]-5), (icon_center[0] + body_r+5, icon_center[1]+5), 2)

        icon_y += ICON_SIZE + ICON_PADDING

    # --- Draw Info Text ---
    y_offset = icon_y + 20 # Start below icons
    speed_text = info_font.render(f"Speed: {speed_multiplier:.1f}x", True, INFO_TEXT_COLOR)
    screen.blit(speed_text, (SIMULATION_WIDTH + ICON_PADDING, y_offset))
    y_offset += 25
    meeple_text = info_font.render(f"Meeples: {meeple_count}", True, INFO_TEXT_COLOR)
    screen.blit(meeple_text, (SIMULATION_WIDTH + ICON_PADDING, y_offset))
    y_offset += 25
    controls_text1 = info_font.render("'+'/'-': Speed", True, INFO_TEXT_COLOR)
    screen.blit(controls_text1, (SIMULATION_WIDTH + ICON_PADDING, y_offset))


def handle_collisions(meeples, buildings, trees): # Mostly unchanged logic
    meeples_to_remove = []

    # Meeple-Meeple
    for i in range(len(meeples)):
        if meeples[i] in meeples_to_remove: continue
        for j in range(i + 1, len(meeples)):
            if meeples[j] in meeples_to_remove: continue
            m1 = meeples[i]; m2 = meeples[j]
            dist_x = m1.x - m2.x; dist_y = m1.y - m2.y
            dist_sq = dist_x**2 + dist_y**2
            min_dist = m1.collision_radius + m2.collision_radius
            min_dist_sq = min_dist**2
            if dist_sq < min_dist_sq and dist_sq > 0.001:
                distance = math.sqrt(dist_sq)
                overlap = max(0, (min_dist - distance + (OUTLINE_WIDTH * 1)) / 2.0)
                push_x = dist_x / distance; push_y = dist_y / distance
                m1.x += push_x * overlap * COLLISION_PUSH_FORCE; m1.y += push_y * overlap * COLLISION_PUSH_FORCE
                m2.x -= push_x * overlap * COLLISION_PUSH_FORCE; m2.y -= push_y * overlap * COLLISION_PUSH_FORCE

    # Meeple-Obstacle
    obstacles = buildings + trees
    for meeple in meeples:
        if meeple in meeples_to_remove: continue
        meeple_rect = pygame.Rect(meeple.x - meeple.collision_radius, meeple.y - meeple.collision_radius, meeple.collision_radius * 2, meeple.collision_radius * 2)
        for obstacle in obstacles:
            obstacle_col_rect = obstacle.rect if isinstance(obstacle, Building) else obstacle.collision_rect
            if meeple_rect.colliderect(obstacle_col_rect):
                center_x_obs, center_y_obs = obstacle_col_rect.center
                dist_x = meeple.x - center_x_obs; dist_y = meeple.y - center_y_obs
                dist = math.hypot(dist_x, dist_y)
                if dist < 0.01: dist = 0.01; dist_x = 0.01
                push_x = dist_x / dist; push_y = dist_y / dist
                meeple.x += push_x * OBSTACLE_PUSH_FORCE; meeple.y += push_y * OBSTACLE_PUSH_FORCE
                # Dampen velocity component towards obstacle
                dot_product = meeple.dx * push_x + meeple.dy * push_y
                if dot_product < 0:
                    meeple.dx -= dot_product * push_x * 0.5
                    meeple.dy -= dot_product * push_y * 0.5

    # Meeple-Hole Removal
    for hole in holes:
        for meeple in meeples:
            if meeple in meeples_to_remove: continue
            dist_x = meeple.x - hole.x; dist_y = meeple.y - hole.y
            dist_sq = dist_x**2 + dist_y**2
            if dist_sq < (hole.radius * 0.8)**2:
                if meeple not in meeples_to_remove:
                    meeples_to_remove.append(meeple)

    # Perform removal
    if meeples_to_remove:
        meeples[:] = [m for m in meeples if m not in meeples_to_remove]

def initialize_rain_drops():
    global rain_drop_positions
    rain_drop_positions = []
    for _ in range(NUM_RAIN_DROPS):
        x = random.randint(0, SIMULATION_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        rain_drop_positions.append([x, y])

def update_and_draw_rain(screen):
    global rain_drop_positions
    if not is_raining: return

    # Scale drop speed with simulation speed
    drop_speed = RAIN_DROP_BASE_SPEED * simulation_speed_multiplier

    for i in range(len(rain_drop_positions)):
        rain_drop_positions[i][1] += drop_speed
        if rain_drop_positions[i][1] > SCREEN_HEIGHT:
            rain_drop_positions[i][0] = random.randint(0, SIMULATION_WIDTH)
            rain_drop_positions[i][1] = random.randint(-20, -5)

        start_pos = (rain_drop_positions[i][0], rain_drop_positions[i][1])
        end_pos = (rain_drop_positions[i][0], rain_drop_positions[i][1] + RAIN_DROP_LENGTH)
        pygame.draw.line(screen, RAIN_DROP_COLOR, start_pos, end_pos, 1)


# --- Create Initial Meeples ---
center_x = SIMULATION_WIDTH // 2
center_y = SCREEN_HEIGHT // 2
spawn_radius = 70

for _ in range(INITIAL_NUM_MEEPLES): # Use initial count
    # Reuse the non-overlapping placement logic
    placed = False
    attempts = 0
    while not placed and attempts < 100:
        angle = random.uniform(0, 2 * math.pi); radius_offset = random.uniform(0, spawn_radius)
        x = center_x + math.cos(angle) * radius_offset; y = center_y + math.sin(angle) * radius_offset
        buffer = BODY_RADIUS + OUTLINE_WIDTH
        head_top_y_approx = y - int(BODY_RADIUS * HEAD_V_OFFSET_RATIO) - int(BODY_RADIUS * HEAD_RADIUS_RATIO)
        if x - buffer < 0 or x + buffer > SIMULATION_WIDTH or \
           y + SHADOW_OFFSET + BODY_RADIUS + buffer > SCREEN_HEIGHT or head_top_y_approx - buffer < 0:
            attempts += 1; continue

        # Pass sim boundaries to meeple constructor
        new_meeple = Meeple(x, y, SIMULATION_WIDTH, SCREEN_HEIGHT)

        overlapping = False
        for existing in meeples + buildings + trees: # Check against all existing things
             if isinstance(existing, Meeple):
                dist_x = new_meeple.x - existing.x; dist_y = new_meeple.y - existing.y
                dist_sq = dist_x**2 + dist_y**2
                min_dist_sq = (new_meeple.collision_radius + existing.collision_radius)**2
                if dist_sq < min_dist_sq: overlapping = True; break
             elif isinstance(existing, Building): # Check against building base rect
                 obstacle_rect = existing.rect
                 # Simple point in rect check for spawn center is usually enough
                 if obstacle_rect.collidepoint(new_meeple.x, new_meeple.y): overlapping = True; break
             elif isinstance(existing, Tree): # Check against tree trunk rect
                  obstacle_rect = existing.collision_rect
                  if obstacle_rect.collidepoint(new_meeple.x, new_meeple.y): overlapping = True; break

        if not overlapping:
            meeples.append(new_meeple); placed = True
        attempts += 1


# --- Game Loop ---
running = True
while running:
    current_time = time.time()
    # Calculate dt (delta time) - useful if needing frame-rate independent physics,
    # but here we scale speeds directly based on multiplier. Still good practice.
    dt = clock.tick(60) / 1000.0 # Time since last frame in seconds

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # --- Speed Control Input ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                simulation_speed_multiplier += SPEED_CHANGE_STEP
            elif event.key == pygame.K_MINUS:
                simulation_speed_multiplier -= SPEED_CHANGE_STEP
            # Clamp speed multiplier
            simulation_speed_multiplier = max(MIN_SPEED_MULT, min(simulation_speed_multiplier, MAX_SPEED_MULT))
            print(f"Simulation Speed: {simulation_speed_multiplier:.2f}x") # Feedback

        # --- Tool Interaction Input ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Toolbar Click
            if mouse_x >= SIMULATION_WIDTH:
                icon_y = ICON_PADDING
                for tool_name in TOOLS:
                    icon_rect = pygame.Rect(SIMULATION_WIDTH + ICON_PADDING, icon_y, ICON_SIZE, ICON_SIZE)
                    if icon_rect.collidepoint(mouse_x, mouse_y):
                        selected_tool = tool_name if selected_tool != tool_name else None
                        break
                    icon_y += ICON_SIZE + ICON_PADDING
            # Simulation Area Click
            elif selected_tool is not None and mouse_x < SIMULATION_WIDTH : # Ensure click is in sim area
                if selected_tool == "hole":
                    holes.append(Hole(mouse_x, mouse_y))
                elif selected_tool == "building":
                     # Check if placement overlaps existing buildings/trees significantly
                     new_hut_rect = pygame.Rect(mouse_x - HUT_BASE_SIZE[0]//2, mouse_y - HUT_BASE_SIZE[1]//2, HUT_BASE_SIZE[0], HUT_BASE_SIZE[1])
                     can_place = True
                     for obs in buildings + trees:
                          if new_hut_rect.colliderect(obs.rect if isinstance(obs, Building) else obs.collision_rect):
                              print("Cannot place hut: overlaps existing object.")
                              can_place = False
                              break
                     if can_place:
                         buildings.append(Building(mouse_x, mouse_y))

                elif selected_tool == "tree":
                    new_tree_rect = pygame.Rect(mouse_x - TREE_TRUNK_WIDTH//2, mouse_y - TREE_TRUNK_WIDTH//2, TREE_TRUNK_WIDTH, TREE_TRUNK_WIDTH)
                    can_place = True
                    for obs in buildings + trees:
                         if new_tree_rect.colliderect(obs.rect if isinstance(obs, Building) else obs.collision_rect):
                             print("Cannot place tree: overlaps existing object.")
                             can_place = False
                             break
                    if can_place:
                         trees.append(Tree(mouse_x, mouse_y))

                elif selected_tool == "hurricane":
                    active_effects = [e for e in active_effects if not isinstance(e, Hurricane)]
                    active_effects.append(Hurricane(mouse_x, mouse_y))
                elif selected_tool == "rain":
                    if not is_raining:
                        is_raining = True; rain_end_time = current_time + RAIN_DURATION
                        initialize_rain_drops()
                    else: is_raining = False # Toggle off
                elif selected_tool == "add_meeple":
                     # Add basic check to prevent adding inside obstacles
                     can_place = True
                     temp_meeple_rect = pygame.Rect(mouse_x-BODY_RADIUS, mouse_y-BODY_RADIUS, BODY_RADIUS*2, BODY_RADIUS*2)
                     for obs in buildings + trees:
                          if temp_meeple_rect.colliderect(obs.rect if isinstance(obs, Building) else obs.collision_rect):
                              print("Cannot place meeple inside obstacle.")
                              can_place = False
                              break
                     if can_place:
                         meeples.append(Meeple(mouse_x, mouse_y, SIMULATION_WIDTH, SCREEN_HEIGHT))

                # Deselect tool after use? (Optional)
                # selected_tool = None

    # --- Update Phase ---
    # Update timed effects
    if is_raining and current_time > rain_end_time: is_raining = False
    active_effects = [e for e in active_effects if e.is_active()]

    # Update Meeples (apply forces, wander, move)
    current_speed_mod_rain = RAIN_SPEED_MULTIPLIER if is_raining else 1.0
    for meeple in meeples:
        meeple.speed_multiplier = current_speed_mod_rain
        for effect in active_effects:
            if hasattr(effect, 'apply_effect'): effect.apply_effect(meeple)
        meeple.wander() # Includes speed calculation now
        meeple.move() # Includes applying forces and boundary checks

    # --- Collision Handling ---
    # Run multiple collision passes for stability, especially at higher speeds
    num_collision_passes = max(1, int(simulation_speed_multiplier)) # More passes if faster?
    for _ in range(num_collision_passes):
        handle_collisions(meeples, buildings, trees) # Includes hole removal

    # --- Drawing Phase ---
    screen.fill(FIELD_COLOR)

    # Environment objects (sorted by Y where relevant)
    for hole in holes: hole.draw(screen)
    # Draw buildings and trees together, sorted by the bottom of their base/trunk for correct overlap
    environment_objects = sorted(buildings + trees, key=lambda obj: obj.rect.bottom if isinstance(obj, Building) else obj.y)
    for obj in environment_objects:
        obj.draw(screen)

    # Meeples (sorted by Y)
    meeples_sorted = sorted(meeples, key=lambda m: m.y)
    for meeple in meeples_sorted: meeple.draw(screen)

    # Effects visuals
    for effect in active_effects:
        if hasattr(effect, 'draw'): effect.draw(screen)

    # Rain
    update_and_draw_rain(screen) # Handles drawing if raining

    # Toolbar
    draw_toolbar(screen, selected_tool, simulation_speed_multiplier, len(meeples))

    # Update Display
    pygame.display.flip()

# --- Cleanup ---
pygame.quit()
