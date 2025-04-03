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
ICON_SIZE = 50 # Smaller icons to fit more
ICON_PADDING = 8
ICON_SELECTED_COLOR = (255, 255, 0)
ICON_DEFAULT_COLOR = (150, 150, 150)
INFO_TEXT_COLOR = (240, 240, 240)

# Initial Meeple Count
INITIAL_NUM_MEEPLES = 20 # Start with fewer for performance testing cycle

# Meeple Appearance
BODY_RADIUS = 8 # Slightly smaller
HEAD_RADIUS_RATIO = 0.6
HEAD_V_OFFSET_RATIO = 0.8
MEEPLE_BODY_COLOR = (200, 50, 50)
MEEPLE_HEAD_COLOR = (220, 70, 70)
MEEPLE_SHADOW_COLOR = (30, 80, 30)
OUTLINE_COLOR = (20, 20, 20)
OUTLINE_WIDTH = 1
SHADOW_OFFSET = 2

# Simulation Parameters
MEEPLE_BASE_SPEED = 50.0 # Pixels per second (adjust based on dt)
WANDER_STRENGTH = 1.5 # Radians per second change
COLLISION_PUSH_FORCE = 1.0 # Adjusted for dt? Let's try direct push first.
OBSTACLE_PUSH_FORCE = 1.5
HOME_PROXIMITY_THRESHOLD = 15 # How close to home counts as "at home"

# --- Speed Control ---
simulation_speed_multiplier = 1.0
SPEED_CHANGE_STEP = 0.2
MIN_SPEED_MULT = 0.2
MAX_SPEED_MULT = 5.0

# --- Day/Night Cycle ---
DAY_DURATION_SECONDS = 30 # Shorter cycle for testing
NIGHT_DURATION_SECONDS = 20
FULL_CYCLE_SECONDS = DAY_DURATION_SECONDS + NIGHT_DURATION_SECONDS
cycle_timer = 0.0
is_daytime = True

# Tool Specific Constants
HOLE_RADIUS = 30; HOLE_COLOR = (0, 0, 0)

# Hut Appearance & Settings
HUT_BASE_SIZE = (50, 30)
HUT_ROOF_HEIGHT = 30
HUT_WALL_COLOR = (180, 140, 100)
HUT_WALL_SHADE_COLOR = (150, 110, 80) # Darker wall color
HUT_ROOF_COLOR = (139, 69, 19)
HUT_ROOF_SHADE_COLOR = (100, 50, 10) # Darker roof color
HUT_THATCH_LINE_COLOR = (80, 40, 10)
HUT_OUTLINE_COLOR = (40, 40, 20)
HUT_MAX_RESIDENTS = 4

# Farm Appearance
FARM_SIZE = (100, 70)
FARM_FIELD_COLOR = (100, 180, 100) # Lighter green
FARM_BORDER_COLOR = (101, 67, 33) # Brown border
FARM_BORDER_WIDTH = 4

# Factory Appearance
FACTORY_BASE_SIZE = (70, 50)
FACTORY_COLOR = (130, 130, 130) # Grey
FACTORY_ROOF_COLOR = (100, 100, 100) # Darker Grey Roof
FACTORY_CHIMNEY_SIZE = (8, 30)
FACTORY_CHIMNEY_COLOR = (70, 70, 70)
FACTORY_OUTLINE_COLOR = (50, 50, 50)

# Tree Settings (as before)
TREE_RADIUS = 15; TREE_CANOPY_COLOR=(30,100,30); TREE_TRUNK_COLOR=(100,60,20); TREE_TRUNK_WIDTH=6

# Hurricane Settings (as before)
HURRICANE_RADIUS = 100; HURRICANE_STRENGTH = 80.0 # Force units (adjust w/ dt)
HURRICANE_DURATION = 8; HURRICANE_VISUAL_COLOR = (150,150,200,100)

# Rain Settings (as before)
RAIN_DURATION = 10; RAIN_SPEED_MULTIPLIER = 0.6; RAIN_DROP_COLOR=(100,100,200)
RAIN_DROP_LENGTH = 5; NUM_RAIN_DROPS = 200; RAIN_DROP_BASE_SPEED = 200 # pixels/sec

# --- Tool Definitions ---
TOOLS = ["hole", "hut", "farm", "factory", "hurricane", "tree", "rain", "add_meeple"]
TOOL_ICONS = {
    "hole": {"color": (10, 10, 10), "shape": "circle"},
    "hut": {"color": HUT_WALL_COLOR, "shape": "hut"},
    "farm": {"color": FARM_FIELD_COLOR, "shape": "rect"},
    "factory": {"color": FACTORY_COLOR, "shape": "rect_chimney"},
    "hurricane": {"color": (100, 100, 180), "shape": "swirl"},
    "tree": {"color": (40, 110, 40), "shape": "tree"},
    "rain": {"color": (80, 80, 150), "shape": "drops"},
    "add_meeple": {"color": MEEPLE_BODY_COLOR, "shape": "meeple_plus"}
}

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Meeple Sim - Cycles & Buildings")
clock = pygame.time.Clock()
info_font = pygame.font.SysFont(None, 22) # Smaller font

