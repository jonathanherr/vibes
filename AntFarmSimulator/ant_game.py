
#!/usr/bin/env python3
import os
import time
import sys
import select
import tty
import termios
import random
import math

# Color definitions
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BG_BLACK = '\033[40m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'

# Color schemes for ants
ANT_COLOR_SCHEMES = [
    Colors.RED, Colors.GREEN, Colors.YELLOW, Colors.BLUE, Colors.MAGENTA, Colors.CYAN,
    Colors.RED + Colors.BOLD, Colors.GREEN + Colors.BOLD, Colors.YELLOW + Colors.BOLD,
    Colors.BLUE + Colors.BOLD, Colors.MAGENTA + Colors.BOLD, Colors.CYAN + Colors.BOLD,
    Colors.RED + Colors.UNDERLINE, Colors.GREEN + Colors.UNDERLINE, Colors.YELLOW + Colors.UNDERLINE,
    Colors.BLUE + Colors.UNDERLINE, Colors.MAGENTA + Colors.UNDERLINE, Colors.CYAN + Colors.UNDERLINE,
    Colors.RED + Colors.BOLD + Colors.UNDERLINE, Colors.GREEN + Colors.BOLD + Colors.UNDERLINE,
    Colors.YELLOW + Colors.BOLD + Colors.UNDERLINE, Colors.BLUE + Colors.BOLD + Colors.UNDERLINE,
    Colors.MAGENTA + Colors.BOLD + Colors.UNDERLINE, Colors.CYAN + Colors.BOLD + Colors.UNDERLINE,
    Colors.WHITE + Colors.BOLD, Colors.WHITE + Colors.UNDERLINE
]

# Game element colors
NEST_COLOR = Colors.BG_BLUE + Colors.WHITE + Colors.BOLD
FOOD_COLOR = Colors.BG_GREEN + Colors.WHITE
BORDER_COLOR = Colors.WHITE + Colors.BOLD
OBSTACLE_COLOR = Colors.BG_BLACK + Colors.WHITE

def manhattan_distance(x1, y1, x2, y2):
    return abs(x2 - x1) + abs(y2 - y1)

def colorize(text, color_code):
    return f"{color_code}{text}{Colors.RESET}"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def assign_color_to_ant(symbol):
    color_index = ord(symbol) % len(ANT_COLOR_SCHEMES)
    return ANT_COLOR_SCHEMES[color_index]

