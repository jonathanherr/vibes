import random
import math
from ant import Ant
from utils import manhattan_distance, colorize, ANT_COLORS, assign_color_to_ant, NEST_COLOR, FOOD_COLOR, BORDER_COLOR, OBSTACLE_COLOR, CARRYING_ANT_COLOR


class GameWorld:

    def __init__(self, width, height, num_ants, custom_labels=None, stuck_limit=15):
        self.width = width
        self.height = height
        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        self.nest_pos = (height // 2, width // 2)
        self.ants = []
        self.food_positions = set()
        self.premium_food_positions = set()  # High-value food worth 3 points
        self.obstacle_positions = set()
        self.starting_positions = []
        self.current_round = 0  # Track current round for tiebreaker purposes
        self.stuck_limit = stuck_limit  # Anti-stuck threshold

        # Place nest
        self.grid[self.nest_pos[0]][self.nest_pos[1]] = 'N'

        # Generate obstacles first (before food and starting positions)
        self._generate_obstacles()

        # Generate multiple starting points around the nest
        self._generate_starting_positions(num_ants)

        # Create ants at different starting positions
        for i in range(num_ants):
            # Use custom labels if provided, otherwise default to A, B, C, etc.
            if custom_labels and i < len(custom_labels):
                ant_symbol = custom_labels[i]
            else:
                ant_symbol = chr(65 + i)  # A, B, C, etc.

            start_pos = self.starting_positions[i %
                                                len(self.starting_positions)]
            self.ants.append(Ant(ant_symbol, start_pos[0], start_pos[1]))

        # Initial food placement - scale with number of ants and map size
        # Larger map needs more food but maintain scarcity for competition
        map_area = self.width * self.height
        food_density = 0.025  # About 2.5% of map area as food (was more crowded before)
        
        regular_food = max(int(map_area * food_density), num_ants * 2)  # Scale with map size
        self._generate_regular_food(regular_food)
        
        # Add premium food pieces - scale with both ants and map size
        premium_food_count = min(max(num_ants // 4, 3), 6)  # 3-6 premium pieces for larger map
        self._generate_premium_food(premium_food_count)

    def _generate_obstacles(self):
        """Create obstacles in the world"""
        # Create some walls and barriers

        # 1. Create some random scatter obstacles
        num_scatter_obstacles = self.width * self.height // 30  # About 3% of grid as scattered obstacles

        for _ in range(num_scatter_obstacles):
            for attempt in range(50):  # Try 50 times to place each obstacle
                x = random.randint(0, self.height - 1)
                y = random.randint(0, self.width - 1)

                # Make sure not too close to nest
                if manhattan_distance(x, y, self.nest_pos[0],
                                      self.nest_pos[1]) < 6:
                    continue

                # Place obstacle if space is empty
                if self.grid[x][y] == ' ':
                    self.obstacle_positions.add((x, y))
                    self.grid[x][y] = '#'
                    break

        # 2. Create 2-3 "wall" structures that ants must navigate around
        num_walls = random.randint(2, 3)

        for _ in range(num_walls):
            # Shorter wall length to prevent trapping - scale with map size
            max_wall_length = min(self.width, self.height) // 4  # Max 25% of smallest dimension
            wall_length = random.randint(3, max(4, max_wall_length))

            # Pick a random starting point away from nest
            for attempt in range(100):
                start_x = random.randint(0, self.height - 1)
                start_y = random.randint(0, self.width - 1)

                # Check distance from nest
                if manhattan_distance(start_x, start_y, self.nest_pos[0],
                                      self.nest_pos[1]) < 8:
                    continue

                # Choose a direction for the wall (horizontal or vertical)
                is_horizontal = random.choice([True, False])

                # Check if we can fit the wall without going off-grid
                if is_horizontal and start_y + wall_length >= self.width:
                    continue
                if not is_horizontal and start_x + wall_length >= self.height:
                    continue

                # Place the wall
                valid_wall = True
                wall_positions = []

                for i in range(wall_length):
                    if is_horizontal:
                        pos = (start_x, start_y + i)
                    else:
                        pos = (start_x + i, start_y)

                    # Check if position already has something
                    if pos[0] < 0 or pos[0] >= self.height or pos[
                            1] < 0 or pos[1] >= self.width:
                        valid_wall = False
                        break

                    if pos == self.nest_pos or manhattan_distance(
                            pos[0], pos[1], self.nest_pos[0],
                            self.nest_pos[1]) < 6:
                        valid_wall = False
                        break

                    wall_positions.append(pos)

                if valid_wall:
                    # Add all wall positions to obstacles
                    for pos in wall_positions:
                        self.obstacle_positions.add(pos)
                        self.grid[pos[0]][pos[1]] = '#'
                    break  # Successfully placed wall

    def _generate_regular_food(self, count):
        """Generate regular food worth 1 point each"""
        self.spawn_food(count)
    
    def _generate_premium_food(self, count):
        """Generate premium food worth 3 points each - rare and valuable"""
        for _ in range(count):
            if len(self.premium_food_positions) >= count:
                break
            
            # Use similar placement strategy as regular food but more selective
            min_nest_distance = min(self.width, self.height) // 2  # Further from nest
            min_food_distance = min(self.width, self.height) // 3   # Well-separated
            
            for attempt in range(100):  # Try hard to place premium food
                # Place in corners and edges preferentially - harder to reach
                if attempt < 60:
                    # Strategy: Place in corners/edges (harder to reach)
                    edge = random.randint(0, 3)
                    if edge == 0:  # Top edge
                        x = random.randint(0, 2)
                        y = random.randint(0, self.width - 1)
                    elif edge == 1:  # Right edge
                        x = random.randint(0, self.height - 1)
                        y = random.randint(self.width - 3, self.width - 1)
                    elif edge == 2:  # Bottom edge
                        x = random.randint(self.height - 3, self.height - 1)
                        y = random.randint(0, self.width - 1)
                    else:  # Left edge
                        x = random.randint(0, self.height - 1)
                        y = random.randint(0, 2)
                else:
                    # Fallback to random placement
                    x = random.randint(0, self.height - 1)
                    y = random.randint(0, self.width - 1)
                
                # Ensure coordinates are within bounds
                x = max(0, min(x, self.height - 1))
                y = max(0, min(y, self.width - 1))
                
                if self.grid[x][y] != ' ' or (x, y) == self.nest_pos:
                    continue  # Space already occupied
                
                # Check distance from nest (premium food should be harder to reach)
                if manhattan_distance(x, y, self.nest_pos[0], self.nest_pos[1]) < min_nest_distance:
                    continue
                
                # Check distance from other food (premium and regular)
                too_close = False
                all_food = list(self.food_positions) + list(self.premium_food_positions)
                for food_pos in all_food:
                    if manhattan_distance(x, y, food_pos[0], food_pos[1]) < min_food_distance:
                        too_close = True
                        break
                
                if not too_close:
                    self.premium_food_positions.add((x, y))
                    break

    def _generate_starting_positions(self, num_ants):
        """Create multiple starting positions for ants"""
        # Always include the nest itself as a starting point
        self.starting_positions.append(self.nest_pos)

        # Create starting points in a ring around the nest
        num_positions = min(8, num_ants)  # Up to 8 starting positions

        for i in range(num_positions -
                       1):  # -1 because we already have the nest
            angle = (i / (num_positions - 1)) * 2 * math.pi

            # Distance 2-3 cells from nest
            distance = random.randint(2, 3)

            x = int(self.nest_pos[0] + distance * math.sin(angle))
            y = int(self.nest_pos[1] + distance * math.cos(angle))

            # Make sure position is valid
            x = max(1, min(x, self.height - 2))
            y = max(1, min(y, self.width - 2))

            self.starting_positions.append((x, y))

    def spawn_food(self, count):
        """Spawn new food pieces in empty spaces with better distribution"""
        for _ in range(count):
            if len(self.food_positions) >= (self.width * self.height) // 4:
                break  # Prevent overcrowding

            # Scale distances with map size
            min_nest_distance = min(self.width, self.height) // 3  # Scale with map size
            min_food_distance = min(self.width, self.height) // 4  # Scale with map size

            # Try to find a good spot with better distribution
            for attempt in range(200):  # More attempts to find good spots
                # Use different strategies for placement
                if attempt < 75:
                    # Strategy 1: Place food in outer regions using angular distribution
                    angle = random.uniform(0, 2 *
                                           math.pi)  # Random angle in radians
                    # Prefer placing food farther from the nest
                    distance_factor = random.random(
                    )**0.5  # Bias toward larger distances
                    max_distance = min(self.width, self.height) // 2
                    distance = min_nest_distance + int(
                        distance_factor * (max_distance - min_nest_distance))

                    x = int(self.nest_pos[0] + distance * math.sin(angle))
                    y = int(self.nest_pos[1] + distance * math.cos(angle))
                elif attempt < 150:
                    # Strategy 2: Focus on the corners and edges of the world
                    if random.random() < 0.7:  # 70% chance for edge placement
                        # Pick a random edge
                        edge = random.randint(0, 3)
                        if edge == 0:  # Top edge
                            x = 0
                            y = random.randint(0, self.width - 1)
                        elif edge == 1:  # Right edge
                            x = random.randint(0, self.height - 1)
                            y = self.width - 1
                        elif edge == 2:  # Bottom edge
                            x = self.height - 1
                            y = random.randint(0, self.width - 1)
                        else:  # Left edge
                            x = random.randint(0, self.height - 1)
                            y = 0
                    else:  # 30% chance for corner-ish placement
                        quadrant = random.randint(0, 3)
                        if quadrant == 0:  # Top-left
                            x = random.randint(0, self.height // 3)
                            y = random.randint(0, self.width // 3)
                        elif quadrant == 1:  # Top-right
                            x = random.randint(0, self.height // 3)
                            y = random.randint(2 * self.width // 3,
                                               self.width - 1)
                        elif quadrant == 2:  # Bottom-right
                            x = random.randint(2 * self.height // 3,
                                               self.height - 1)
                            y = random.randint(2 * self.width // 3,
                                               self.width - 1)
                        else:  # Bottom-left
                            x = random.randint(2 * self.height // 3,
                                               self.height - 1)
                            y = random.randint(0, self.width // 3)
                else:
                    # Strategy 3: Fallback to pure random placement
                    x = random.randint(0, self.height - 1)
                    y = random.randint(0, self.width - 1)

                # Ensure coordinates are within bounds
                x = max(0, min(x, self.height - 1))
                y = max(0, min(y, self.width - 1))

                if self.grid[x][y] != ' ' or (x, y) == self.nest_pos:
                    continue  # Space already occupied

                # Check distance from nest
                if manhattan_distance(x, y, self.nest_pos[0],
                                      self.nest_pos[1]) < min_nest_distance:
                    continue  # Too close to nest

                # Check distance from other food
                too_close = False
                for food_pos in self.food_positions:
                    if manhattan_distance(x, y, food_pos[0],
                                          food_pos[1]) < min_food_distance:
                        too_close = True
                        break

                if not too_close:
                    self.food_positions.add((x, y))
                    break

    def update(self):
        """Update game state"""
        # No new food spawning - fixed amount at start

        # Increment round counter
        self.current_round += 1

        # Create a copy of the ants list and shuffle it for fair updates
        ants_to_update = self.ants.copy()
        random.shuffle(ants_to_update)

        # Keep track of ant positions to avoid collisions
        occupied_positions = set()
        occupied_positions.add(self.nest_pos)  # Mark nest as occupied
        occupied_positions.update(
            self.obstacle_positions)  # Mark obstacles as occupied

        # First pass: update ants' intended positions
        for ant in ants_to_update:
            # Save original position in case we need to revert
            original_x, original_y = ant.x, ant.y

            # Update ant position
            ant.update(self)

            # Check for collision with another ant or obstacle
            current_pos = (ant.x, ant.y)
            if current_pos in occupied_positions and current_pos != self.nest_pos:
                # Revert to original position if collision occurs
                # (nest position is allowed to have multiple ants)
                ant.x, ant.y = original_x, original_y
                current_pos = (ant.x, ant.y)

            # Mark position as occupied
            occupied_positions.add(current_pos)

        # Update grid
        self.grid = [[' ' for _ in range(self.width)]
                     for _ in range(self.height)]

        # Place obstacles
        for obstacle_pos in self.obstacle_positions:
            self.grid[obstacle_pos[0]][obstacle_pos[1]] = '#'

        # Place nest
        self.grid[self.nest_pos[0]][self.nest_pos[1]] = 'N'

        # Place food
        for food_pos in self.food_positions:
            self.grid[food_pos[0]][food_pos[1]] = 'F'
            
        # Place premium food with different symbol
        for premium_pos in self.premium_food_positions:
            self.grid[premium_pos[0]][premium_pos[1]] = 'P'

        # Place ants - shuffle again to ensure random rendering order
        random.shuffle(ants_to_update)
        for ant in ants_to_update:
            # Allow multiple ants on nest, otherwise one ant per cell
            if (ant.x,
                    ant.y) != self.nest_pos or self.grid[ant.x][ant.y] == 'N':
                # Don't place ants on obstacles
                if (ant.x, ant.y) not in self.obstacle_positions:
                    self.grid[ant.x][ant.y] = ant.symbol

    def render(self):
        """Render the game world as a string with vintage antfarm frame"""
        from utils import FRAME_COLOR, FRAME_ACCENT_COLOR, FRAME_LABEL_COLOR
        
        # Create vintage antfarm frame
        frame_width = self.width + 8  # Extra space for decorative frame
        
        # Top frame with decorative corners
        top_frame = colorize('╔', FRAME_ACCENT_COLOR) + colorize('═' * 3, FRAME_COLOR) + \
                   colorize('[ ANT FARM SIMULATOR ]', FRAME_LABEL_COLOR) + \
                   colorize('═' * (frame_width - 24), FRAME_COLOR) + colorize('╗', FRAME_ACCENT_COLOR)
        result = [top_frame]
        
        # Decorative separator
        separator = colorize('║', FRAME_ACCENT_COLOR) + colorize('░', FRAME_COLOR) * 2 + \
                   colorize('+' + '─' * self.width + '+', BORDER_COLOR) + \
                   colorize('░', FRAME_COLOR) * 2 + colorize('║', FRAME_ACCENT_COLOR)
        result.append(separator)

        # Build a set of positions where ants are carrying food for special rendering
        carrying_positions = {(ant.x, ant.y) for ant in self.ants if ant.has_food}

        # Process each row of the grid
        for row_idx, row in enumerate(self.grid):
            colored_row = []

            # Process each cell in the row
            for col_idx, cell in enumerate(row):
                if cell == ' ':
                    # Empty space
                    colored_row.append(' ')
                elif cell == 'N' and (row_idx, col_idx) == self.nest_pos:
                    # Nest (only at nest position)
                    colored_row.append(colorize('N', NEST_COLOR))
                elif cell == 'F' and (row_idx, col_idx) in self.food_positions:
                    # Regular food (only at food positions)
                    colored_row.append(colorize('F', FOOD_COLOR))
                elif cell == 'P' and (row_idx, col_idx) in self.premium_food_positions:
                    # Premium food (worth 3 points) - use bright magenta
                    from utils import Colors
                    PREMIUM_FOOD_COLOR = Colors.BG_MAGENTA + Colors.WHITE + Colors.BOLD
                    colored_row.append(colorize('P', PREMIUM_FOOD_COLOR))
                elif cell == '#':
                    # Obstacle
                    colored_row.append(colorize('#', OBSTACLE_COLOR))
                else:
                    # Ant (any symbol - default or custom)
                    if (row_idx, col_idx) in carrying_positions:
                        colored_row.append(colorize(cell, CARRYING_ANT_COLOR))
                    else:
                        ant_color = assign_color_to_ant(cell)
                        colored_row.append(colorize(cell, ant_color))

            # Add row with vintage frame sides
            row_with_frame = colorize('║', FRAME_ACCENT_COLOR) + colorize('░', FRAME_COLOR) * 2 + \
                            colorize('|', BORDER_COLOR) + ''.join(colored_row) + colorize('|', BORDER_COLOR) + \
                            colorize('░', FRAME_COLOR) * 2 + colorize('║', FRAME_ACCENT_COLOR)
            result.append(row_with_frame)

        # Bottom separator
        bottom_separator = colorize('║', FRAME_ACCENT_COLOR) + colorize('░', FRAME_COLOR) * 2 + \
                          colorize('+' + '─' * self.width + '+', BORDER_COLOR) + \
                          colorize('░', FRAME_COLOR) * 2 + colorize('║', FRAME_ACCENT_COLOR)
        result.append(bottom_separator)
        
        # Bottom frame with decorative corners
        bottom_frame = colorize('╚', FRAME_ACCENT_COLOR) + colorize('═' * 3, FRAME_COLOR) + \
                      colorize('[ VINTAGE EDITION ]', FRAME_LABEL_COLOR) + \
                      colorize('═' * (frame_width - 21), FRAME_COLOR) + colorize('╝', FRAME_ACCENT_COLOR)
        result.append(bottom_frame)
        
        return '\n'.join(result)

    def is_valid_position(self, x, y):
        """Check if position is within grid bounds"""
        return 0 <= x < self.height and 0 <= y < self.width