# --- Base Class for Placeable Objects ---
class Placeable:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        # Define collision_rect and draw_rect in subclasses
        self.collision_rect = None
        self.draw_rect = None # Used for sorting drawing order

    def draw(self, screen):
        raise NotImplementedError

# --- Classes ---

class Meeple:
    def __init__(self, x, y, sim_width, sim_height):
        self.x = float(x)
        self.y = float(y)
        self.body_radius = BODY_RADIUS
        self.head_radius = int(self.body_radius * HEAD_RADIUS_RATIO)
        self.head_v_offset = -int(self.body_radius * HEAD_V_OFFSET_RATIO)
        self.collision_radius = self.body_radius
        self.sim_width = sim_width
        self.sim_height = sim_height

        self.speed_multiplier_effect = 1.0 # For rain etc.
        self.angle = random.uniform(0, 2 * math.pi) # Current direction
        self.dx = 0.0
        self.dy = 0.0

        # --- New Attributes ---
        self.home = None # Reference to assigned Hut object
        self.state = "wandering" # "wandering", "going_home", "at_home"
        self.target_pos = None # Target position (e.g., home location)

        # Appearance
        self.body_color = MEEPLE_BODY_COLOR; self.head_color = MEEPLE_HEAD_COLOR
        self.shadow_color = MEEPLE_SHADOW_COLOR; self.outline_color = OUTLINE_COLOR
        self.force_x = 0.0; self.force_y = 0.0 # External forces (hurricane)

    def assign_home(self, home_building):
        if isinstance(home_building, Hut) and len(home_building.residents) < home_building.max_residents:
             self.home = home_building
             home_building.residents.append(self)
             # print(f"Assigned meeple to home at {home_building.rect.center}")
             return True
        return False

    def apply_force(self, fx, fy):
        self.force_x += fx
        self.force_y += fy

    def update(self, dt, is_daytime):
        """Handles state transitions and movement calculations based on dt."""
        # --- State Logic ---
        if self.home:
            dist_to_home_sq = (self.x - self.home.rect.centerx)**2 + (self.y - self.home.rect.centery)**2
            is_near_home = dist_to_home_sq < HOME_PROXIMITY_THRESHOLD**2

            if is_daytime:
                if self.state == "at_home":
                    self.state = "wandering"
                    self.target_pos = None
                    # print("Meeple leaving home")
            else: # Nighttime
                if self.state == "wandering":
                    self.state = "going_home"
                    self.target_pos = self.home.rect.center
                    # print("Meeple going home")

            if self.state == "going_home" and is_near_home:
                self.state = "at_home"
                self.target_pos = None
                # Snap to a position near home? Or just stop?
                self.x, self.y = self.home.get_random_spot_nearby() # Jitter position near home
                # print("Meeple arrived home")

        # --- Movement Logic ---
        current_base_speed = MEEPLE_BASE_SPEED * self.speed_multiplier_effect
        effective_speed = current_base_speed * simulation_speed_multiplier

        if self.state == "at_home":
            self.dx = 0
            self.dy = 0
        elif self.state == "going_home" and self.target_pos:
            # Move towards target
            target_dx = self.target_pos[0] - self.x
            target_dy = self.target_pos[1] - self.y
            dist_to_target = math.hypot(target_dx, target_dy)

            if dist_to_target > 1.0: # Avoid division by zero and jittering at target
                self.angle = math.atan2(target_dy, target_dx)
                self.dx = math.cos(self.angle) * effective_speed
                self.dy = math.sin(self.angle) * effective_speed
            else:
                self.dx = 0; self.dy = 0 # Reached target (or very close)
        else: # Wandering state
            # Apply wander steer behavior (change angle gradually)
            angle_change = random.uniform(-WANDER_STRENGTH, WANDER_STRENGTH) * dt * simulation_speed_multiplier
            self.angle += angle_change
            # Recalculate dx/dy based on new angle and current speed
            self.dx = math.cos(self.angle) * effective_speed
            self.dy = math.sin(self.angle) * effective_speed

        # Apply external forces (scaled by dt? Force is impulse N*s or constant N?)
        # Let's treat force as constant acceleration: a = F/m (assume m=1)
        # dv = a * dt => dv = F * dt
        self.dx += self.force_x * dt * simulation_speed_multiplier
        self.dy += self.force_y * dt * simulation_speed_multiplier
        self.force_x = 0.0 # Reset force for next frame
        self.force_y = 0.0

        # Speed limit check (optional) - check total speed per second
        # current_speed_sq = (self.dx/dt)**2 + (self.dy/dt)**2 # Speed per second squared
        # max_allowed_speed = MEEPLE_BASE_SPEED * simulation_speed_multiplier * self.speed_multiplier_effect * 1.5
        # if current_speed_sq > max_allowed_speed**2:
        #    actual_speed = math.sqrt(current_speed_sq)
        #    scale = max_allowed_speed / actual_speed
        #    self.dx *= scale
        #    self.dy *= scale


        # Update position using calculated velocity for this frame
        self.x += self.dx * dt
        self.y += self.dy * dt

        # --- Boundary Check ---
        buffer = self.collision_radius + OUTLINE_WIDTH
        head_top_y = self.y + self.head_v_offset - self.head_radius
        bounce_damp = 0.5 # Reduce speed on bounce

        if self.x - buffer < 0:
            self.x = buffer
            self.dx = abs(self.dx * bounce_damp)
            self.angle = math.atan2(self.dy, self.dx) # Update angle after bounce
        elif self.x + buffer > self.sim_width:
            self.x = self.sim_width - buffer
            self.dx = -abs(self.dx * bounce_damp)
            self.angle = math.atan2(self.dy, self.dx)

        if head_top_y - buffer < 0:
             self.y = buffer - (self.head_v_offset - self.head_radius)
             self.dy = abs(self.dy * bounce_damp)
             self.angle = math.atan2(self.dy, self.dx)
        elif (self.y + SHADOW_OFFSET + self.body_radius + buffer) > self.sim_height:
             self.y = self.sim_height - (SHADOW_OFFSET + self.body_radius) - buffer
             self.dy = -abs(self.dy * bounce_damp)
             self.angle = math.atan2(self.dy, self.dx)


    def draw(self, screen):
        if self.state == "at_home" and self.home: # Optional: Hide meeples at home
             # Maybe draw them semi-transparent or smaller?
             # Or just draw them normally where they stopped.
             pass # Draw normally for now

        body_pos = (int(self.x), int(self.y))
        head_pos = (int(self.x), int(self.y + self.head_v_offset))
        shadow_pos = (int(self.x), int(self.y + SHADOW_OFFSET))

        pygame.draw.circle(screen, self.shadow_color, shadow_pos, self.body_radius)
        if OUTLINE_WIDTH > 0:
            pygame.draw.circle(screen, self.outline_color, body_pos, self.body_radius + OUTLINE_WIDTH)
            pygame.draw.circle(screen, self.outline_color, head_pos, self.head_radius + OUTLINE_WIDTH)
        pygame.draw.circle(screen, self.body_color, body_pos, self.body_radius)
        pygame.draw.circle(screen, self.head_color, head_pos, self.head_radius)


