import random
from utils import manhattan_distance

class Ant:
    def __init__(self, symbol, x, y, handicap=0.0):
        self.symbol = symbol
        self.x = x
        self.y = y
        self.has_food = False
        self.food_collected = 0
        self.target = None
        self.distance_traveled = 0  # Track total distance moved
        self.last_collection_time = 0  # Track when food was last collected
        self.food_value = 1  # Value of currently carried food (1 or 3)
        self.handicap = handicap  # Player's handicap level (0.0 - 1.0)
        self.base_food_collected = 0  # Track base score before handicap bonuses
        # Anti-stuck tracking
        self.prev_pos = (x, y)
        self.stuck_counter = 0

    def update(self, world):
        """Update ant's position and state"""
        start_pos = (self.x, self.y)
        if self.has_food:
            # Return to nest
            if (self.x, self.y) == world.nest_pos:
                self.has_food = False
                # Add the food value with handicap bonus
                base_value = getattr(self, 'food_value', 1)
                handicap_value = self.apply_handicap_food_bonus(base_value)
                self.food_collected += handicap_value
                self.base_food_collected += base_value  # Track base score
                self.last_collection_time = world.current_round
                self.target = None
            else:
                self._move_towards(world.nest_pos[0], world.nest_pos[1], world)
        else:
            # Look for food
            all_food = list(world.food_positions) + list(world.premium_food_positions)
            if not self.target or self.target not in all_food:
                self._find_new_food_target(world)
            
            if self.target:
                if (self.x, self.y) == self.target:
                    # Pick up food - set has_food flag and remember food type
                    self.has_food = True
                    # Store food value for later scoring at nest
                    if self.target in world.premium_food_positions:
                        self.food_value = 3  # Premium food worth 3 points
                        world.premium_food_positions.remove(self.target)
                    elif self.target in world.food_positions:
                        self.food_value = 1  # Regular food worth 1 point  
                        world.food_positions.remove(self.target)
                    else:
                        self.food_value = 1  # Default fallback
                    self.target = None
                else:
                    self._move_towards(self.target[0], self.target[1], world)
            else:
                self._random_move(world)

        # Anti-stuck check: if we didn't move this update, increment counter; else reset
        if (self.x, self.y) == start_pos:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
            self.prev_pos = (self.x, self.y)

        # Teleport if stuck too long
        if self.stuck_counter >= getattr(world, 'stuck_limit', 15):
            # Try to find a random safe teleport location
            safe_pos = self._find_safe_teleport_position(world)
            if safe_pos:
                self.x, self.y = safe_pos
                # Removed debug print for cleaner gameplay
            else:
                # Fallback to nest if no safe position found
                self.x, self.y = world.nest_pos
                # Removed debug print for cleaner gameplay
            self.target = None
            self.stuck_counter = 0

    def _find_new_food_target(self, world):
        """Find food source with some randomness to avoid all ants targeting the same food"""
        # Combine regular and premium food
        available_food = list(world.food_positions) + list(world.premium_food_positions)
        
        if not available_food:
            return
        
        # Prioritize premium food if it's nearby (within 10 spaces)
        premium_nearby = []
        for premium_pos in world.premium_food_positions:
            if manhattan_distance(self.x, self.y, premium_pos[0], premium_pos[1]) <= 10:
                premium_nearby.append(premium_pos)
        
        # 60% chance to target nearby premium food if available
        if premium_nearby and random.random() < 0.6:
            self.target = random.choice(premium_nearby)
        elif random.random() < 0.3:  # 30% chance to pick random food
            self.target = random.choice(available_food)
        else:
            # Find closest food with slight random variation to avoid clustering
            # Add a small random factor to the distance calculation
            self.target = min(available_food,
                             key=lambda pos: manhattan_distance(self.x, self.y, pos[0], pos[1]) * 
                                            (0.8 + random.random() * 0.4))  # Random factor between 0.8 and 1.2

    def _move_towards(self, target_x, target_y, world):
        """Move one step towards target with some randomness, avoiding obstacles"""
        dx = 0 if self.x == target_x else (1 if self.x < target_x else -1)
        dy = 0 if self.y == target_y else (1 if self.y < target_y else -1)
        
        # Default move positions
        move_x, move_y = self.x + dx, self.y + dy
        
        # Check if direct movement would hit an obstacle
        direct_move_blocked = (move_x, move_y) in world.obstacle_positions
        
        # If direct move is blocked or we're taking a detour (20% chance), find an alternative path
        if direct_move_blocked or random.random() < 0.2:
            # Generate all possible move directions
            possible_moves = []
            
            # Check all four directions
            for test_dx, test_dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                test_x, test_y = self.x + test_dx, self.y + test_dy
                
                # Check if move is valid (in bounds and not an obstacle)
                if (world.is_valid_position(test_x, test_y) and 
                    (test_x, test_y) not in world.obstacle_positions):
                    
                    # Calculate how good this move is (lower score is better)
                    # Distance to target after this move
                    distance_score = manhattan_distance(test_x, test_y, target_x, target_y)
                    
                    # Add a small random factor to avoid all ants making the same choice
                    random_factor = random.random() * 1.5
                    
                    # Prefer moves that make progress in both x and y directions if possible
                    direction_bonus = 0
                    if (test_dx != 0 and dx != 0 and test_dx == dx) or (test_dy != 0 and dy != 0 and test_dy == dy):
                        direction_bonus = -1  # Bonus for moving in the correct direction
                        
                    # Calculate final score (lower is better)
                    move_score = distance_score + random_factor + direction_bonus
                    
                    possible_moves.append(((test_x, test_y), move_score))
            
            # If we have valid moves, choose the best one
            if possible_moves:
                # Sort by score (lower is better)
                possible_moves.sort(key=lambda m: m[1])
                
                # Take the best move most of the time, but occasionally take the 2nd best for variety
                if len(possible_moves) > 1 and random.random() < 0.2:  # 20% chance to take 2nd best move
                    best_move = possible_moves[1][0]
                else:
                    best_move = possible_moves[0][0]
                
                # Track movement distance before updating position
                old_x, old_y = self.x, self.y
                self.x, self.y = best_move
                
                # Increment distance traveled
                self.distance_traveled += 1
            
        # If no obstacles and we're not taking a detour, move directly
        elif not direct_move_blocked:
            # Save original position to track if we moved
            old_x, old_y = self.x, self.y
            
            # Randomly decide which direction to try first
            if random.random() < 0.5:
                # Try Y first, then X
                if dy != 0 and world.is_valid_position(self.x, self.y + dy) and (self.x, self.y + dy) not in world.obstacle_positions:
                    self.y += dy
                elif dx != 0 and world.is_valid_position(self.x + dx, self.y) and (self.x + dx, self.y) not in world.obstacle_positions:
                    self.x += dx
            else:
                # Try X first, then Y
                if dx != 0 and world.is_valid_position(self.x + dx, self.y) and (self.x + dx, self.y) not in world.obstacle_positions:
                    self.x += dx
                elif dy != 0 and world.is_valid_position(self.x, self.y + dy) and (self.x, self.y + dy) not in world.obstacle_positions:
                    self.y += dy
                    
            # If we moved, increment distance traveled
            if self.x != old_x or self.y != old_y:
                self.distance_traveled += 1

    def _random_move(self, world):
        """Make a random move when no target is available - more exploratory, avoiding obstacles"""
        # Check if we're near the nest - sometimes move away from it
        near_nest = manhattan_distance(self.x, self.y, world.nest_pos[0], world.nest_pos[1]) < 3
        
        # Include all possible directions by default
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        # Check for nearby obstacles to avoid getting stuck
        nearby_obstacles = sum(1 for dx, dy in directions 
                             if (self.x + dx, self.y + dy) in world.obstacle_positions)
        
        # If we're surrounded by obstacles, prioritize diagonal moves
        if nearby_obstacles >= 3:
            # Add more weight to diagonal moves
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)] * 2)
        
        # If we're near the nest, prioritize moving outward to explore
        if near_nest:
            # Calculate vector from nest to current position
            away_x = self.x - world.nest_pos[0]
            away_y = self.y - world.nest_pos[1]
            
            # Add weighted directions that move further from nest
            if away_x > 0:
                directions.extend([(1, 0), (1, 1), (1, -1)] * 2)
            elif away_x < 0:
                directions.extend([(-1, 0), (-1, 1), (-1, -1)] * 2)
                
            if away_y > 0:
                directions.extend([(0, 1), (1, 1), (-1, 1)] * 2)
            elif away_y < 0:
                directions.extend([(0, -1), (1, -1), (-1, -1)] * 2)
        
        # Shuffle all possible directions
        random.shuffle(directions)
        
        # Flag to track if we've moved
        moved = False
        
        # Try each direction until a valid move is found
        for dx, dy in directions:
            new_x, new_y = self.x + dx, self.y + dy
            
            # Check for valid move (in bounds and not an obstacle)
            if (world.is_valid_position(new_x, new_y) and 
                (new_x, new_y) not in world.obstacle_positions):
                
                self.x, self.y = new_x, new_y
                self.distance_traveled += 1
                moved = True
                break
                
        # If we couldn't move (trapped by obstacles), try harder to find a path
        # by considering all valid adjacent cells, even if they're not ideal
        if not moved:
            # Try one more time with just the four cardinal directions
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_x, new_y = self.x + dx, self.y + dy
                if (world.is_valid_position(new_x, new_y) and 
                    (new_x, new_y) not in world.obstacle_positions):
                    self.x, self.y = new_x, new_y
                    self.distance_traveled += 1
                    break
    
    def _find_safe_teleport_position(self, world):
        """Find a safe teleport position away from walls and obstacles"""
        # Try to find a good teleport spot - prioritize open areas
        for attempt in range(50):
            # Pick a random position
            x = random.randint(3, world.height - 4)  # Keep away from edges
            y = random.randint(3, world.width - 4)
            
            # Check if this position and its surroundings are clear
            if (world.is_valid_position(x, y) and 
                (x, y) not in world.obstacle_positions):
                
                # Check that the area around this position is relatively clear
                obstacles_nearby = 0
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        check_x, check_y = x + dx, y + dy
                        if (world.is_valid_position(check_x, check_y) and 
                            (check_x, check_y) in world.obstacle_positions):
                            obstacles_nearby += 1
                
                # If less than 30% of nearby area is obstacles, it's a good spot
                if obstacles_nearby < 7:  # Less than 7 out of 25 nearby cells
                    return (x, y)
        
        # If we can't find a good spot, return None to fall back to nest
        return None
    
    def apply_handicap_food_bonus(self, base_value):
        """Apply handicap bonus to food scoring (0-50% bonus)"""
        from player_history import HandicapScoring
        return HandicapScoring.apply_food_bonus(base_value, self.handicap)
    
    def apply_handicap_distance_bonus(self, base_distance):
        """Apply handicap bonus to distance tiebreaker (0-30% bonus)"""
        from player_history import HandicapScoring
        return HandicapScoring.apply_distance_tiebreaker_bonus(base_distance, self.handicap)
    
    def get_handicap_premium_attraction(self):
        """Get premium food attraction bonus (0-100% better chance)"""
        from player_history import HandicapScoring
        return HandicapScoring.apply_premium_food_attraction(self.handicap)