class Ant:
    def __init__(self, symbol, x, y):
        self.symbol = symbol
        self.x = x
        self.y = y
        self.has_food = False
        self.food_collected = 0
        self.target = None
        self.distance_traveled = 0
        self.last_collection_time = 0

    def update(self, world):
        if self.has_food:
            if (self.x, self.y) == world.nest_pos:
                self.has_food = False
                self.food_collected += 1
                self.last_collection_time = world.current_round
                self.target = None
            else:
                self._move_towards(world.nest_pos[0], world.nest_pos[1], world)
        else:
            if not self.target or self.target not in world.food_positions:
                self._find_new_food_target(world)
            
            if self.target:
                if (self.x, self.y) == self.target:
                    self.has_food = True
                    if self.target in world.food_positions:
                        world.food_positions.remove(self.target)
                    self.target = None
                else:
                    self._move_towards(self.target[0], self.target[1], world)
            else:
                self._random_move(world)

    def _find_new_food_target(self, world):
        if not world.food_positions:
            return
        
        available_food = list(world.food_positions)
        
        if random.random() < 0.3:
            self.target = random.choice(available_food)
        else:
            self.target = min(available_food,
                            key=lambda pos: manhattan_distance(self.x, self.y, pos[0], pos[1]) * 
                            (0.8 + random.random() * 0.4))

    def _move_towards(self, target_x, target_y, world):
        dx = 0 if self.x == target_x else (1 if self.x < target_x else -1)
        dy = 0 if self.y == target_y else (1 if self.y < target_y else -1)
        
        move_x, move_y = self.x + dx, self.y + dy
        direct_move_blocked = (move_x, move_y) in world.obstacle_positions
        
        if direct_move_blocked or random.random() < 0.2:
            possible_moves = []
            
            for test_dx, test_dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                test_x, test_y = self.x + test_dx, self.y + test_dy
                
                if (world.is_valid_position(test_x, test_y) and 
                    (test_x, test_y) not in world.obstacle_positions):
                    
                    distance_score = manhattan_distance(test_x, test_y, target_x, target_y)
                    random_factor = random.random() * 1.5
                    direction_bonus = 0
                    if (test_dx != 0 and dx != 0 and test_dx == dx) or (test_dy != 0 and dy != 0 and test_dy == dy):
                        direction_bonus = -1
                    
                    move_score = distance_score + random_factor + direction_bonus
                    possible_moves.append(((test_x, test_y), move_score))
            
            if possible_moves:
                possible_moves.sort(key=lambda m: m[1])
                
                if len(possible_moves) > 1 and random.random() < 0.2:
                    best_move = possible_moves[1][0]
                else:
                    best_move = possible_moves[0][0]
                
                old_x, old_y = self.x, self.y
                self.x, self.y = best_move
                self.distance_traveled += 1
            
        elif not direct_move_blocked:
            old_x, old_y = self.x, self.y
            
            if random.random() < 0.5:
                if dy != 0 and world.is_valid_position(self.x, self.y + dy) and (self.x, self.y + dy) not in world.obstacle_positions:
                    self.y += dy
                elif dx != 0 and world.is_valid_position(self.x + dx, self.y) and (self.x + dx, self.y) not in world.obstacle_positions:
                    self.x += dx
            else:
                if dx != 0 and world.is_valid_position(self.x + dx, self.y) and (self.x + dx, self.y) not in world.obstacle_positions:
                    self.x += dx
                elif dy != 0 and world.is_valid_position(self.x, self.y + dy) and (self.x, self.y + dy) not in world.obstacle_positions:
                    self.y += dy
                    
            if self.x != old_x or self.y != old_y:
                self.distance_traveled += 1

    def _random_move(self, world):
        near_nest = manhattan_distance(self.x, self.y, world.nest_pos[0], world.nest_pos[1]) < 3
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        nearby_obstacles = sum(1 for dx, dy in directions 
                             if (self.x + dx, self.y + dy) in world.obstacle_positions)
        
        if nearby_obstacles >= 3:
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)] * 2)
        
        if near_nest:
            away_x = self.x - world.nest_pos[0]
            away_y = self.y - world.nest_pos[1]
            
            if away_x > 0:
                directions.extend([(1, 0), (1, 1), (1, -1)] * 2)
            elif away_x < 0:
                directions.extend([(-1, 0), (-1, 1), (-1, -1)] * 2)
                
            if away_y > 0:
                directions.extend([(0, 1), (1, 1), (-1, 1)] * 2)
            elif away_y < 0:
                directions.extend([(0, -1), (1, -1), (-1, -1)] * 2)
        
        random.shuffle(directions)
        moved = False
        
        for dx, dy in directions:
            new_x, new_y = self.x + dx, self.y + dy
            
            if (world.is_valid_position(new_x, new_y) and 
                (new_x, new_y) not in world.obstacle_positions):
                
                self.x, self.y = new_x, new_y
                self.distance_traveled += 1
                moved = True
                break
                
        if not moved:
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_x, new_y = self.x + dx, self.y + dy
                if (world.is_valid_position(new_x, new_y) and 
                    (new_x, new_y) not in world.obstacle_positions):
                    self.x, self.y = new_x, new_y
                    self.distance_traveled += 1
                    break