class Hole(Placeable): # Inherits from Placeable
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = HOLE_RADIUS
        self.color = HOLE_COLOR
        # Collision rect is centered
        self.collision_rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        self.draw_rect = self.collision_rect # For sorting

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

class Hut(Placeable): # Was Building
    def __init__(self, center_x, center_y):
        super().__init__(center_x, center_y)
        self.type = "hut"
        self.width, self.base_height = HUT_BASE_SIZE
        self.roof_height = HUT_ROOF_HEIGHT
        # Base rectangle used for resident targeting and main collision logic origin
        self.rect = pygame.Rect(center_x - self.width // 2,
                                 center_y - self.base_height // 2,
                                 self.width, self.base_height)
        # Full bounding box for collision detection (includes roof)
        self.collision_rect = pygame.Rect(self.rect.left,
                                           self.rect.top - self.roof_height,
                                           self.width,
                                           self.base_height + self.roof_height)
        self.draw_rect = self.rect # Sort based on base

        # Appearance colors
        self.wall_color = HUT_WALL_COLOR; self.wall_shade_color = HUT_WALL_SHADE_COLOR
        self.roof_color = HUT_ROOF_COLOR; self.roof_shade_color = HUT_ROOF_SHADE_COLOR
        self.thatch_color = HUT_THATCH_LINE_COLOR; self.outline_color = HUT_OUTLINE_COLOR

        # --- Home Functionality ---
        self.residents = []
        self.max_residents = HUT_MAX_RESIDENTS

    def get_random_spot_nearby(self):
        """Returns a random (x, y) near the center for 'at_home' state."""
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, self.width * 0.3) # Within base area roughly
        return (self.rect.centerx + math.cos(angle) * radius,
                self.rect.centery + math.sin(angle) * radius)

    def draw(self, screen):
        # --- Draw Base with Shading ---
        base_rect = self.rect
        pygame.draw.rect(screen, self.wall_color, base_rect, border_radius=2)
        # Shade (e.g., left side)
        shade_rect = pygame.Rect(base_rect.left, base_rect.top, base_rect.width // 3, base_rect.height)
        pygame.draw.rect(screen, self.wall_shade_color, shade_rect, border_top_left_radius=2, border_bottom_left_radius=2)
        # Outline
        pygame.draw.rect(screen, self.outline_color, base_rect, width=OUTLINE_WIDTH, border_radius=2)

        # --- Draw Roof with Shading ---
        roof_peak_y = base_rect.top - self.roof_height
        roof_points = [ (base_rect.left - OUTLINE_WIDTH, base_rect.top),
                        (base_rect.right + OUTLINE_WIDTH, base_rect.top),
                        (base_rect.centerx, roof_peak_y) ]
        pygame.draw.polygon(screen, self.roof_color, roof_points)

        # Roof Shade (e.g., left side)
        shade_roof_points = [ (base_rect.left - OUTLINE_WIDTH, base_rect.top),
                              (base_rect.centerx, base_rect.top), # Midpoint base
                              (base_rect.centerx, roof_peak_y) ]  # Peak
        pygame.draw.polygon(screen, self.roof_shade_color, shade_roof_points)

        # --- Thatch Lines ---
        num_thatch_lines = 4
        for i in range(1, num_thatch_lines + 1):
            lerp_factor = i / (num_thatch_lines + 1)
            line_y = base_rect.top - (lerp_factor * self.roof_height * 0.9)
            line_start_x = base_rect.left + (lerp_factor * self.width * 0.1)
            line_end_x = base_rect.right - (lerp_factor * self.width * 0.1)
            pygame.draw.line(screen, self.thatch_color, (line_start_x, line_y), (line_end_x, line_y), 2)

class Farm(Placeable):
     def __init__(self, center_x, center_y):
        super().__init__(center_x, center_y)
        self.type = "farm"
        self.width, self.height = FARM_SIZE
        self.rect = pygame.Rect(center_x - self.width // 2,
                                 center_y - self.height // 2,
                                 self.width, self.height)
        self.collision_rect = self.rect
        self.draw_rect = self.rect # Sort based on full rect
        self.field_color = FARM_FIELD_COLOR
        self.border_color = FARM_BORDER_COLOR

     def draw(self, screen):
        pygame.draw.rect(screen, self.field_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, width=FARM_BORDER_WIDTH)

class Factory(Placeable):
    def __init__(self, center_x, center_y):
        super().__init__(center_x, center_y)
        self.type = "factory"
        self.width, self.height = FACTORY_BASE_SIZE
        self.rect = pygame.Rect(center_x - self.width // 2,
                                 center_y - self.height // 2,
                                 self.width, self.height)
        self.collision_rect = self.rect
        self.draw_rect = self.rect
        self.base_color = FACTORY_COLOR
        self.roof_color = FACTORY_ROOF_COLOR
        self.chimney_color = FACTORY_CHIMNEY_COLOR
        self.outline_color = FACTORY_OUTLINE_COLOR

        # Chimney position (relative to top-right corner)
        self.chimney_w, self.chimney_h = FACTORY_CHIMNEY_SIZE
        self.chimney_rect = pygame.Rect(self.rect.right - self.chimney_w - 5, # Offset from corner
                                        self.rect.top - self.chimney_h,
                                        self.chimney_w, self.chimney_h)
        # Make collision rect encompass chimney too
        self.collision_rect = self.rect.union(self.chimney_rect)


    def draw(self, screen):
        # Base
        pygame.draw.rect(screen, self.base_color, self.rect)
        # Simple flat roof part
        roof_rect = pygame.Rect(self.rect.left, self.rect.top, self.rect.width, 5)
        pygame.draw.rect(screen, self.roof_color, roof_rect)
        # Outline base
        pygame.draw.rect(screen, self.outline_color, self.rect, width=OUTLINE_WIDTH)
        # Chimney
        pygame.draw.rect(screen, self.chimney_color, self.chimney_rect)
        pygame.draw.rect(screen, self.outline_color, self.chimney_rect, width=OUTLINE_WIDTH)


class Tree(Placeable): # Mostly unchanged, inherits Placeable
    def __init__(self, x, y):
        super().__init__(x, y) # x, y is base of trunk
        self.type = "tree"
        self.trunk_radius = TREE_TRUNK_WIDTH // 2
        self.collision_radius = self.trunk_radius # Collision only with trunk base
        self.canopy_radius = TREE_RADIUS
        self.canopy_color = TREE_CANOPY_COLOR
        self.trunk_color = TREE_TRUNK_COLOR
        # Collision rect centered on the trunk base
        self.collision_rect = pygame.Rect(x - self.collision_radius, y - self.collision_radius,
                                          self.collision_radius * 2, self.collision_radius * 2)
        # Define draw_rect based on trunk base Y for sorting
        self.draw_rect = pygame.Rect(x - self.trunk_radius, y - self.trunk_radius, TREE_TRUNK_WIDTH, TREE_TRUNK_WIDTH)

    def draw(self, screen):
        canopy_y = self.y - self.canopy_radius // 2
        pygame.draw.circle(screen, self.canopy_color, (self.x, canopy_y), self.canopy_radius)
        trunk_height = self.canopy_radius
        pygame.draw.line(screen, self.trunk_color, (self.x, self.y), (self.x, canopy_y), TREE_TRUNK_WIDTH)


class Hurricane: # No changes needed for dt here, force applied over time
    def __init__(self, x, y):
        self.x = x; self.y = y; self.radius = HURRICANE_RADIUS
        self.strength = HURRICANE_STRENGTH # Force magnitude
        self.end_time = time.time() + HURRICANE_DURATION
        self.max_radius_sq = self.radius * self.radius

    def is_active(self): return time.time() < self.end_time

    def apply_effect(self, meeple):
        dist_x = meeple.x - self.x; dist_y = meeple.y - self.y
        dist_sq = dist_x**2 + dist_y**2
        if dist_sq < self.max_radius_sq and dist_sq > 0.01:
            distance = math.sqrt(dist_sq)
            norm_x = dist_x / distance; norm_y = dist_y / distance
            # Force is perpendicular (-ny, nx) + outward (nx, ny)
            force_x = -norm_y * self.strength + norm_x * self.strength * 0.1
            force_y = norm_x * self.strength + norm_y * self.strength * 0.1
            meeple.apply_force(force_x, force_y) # Force applied (will be mult by dt in Meeple update)

    def draw(self, screen):
        surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, HURRICANE_VISUAL_COLOR, (self.radius, self.radius), self.radius)
        screen.blit(surface, (self.x - self.radius, self.y - self.radius))