class GameWorld:
    def __init__(self, width, height, num_ants, custom_labels=None):
        self.width = width
        self.height = height
        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        self.nest_pos = (height // 2, width // 2)
        self.ants = []
        self.food_positions = set()
        self.obstacle_positions = set()
        self.starting_positions = []
        self.current_round = 0

        self.grid[self.nest_pos[0]][self.nest_pos[1]] = 'N'
        self._generate_obstacles()
        self._generate_starting_positions(num_ants)

        for i in range(num_ants):
            if custom_labels and i < len(custom_labels):
                ant_symbol = custom_labels[i]
            else:
                ant_symbol = chr(65 + i)

            start_pos = self.starting_positions[i % len(self.starting_positions)]
            self.ants.append(Ant(ant_symbol, start_pos[0], start_pos[1]))

        food_amount = max(num_ants * 4, 10)
        self._generate_fixed_food(food_amount)

    def _generate_obstacles(self):
        num_scatter_obstacles = self.width * self.height // 30

        for _ in range(num_scatter_obstacles):
            for attempt in range(50):
                x = random.randint(0, self.height - 1)
                y = random.randint(0, self.width - 1)

                if manhattan_distance(x, y, self.nest_pos[0], self.nest_pos[1]) < 6:
                    continue

                if self.grid[x][y] == ' ':
                    self.obstacle_positions.add((x, y))
                    self.grid[x][y] = '#'
                    break

        num_walls = random.randint(2, 3)

        for _ in range(num_walls):
            wall_length = random.randint(5, 12)

            for attempt in range(100):
                start_x = random.randint(0, self.height - 1)
                start_y = random.randint(0, self.width - 1)

                if manhattan_distance(start_x, start_y, self.nest_pos[0], self.nest_pos[1]) < 8:
                    continue

                is_horizontal = random.choice([True, False])

                if is_horizontal and start_y + wall_length >= self.width:
                    continue
                if not is_horizontal and start_x + wall_length >= self.height:
                    continue

                valid_wall = True
                wall_positions = []

                for i in range(wall_length):
                    if is_horizontal:
                        pos = (start_x, start_y + i)
                    else:
                        pos = (start_x + i, start_y)

                    if pos[0] < 0 or pos[0] >= self.height or pos[1] < 0 or pos[1] >= self.width:
                        valid_wall = False
                        break

                    if pos == self.nest_pos or manhattan_distance(pos[0], pos[1], self.nest_pos[0], self.nest_pos[1]) < 6:
                        valid_wall = False
                        break

                    wall_positions.append(pos)

                if valid_wall:
                    for pos in wall_positions:
                        self.obstacle_positions.add(pos)
                        self.grid[pos[0]][pos[1]] = '#'
                    break

    def _generate_fixed_food(self, count):
        self.spawn_food(count)

    def _generate_starting_positions(self, num_ants):
        self.starting_positions.append(self.nest_pos)
        num_positions = min(8, num_ants)

        for i in range(num_positions - 1):
            angle = (i / (num_positions - 1)) * 2 * math.pi
            distance = random.randint(2, 3)
            x = int(self.nest_pos[0] + distance * math.sin(angle))
            y = int(self.nest_pos[1] + distance * math.cos(angle))
            x = max(1, min(x, self.height - 2))
            y = max(1, min(y, self.width - 2))
            self.starting_positions.append((x, y))

    def spawn_food(self, count):
        for _ in range(count):
            if len(self.food_positions) >= (self.width * self.height) // 4:
                break

            min_nest_distance = min(self.width, self.height) // 3
            min_food_distance = min(self.width, self.height) // 4

            for attempt in range(200):
                if attempt < 75:
                    angle = random.uniform(0, 2 * math.pi)
                    distance_factor = random.random()**0.5
                    max_distance = min(self.width, self.height) // 2
                    distance = min_nest_distance + int(distance_factor * (max_distance - min_nest_distance))
                    x = int(self.nest_pos[0] + distance * math.sin(angle))
                    y = int(self.nest_pos[1] + distance * math.cos(angle))
                elif attempt < 150:
                    if random.random() < 0.7:
                        edge = random.randint(0, 3)
                        if edge == 0:
                            x = 0
                            y = random.randint(0, self.width - 1)
                        elif edge == 1:
                            x = random.randint(0, self.height - 1)
                            y = self.width - 1
                        elif edge == 2:
                            x = self.height - 1
                            y = random.randint(0, self.width - 1)
                        else:
                            x = random.randint(0, self.height - 1)
                            y = 0
                    else:
                        quadrant = random.randint(0, 3)
                        if quadrant == 0:
                            x = random.randint(0, self.height // 3)
                            y = random.randint(0, self.width // 3)
                        elif quadrant == 1:
                            x = random.randint(0, self.height // 3)
                            y = random.randint(2 * self.width // 3, self.width - 1)
                        elif quadrant == 2:
                            x = random.randint(2 * self.height // 3, self.height - 1)
                            y = random.randint(2 * self.width // 3, self.width - 1)
                        else:
                            x = random.randint(2 * self.height // 3, self.height - 1)
                            y = random.randint(0, self.width // 3)
                else:
                    x = random.randint(0, self.height - 1)
                    y = random.randint(0, self.width - 1)

                x = max(0, min(x, self.height - 1))
                y = max(0, min(y, self.width - 1))

                if self.grid[x][y] != ' ' or (x, y) == self.nest_pos:
                    continue

                if manhattan_distance(x, y, self.nest_pos[0], self.nest_pos[1]) < min_nest_distance:
                    continue

                too_close = False
                for food_pos in self.food_positions:
                    if manhattan_distance(x, y, food_pos[0], food_pos[1]) < min_food_distance:
                        too_close = True
                        break

                if not too_close:
                    self.food_positions.add((x, y))
                    break

    def update(self):
        self.current_round += 1
        ants_to_update = self.ants.copy()
        random.shuffle(ants_to_update)
        occupied_positions = set()
        occupied_positions.add(self.nest_pos)
        occupied_positions.update(self.obstacle_positions)

        for ant in ants_to_update:
            original_x, original_y = ant.x, ant.y
            ant.update(self)
            current_pos = (ant.x, ant.y)
            if current_pos in occupied_positions and current_pos != self.nest_pos:
                ant.x, ant.y = original_x, original_y
                current_pos = (ant.x, ant.y)
            occupied_positions.add(current_pos)

        self.grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        for obstacle_pos in self.obstacle_positions:
            self.grid[obstacle_pos[0]][obstacle_pos[1]] = '#'
        self.grid[self.nest_pos[0]][self.nest_pos[1]] = 'N'
        for food_pos in self.food_positions:
            self.grid[food_pos[0]][food_pos[1]] = 'F'
        random.shuffle(ants_to_update)
        for ant in ants_to_update:
            if (ant.x, ant.y) != self.nest_pos or self.grid[ant.x][ant.y] == 'N':
                if (ant.x, ant.y) not in self.obstacle_positions:
                    self.grid[ant.x][ant.y] = ant.symbol

    def render(self):
        border = colorize('+' + '-' * self.width + '+', BORDER_COLOR)
        result = [border]

        for row_idx, row in enumerate(self.grid):
            colored_row = []

            for col_idx, cell in enumerate(row):
                if cell == ' ':
                    colored_row.append(' ')
                elif cell == 'N' and (row_idx, col_idx) == self.nest_pos:
                    colored_row.append(colorize('N', NEST_COLOR))
                elif cell == 'F' and (row_idx, col_idx) in self.food_positions:
                    colored_row.append(colorize('F', FOOD_COLOR))
                elif cell == '#':
                    colored_row.append(colorize('#', OBSTACLE_COLOR))
                else:
                    ant_color = assign_color_to_ant(cell)
                    colored_row.append(colorize(cell, ant_color))

            result.append(colorize('|', BORDER_COLOR) + ''.join(colored_row) + colorize('|', BORDER_COLOR))

        result.append(border)
        return '\n'.join(result)

    def is_valid_position(self, x, y):
        return 0 <= x < self.height and 0 <= y < self.width

def get_validated_input(prompt, min_val, max_val, default=None):
    default_text = f" (default: {default})" if default is not None else ""
    while True:
        try:
            user_input = input(f"{prompt}{default_text}: ")
            if user_input == "" and default is not None:
                return default
            value = int(user_input)
            if min_val <= value <= max_val:
                return value
            print(f"Please enter a number between {min_val} and {max_val}")
        except ValueError:
            print("Please enter a valid number")

def is_data():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def main():
    print(colorize("\n=== ANT FARM SIMULATION ===", Colors.CYAN + Colors.BOLD))
    print(colorize("A competitive ant colony simulator", Colors.WHITE))
    print()
    
    ant_prompt = colorize("Enter number of ants (1-26)", Colors.YELLOW + Colors.BOLD)
    num_ants = get_validated_input(ant_prompt, 1, 26, 15)
    
    print("\n" + colorize("Would you like to use custom ant labels?", Colors.YELLOW + Colors.BOLD))
    print(colorize("1. ", Colors.YELLOW) + "No, use default labels (A, B, C, etc.)")
    print(colorize("2. ", Colors.GREEN) + "Yes, I'll provide custom labels")
    
    label_prompt = colorize("Enter choice (1-2)", Colors.YELLOW + Colors.BOLD)
    label_choice = get_validated_input(label_prompt, 1, 2, 1)
    
    custom_labels = None
    if label_choice == 2:
        while True:
            print("\n" + colorize("Enter custom labels (exactly " + str(num_ants) + " characters)", Colors.YELLOW + Colors.BOLD))
            print("Example: " + colorize("ABCDEFGHIJKLMNO", Colors.CYAN) + " for 15 ants")
            labels = input("> ").strip().upper()
            
            if len(labels) == num_ants and all(c.isalnum() for c in labels):
                custom_labels = labels
                break
            else:
                print(colorize("Error: ", Colors.RED) + f"Please enter exactly {num_ants} alphanumeric characters.")
    
    speed_options = {
        '1': 1.5,    # Slow
        '2': 0.5,    # Normal
        '3': 0.1     # Fast
    }
    
    print("\n" + colorize("Select initial game speed:", Colors.YELLOW + Colors.BOLD))
    print(colorize("1. ", Colors.YELLOW) + "Slow")
    print(colorize("2. ", Colors.GREEN) + "Normal")
    print(colorize("3. ", Colors.RED) + "Fast")
    
    speed_prompt = colorize("Enter speed (1-3)", Colors.YELLOW + Colors.BOLD)
    speed_choice = str(get_validated_input(speed_prompt, 1, 3, 2))
    game_speed = speed_options[speed_choice]
    
    world = GameWorld(width=80, height=35, num_ants=num_ants, custom_labels=custom_labels)
    
    print("\n" + colorize("Game starting...", Colors.GREEN + Colors.BOLD))
    print(colorize("Controls:", Colors.CYAN))
    print("• Press " + colorize("1-3", Colors.YELLOW + Colors.BOLD) + " during the game to change speed:")
    print("  " + colorize("1", Colors.YELLOW) + ": Slow, " + 
          colorize("2", Colors.GREEN) + ": Normal, " + 
          colorize("3", Colors.RED) + ": Fast")
    print("• Press " + colorize("q", Colors.WHITE + Colors.BOLD) + " or " + 
          colorize("Ctrl+C", Colors.WHITE + Colors.BOLD) + " to quit")
    time.sleep(2)
    
    old_settings = termios.tcgetattr(sys.stdin)
    
    try:
        tty.setcbreak(sys.stdin.fileno())
        
        round_num = 1
        running = True
        num_rounds = 1000
        while running and round_num <= num_rounds and (len(world.food_positions) > 0 or any(ant.has_food for ant in world.ants)):
            clear_screen()
            
            speed_name = "Slow" if game_speed == 1.5 else "Normal" if game_speed == 0.5 else "Fast"
            speed_color = Colors.YELLOW if speed_name == "Slow" else Colors.GREEN if speed_name == "Normal" else Colors.RED
            
            round_info = (
                colorize("Round ", Colors.CYAN + Colors.BOLD) + 
                colorize(f"{round_num}", Colors.WHITE + Colors.BOLD) + 
                colorize("/", Colors.CYAN) + 
                colorize(f"{num_rounds}", Colors.WHITE) + 
                colorize(" | Speed: ", Colors.CYAN + Colors.BOLD) + 
                colorize(f"{speed_name}", speed_color + Colors.BOLD)
            )
            print(round_info)
            
            controls = colorize("Controls: ", Colors.CYAN)
            controls += colorize("1", Colors.YELLOW) + "=Slow, "
            controls += colorize("2", Colors.GREEN) + "=Normal, "
            controls += colorize("3", Colors.RED) + "=Fast, "
            controls += colorize("q", Colors.WHITE + Colors.BOLD) + "=Quit"
            print(controls)
            
            score_key = []
            score_key.append(colorize("Score Key:", Colors.CYAN + Colors.BOLD))
            for ant in sorted(world.ants, key=lambda x: x.symbol):
                ant_color = assign_color_to_ant(ant.symbol)
                score_text = (
                    "Ant " + 
                    colorize(ant.symbol, ant_color) + 
                    ": " + 
                    colorize(str(ant.food_collected), Colors.WHITE + Colors.BOLD)
                )
                score_key.append(score_text)
            
            world_display = world.render().split('\n')
            max_score_lines = len(world_display) - 2
            
            print(world_display[0])
            for i in range(1, len(world_display)-1):
                line = world_display[i]
                if i <= len(score_key) and i <= max_score_lines:
                    print(f"{line}    {score_key[i-1]}")
                else:
                    print(line)
            print(world_display[-1])
            
            world.update()
            
            start_time = time.time()
            while time.time() - start_time < game_speed:
                if is_data():
                    key = sys.stdin.read(1)
                    if key == 'q':
                        running = False
                        break
                    elif key in speed_options:
                        game_speed = speed_options[key]
                        break
                time.sleep(0.05)
            
            if running:
                round_num += 1
    
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        
    print("\n" + colorize("GAME OVER!", Colors.RED + Colors.BOLD))
    if len(world.food_positions) == 0 and not any(ant.has_food for ant in world.ants):
        print(colorize("All food has been collected and returned to the nest!", Colors.GREEN + Colors.BOLD))
    
    sorted_ants = sorted(world.ants, key=lambda ant: (ant.food_collected, ant.distance_traveled), reverse=True)
    winner = sorted_ants[0]
    winner_color = assign_color_to_ant(winner.symbol)
    
    winner_text = (
        "\n" + colorize("WINNER", Colors.YELLOW + Colors.BOLD) + " is " +
        "Ant " + colorize(winner.symbol, winner_color + Colors.BOLD) + 
        " with " + colorize(str(winner.food_collected), Colors.WHITE + Colors.BOLD) + 
        " food collected!"
    )
    print(winner_text)
    
    tied_food = [ant for ant in world.ants if ant.food_collected == winner.food_collected and ant != winner]
    if tied_food:
        tiebreaker_text = (
            "Tiebreaker: " + colorize(winner.symbol, winner_color) + 
            " traveled " + colorize(str(winner.distance_traveled), Colors.WHITE + Colors.BOLD) +
            " squares"
        )
        print(tiebreaker_text)
    
    print("\n" + colorize("FINAL SCORES:", Colors.CYAN + Colors.BOLD))
    
    for i, ant in enumerate(sorted_ants):
        ant_color = assign_color_to_ant(ant.symbol)
        
        if i == 0:
            medal = colorize("🥇 ", Colors.YELLOW + Colors.BOLD)
        elif i == 1:
            medal = colorize("🥈 ", Colors.WHITE + Colors.BOLD)
        elif i == 2:
            medal = colorize("🥉 ", Colors.RED + Colors.BOLD)
        else:
            medal = "   "
        
        score_text = (
            medal + "Ant " + 
            colorize(ant.symbol, ant_color) + 
            ": " + 
            colorize(str(ant.food_collected), Colors.WHITE + Colors.BOLD) +
            " food, " +
            colorize(str(ant.distance_traveled), Colors.CYAN) +
            " distance"
        )
        print(score_text)

if __name__ == "__main__":
    main()