# --- Global State ---
meeples = []
placeables = [] # Single list for Huts, Farms, Factories, Trees, Holes
active_effects = []
is_raining = False
rain_end_time = 0
rain_drop_positions = []
selected_tool = None

# --- Helper Functions ---

def draw_toolbar(screen, selected_tool, speed_multiplier, meeple_count, cycle_info):
    pygame.draw.rect(screen, TOOLBAR_COLOR, (SIMULATION_WIDTH, 0, TOOLBAR_WIDTH, SCREEN_HEIGHT))
    icon_y = ICON_PADDING
    for i, tool_name in enumerate(TOOLS):
        icon_rect = pygame.Rect(SIMULATION_WIDTH + ICON_PADDING, icon_y, ICON_SIZE, ICON_SIZE)
        if tool_name == selected_tool:
            pygame.draw.rect(screen, ICON_SELECTED_COLOR, icon_rect.inflate(4, 4), border_radius=5)

        icon_info = TOOL_ICONS[tool_name]
        icon_center = icon_rect.center
        pygame.draw.rect(screen, ICON_DEFAULT_COLOR, icon_rect, border_radius=5) # Icon background

        # Simple Icons (Adjust visuals as needed)
        if icon_info["shape"] == "circle": # Hole
            pygame.draw.circle(screen, icon_info["color"], icon_center, ICON_SIZE // 2 - 4)
        elif icon_info["shape"] == "hut": # Hut
            base_h = ICON_SIZE // 3; roof_h = ICON_SIZE // 3
            wall_rect = pygame.Rect(icon_rect.left+10, icon_rect.bottom-10-base_h, icon_rect.width-20, base_h)
            pygame.draw.rect(screen, icon_info["color"], wall_rect)
            roof_pts = [(wall_rect.left, wall_rect.top), (wall_rect.right, wall_rect.top), (wall_rect.centerx, wall_rect.top-roof_h)]
            pygame.draw.polygon(screen, HUT_ROOF_COLOR, roof_pts)
        elif icon_info["shape"] == "rect": # Farm
            pygame.draw.rect(screen, icon_info["color"], icon_rect.inflate(-8, -8))
            pygame.draw.rect(screen, FARM_BORDER_COLOR, icon_rect.inflate(-8, -8), width=2)
        elif icon_info["shape"] == "rect_chimney": # Factory
            pygame.draw.rect(screen, icon_info["color"], icon_rect.inflate(-12, -12))
            chimney = pygame.Rect(icon_rect.right-15, icon_rect.top+5, 5, ICON_SIZE//2)
            pygame.draw.rect(screen, FACTORY_CHIMNEY_COLOR, chimney)
        elif icon_info["shape"] == "swirl": # Hurricane
            pygame.draw.circle(screen, icon_info["color"], icon_center, ICON_SIZE // 2 - 4, 3)
            pygame.draw.circle(screen, icon_info["color"], icon_center, ICON_SIZE // 3 - 4, 3)
        elif icon_info["shape"] == "tree":
             pygame.draw.rect(screen, TREE_TRUNK_COLOR, (icon_center[0]-3, icon_center[1], 6, ICON_SIZE//2 - 4))
             pygame.draw.circle(screen, icon_info["color"], (icon_center[0], icon_center[1]-ICON_SIZE//4), ICON_SIZE // 3)
        elif icon_info["shape"] == "drops":
            for _ in range(3):
                rx, ry = random.randint(icon_rect.left+5, icon_rect.right-5), random.randint(icon_rect.top+5, icon_rect.bottom-10)
                pygame.draw.line(screen, icon_info["color"], (rx, ry), (rx, ry+5), 2)
        elif icon_info["shape"] == "meeple_plus":
             body_r = ICON_SIZE // 5; head_r = int(body_r * HEAD_RADIUS_RATIO)
             pygame.draw.circle(screen, icon_info["color"], (icon_center[0], icon_center[1]+body_r//2), body_r)
             pygame.draw.circle(screen, MEEPLE_HEAD_COLOR, (icon_center[0], icon_center[1]-head_r), head_r )
             pygame.draw.line(screen, (255,255,255), (icon_center[0]+body_r, icon_center[1]), (icon_center[0]+body_r+10, icon_center[1]), 2)
             pygame.draw.line(screen, (255,255,255), (icon_center[0]+body_r+5, icon_center[1]-5), (icon_center[0]+body_r+5, icon_center[1]+5), 2)

        icon_y += ICON_SIZE + ICON_PADDING

    # Info Text
    y_offset = icon_y + 15
    speed_text = info_font.render(f"Speed: {speed_multiplier:.1f}x", True, INFO_TEXT_COLOR)
    screen.blit(speed_text, (SIMULATION_WIDTH + ICON_PADDING, y_offset)); y_offset += 20
    meeple_text = info_font.render(f"Meeples: {meeple_count}", True, INFO_TEXT_COLOR)
    screen.blit(meeple_text, (SIMULATION_WIDTH + ICON_PADDING, y_offset)); y_offset += 20
    cycle_text = info_font.render(f"Cycle: {cycle_info}", True, INFO_TEXT_COLOR)
    screen.blit(cycle_text, (SIMULATION_WIDTH + ICON_PADDING, y_offset)); y_offset += 20
    controls_text1 = info_font.render("'+'/'-': Speed", True, INFO_TEXT_COLOR)
    screen.blit(controls_text1, (SIMULATION_WIDTH + ICON_PADDING, y_offset))

def handle_collisions(meeples, obstacles, dt):
    meeples_to_remove = []
    push_scale = 1.0 # Scale push force by dt? Maybe not needed if movement handles dt well.

    # Meeple-Meeple
    for i in range(len(meeples)):
        m1 = meeples[i]
        if m1 in meeples_to_remove: continue
        for j in range(i + 1, len(meeples)):
            m2 = meeples[j]
            if m2 in meeples_to_remove: continue

            dist_x = m1.x - m2.x; dist_y = m1.y - m2.y
            dist_sq = dist_x**2 + dist_y**2
            min_dist = m1.collision_radius + m2.collision_radius
            min_dist_sq = min_dist**2

            if dist_sq < min_dist_sq and dist_sq > 0.001:
                distance = math.sqrt(dist_sq)
                # Simple overlap push correction
                overlap = (min_dist - distance) / 2.0
                push_x = (dist_x / distance) * overlap * COLLISION_PUSH_FORCE * push_scale
                push_y = (dist_y / distance) * overlap * COLLISION_PUSH_FORCE * push_scale
                # Directly adjust position based on overlap
                m1.x += push_x; m1.y += push_y
                m2.x -= push_x; m2.y -= push_y
                # Zero out velocity component towards each other to prevent sticking? Optional.

    # Meeple-Obstacle
    for meeple in meeples:
        if meeple in meeples_to_remove: continue
        meeple_col_rect = pygame.Rect(meeple.x - meeple.collision_radius, meeple.y - meeple.collision_radius,
                                       meeple.collision_radius * 2, meeple.collision_radius * 2)

        for obs in obstacles:
            # Use the obstacle's defined collision_rect
            if obs.collision_rect and meeple_col_rect.colliderect(obs.collision_rect):
                # Push meeple out of obstacle collision rect
                center_x_obs, center_y_obs = obs.collision_rect.center
                dist_x = meeple.x - center_x_obs; dist_y = meeple.y - center_y_obs
                dist = math.hypot(dist_x, dist_y)
                if dist < 0.01: dist = 0.01; dist_x = 0.01 # Avoid zero division

                # Calculate overlap: How much the meeple circle center is inside the obs rect?
                # This is complex for rects. Simplified push away from center:
                push_x = (dist_x / dist) * OBSTACLE_PUSH_FORCE * push_scale
                push_y = (dist_y / dist) * OBSTACLE_PUSH_FORCE * push_scale

                # Apply push directly to position
                meeple.x += push_x
                meeple.y += push_y

                # Dampen velocity towards obstacle center
                vel_x = meeple.dx / dt if dt > 0 else 0
                vel_y = meeple.dy / dt if dt > 0 else 0
                dot_product = vel_x * (dist_x/dist) + vel_y * (dist_y/dist)
                if dot_product < 0: # Moving towards center
                    meeple.dx -= dot_product * (dist_x/dist) * dt * 0.8 # Reflect component away
                    meeple.dy -= dot_product * (dist_y/dist) * dt * 0.8

            # Meeple-Hole Check (Specific type check)
            if isinstance(obs, Hole):
                 dist_x = meeple.x - obs.x; dist_y = meeple.y - obs.y
                 if dist_x**2 + dist_y**2 < (obs.radius * 0.8)**2:
                    if meeple not in meeples_to_remove:
                        meeples_to_remove.append(meeple)


    # Perform removal
    if meeples_to_remove:
        # Remove from home lists if assigned
        for meeple_to_remove in meeples_to_remove:
            if meeple_to_remove.home and meeple_to_remove in meeple_to_remove.home.residents:
                meeple_to_remove.home.residents.remove(meeple_to_remove)
        # Remove from main list
        meeples[:] = [m for m in meeples if m not in meeples_to_remove]


def initialize_rain_drops():
    global rain_drop_positions
    rain_drop_positions = [(random.randint(0, SIMULATION_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(NUM_RAIN_DROPS)]

def update_and_draw_rain(screen, dt):
    global rain_drop_positions
    if not is_raining: return
    drop_speed = RAIN_DROP_BASE_SPEED * simulation_speed_multiplier # Pixels per second

    for i in range(len(rain_drop_positions)):
        rain_drop_positions[i] = (rain_drop_positions[i][0], rain_drop_positions[i][1] + drop_speed * dt)
        if rain_drop_positions[i][1] > SCREEN_HEIGHT:
            rain_drop_positions[i] = (random.randint(0, SIMULATION_WIDTH), random.randint(-20, -5))

        start_pos = (rain_drop_positions[i][0], int(rain_drop_positions[i][1]))
        end_pos = (rain_drop_positions[i][0], int(rain_drop_positions[i][1] + RAIN_DROP_LENGTH))
        pygame.draw.line(screen, RAIN_DROP_COLOR, start_pos, end_pos, 1)

# --- Create Initial Meeples & Objects ---
center_x = SIMULATION_WIDTH // 2; center_y = SCREEN_HEIGHT // 2
spawn_radius = 70
# Simplified initial spawn - overlap possible but collision will fix
for _ in range(INITIAL_NUM_MEEPLES):
    angle = random.uniform(0, 2 * math.pi); r = random.uniform(0, spawn_radius)
    x = center_x + math.cos(angle) * r; y = center_y + math.sin(angle) * r
    meeples.append(Meeple(x, y, SIMULATION_WIDTH, SCREEN_HEIGHT))

# --- Game Loop ---
running = True
while running:
    # Timekeeping
    dt = clock.tick(60) / 1000.0 # Delta time in seconds
    dt = min(dt, 0.05) # Clamp dt to prevent large jumps if frame rate drops

    # Update Day/Night Cycle
    cycle_timer = (cycle_timer + dt * simulation_speed_multiplier) % FULL_CYCLE_SECONDS
    was_daytime = is_daytime
    is_daytime = cycle_timer < DAY_DURATION_SECONDS
    if was_daytime != is_daytime:
        print(f"Cycle changed to {'Day' if is_daytime else 'Night'}") # Feedback


    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        # Speed Control
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                simulation_speed_multiplier += SPEED_CHANGE_STEP
            elif event.key == pygame.K_MINUS:
                simulation_speed_multiplier -= SPEED_CHANGE_STEP
            simulation_speed_multiplier = max(MIN_SPEED_MULT, min(simulation_speed_multiplier, MAX_SPEED_MULT))

        # Tool Interaction
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
            elif selected_tool is not None and mouse_x < SIMULATION_WIDTH:
                # --- Create new object ---
                new_obj = None
                if selected_tool == "hole": new_obj = Hole(mouse_x, mouse_y)
                elif selected_tool == "hut": new_obj = Hut(mouse_x, mouse_y)
                elif selected_tool == "farm": new_obj = Farm(mouse_x, mouse_y)
                elif selected_tool == "factory": new_obj = Factory(mouse_x, mouse_y)
                elif selected_tool == "tree": new_obj = Tree(mouse_x, mouse_y)
                elif selected_tool == "hurricane":
                    active_effects = [e for e in active_effects if not isinstance(e, Hurricane)]
                    active_effects.append(Hurricane(mouse_x, mouse_y))
                elif selected_tool == "rain":
                    is_raining = not is_raining
                    if is_raining: rain_end_time = time.time() + RAIN_DURATION; initialize_rain_drops()
                elif selected_tool == "add_meeple":
                    new_meeple = Meeple(mouse_x, mouse_y, SIMULATION_WIDTH, SCREEN_HEIGHT)
                    can_place = True # Basic check - avoid placing directly inside obstacle centers
                    temp_rect = pygame.Rect(mouse_x-1, mouse_y-1, 2, 2)
                    for obs in placeables:
                         if obs.collision_rect and obs.collision_rect.colliderect(temp_rect):
                             can_place = False; break
                    if can_place: meeples.append(new_meeple)


                # --- Add Placeable & Check Overlap ---
                if isinstance(new_obj, Placeable):
                    can_place = True
                    if new_obj.collision_rect: # Ensure it has a collision rect defined
                        for existing_obj in placeables:
                            if existing_obj.collision_rect and new_obj.collision_rect.colliderect(existing_obj.collision_rect):
                                print(f"Cannot place {selected_tool}: overlaps existing object.")
                                can_place = False
                                break
                    if can_place:
                        placeables.append(new_obj)
                        print(f"Placed {selected_tool} at ({mouse_x}, {mouse_y})")
                        # --- Assign residents if it's a Hut ---
                        if isinstance(new_obj, Hut):
                             assigned_count = 0
                             # Find unassigned meeples
                             unassigned = [m for m in meeples if m.home is None]
                             random.shuffle(unassigned) # Assign randomly
                             for meeple_to_assign in unassigned:
                                 if meeple_to_assign.assign_home(new_obj): # Call assign_home on the Meeple
                                     assigned_count += 1
                                     if assigned_count >= new_obj.max_residents:
                                         break
                             print(f"Assigned {assigned_count} residents.")

                    else:
                        new_obj = None # Prevent adding if placement failed

                # Deselect tool? selected_tool = None

    # --- Update Phase ---
    # Update timed effects
    if is_raining and time.time() > rain_end_time: is_raining = False
    active_effects = [e for e in active_effects if e.is_active()]

    # Update Meeples
    current_speed_mod_rain = RAIN_SPEED_MULTIPLIER if is_raining else 1.0
    for meeple in meeples:
        meeple.speed_multiplier_effect = current_speed_mod_rain
        for effect in active_effects:
            if hasattr(effect, 'apply_effect'): effect.apply_effect(meeple)
        meeple.update(dt, is_daytime) # Pass dt and cycle state

    # --- Collision Handling ---
    handle_collisions(meeples, placeables, dt) # Pass dt if needed by collision logic

    # --- Drawing Phase ---
    screen.fill(FIELD_COLOR)

    # Environment objects (sorted by bottom of their *draw* rect)
    placeables_sorted = sorted(placeables, key=lambda obj: obj.draw_rect.bottom if obj.draw_rect else obj.y)
    for obj in placeables_sorted: obj.draw(screen)

    # Meeples (sorted by Y)
    meeples_sorted = sorted(meeples, key=lambda m: m.y)
    for meeple in meeples_sorted: meeple.draw(screen)

    # Effects visuals
    for effect in active_effects:
        if hasattr(effect, 'draw'): effect.draw(screen)

    # Rain
    update_and_draw_rain(screen, dt)

    # Toolbar
    cycle_phase = "Day" if is_daytime else "Night"
    remaining = (DAY_DURATION_SECONDS - cycle_timer) if is_daytime else (FULL_CYCLE_SECONDS - cycle_timer)
    cycle_info_str = f"{cycle_phase} ({remaining:.1f}s)"
    draw_toolbar(screen, selected_tool, simulation_speed_multiplier, len(meeples), cycle_info_str)

    pygame.display.flip()

# --- Cleanup ---
pygame.quit()
