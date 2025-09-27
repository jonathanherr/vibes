#!/usr/bin/env python3
import os
import time
import sys
import select
import tty
import termios
from game_world import GameWorld
from utils import clear_screen, colorize, ANT_COLORS, assign_color_to_ant, Colors

# Configuration Constants
MAX_ROUNDS = 300  # Balanced for completion vs speed
MAP_WIDTH = 70    # Bigger antfarm display
MAP_HEIGHT = 25   # Bigger antfarm display
STUCK_LIMIT = 5   # Very fast teleport to prevent stuck ants

def get_validated_input(prompt, min_val, max_val, default=None):
    """Get user input with validation"""
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
    """Check if keyboard input is available"""
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def main():
    # Display colorful welcome message
    print(colorize("\n=== ANT FARM SIMULATION ===", Colors.CYAN + Colors.BOLD))
    print(colorize("A competitive ant colony simulator", Colors.WHITE))
    print()
    
    # Get number of ants from user (max 26 for A-Z)
    ant_prompt = colorize("Enter number of ants (1-26)", Colors.YELLOW + Colors.BOLD)
    num_ants = get_validated_input(ant_prompt, 1, 26, 15)
    
    # Ask if user wants to use custom ant labels
    print("\n" + colorize("Would you like to use custom ant labels?", Colors.YELLOW + Colors.BOLD))
    print(colorize("1. ", Colors.YELLOW) + "No, use default labels (A, B, C, etc.)")
    print(colorize("2. ", Colors.GREEN) + "Yes, I'll provide custom labels")
    
    label_prompt = colorize("Enter choice (1-2)", Colors.YELLOW + Colors.BOLD)
    label_choice = get_validated_input(label_prompt, 1, 2, 1)
    
    # Get custom labels if requested
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
    
    # Set up speed options
    speed_options = {
        '1': 1.0,    # Slow
        '2': 0.3,    # Normal (faster default pacing)
        '3': 0.1,    # Fast
        '4': 0.05    # Turbo (hidden option for hosts)
    }
    
    # Display speed selection with colors
    print("\n" + colorize("Select initial game speed:", Colors.YELLOW + Colors.BOLD))
    print(colorize("1. ", Colors.YELLOW) + "Slow")
    print(colorize("2. ", Colors.GREEN) + "Normal")
    print(colorize("3. ", Colors.RED) + "Fast")
    
    speed_prompt = colorize("Enter speed (1-3)", Colors.YELLOW + Colors.BOLD)
    speed_choice = str(get_validated_input(speed_prompt, 1, 3, 2))
    game_speed = speed_options[speed_choice]
    
    # Initialize game with configured grid and stuck limit
    world = GameWorld(width=MAP_WIDTH, height=MAP_HEIGHT, num_ants=num_ants, custom_labels=custom_labels, stuck_limit=STUCK_LIMIT)
    
    # Display controls with colors
    print("\n" + colorize("Game starting...", Colors.GREEN + Colors.BOLD))
    print(colorize("Controls:", Colors.CYAN))
    print("• Press " + colorize("1-3", Colors.YELLOW + Colors.BOLD) + " during the game to change speed:")
    print("  " + colorize("1", Colors.YELLOW) + ": Slow, " + 
          colorize("2", Colors.GREEN) + ": Normal, " + 
          colorize("3", Colors.RED) + ": Fast")
    print("• Press " + colorize("q", Colors.WHITE + Colors.BOLD) + " or " + 
          colorize("Ctrl+C", Colors.WHITE + Colors.BOLD) + " to quit")
    time.sleep(2)
    
    # Save terminal settings
    old_settings = termios.tcgetattr(sys.stdin)
    
    try:
        # Set terminal to raw mode
        tty.setcbreak(sys.stdin.fileno())
        
        # Main game loop - ends when all food collected and returned to nest
        round_num = 1
        running = True
        num_rounds = MAX_ROUNDS
        while running and round_num <= num_rounds and (len(world.food_positions) > 0 or len(world.premium_food_positions) > 0 or any(ant.has_food for ant in world.ants)):
            clear_screen()
            
            # Display current state with colors
            if game_speed == 1.0:
                speed_name = "Slow"
            elif game_speed == 0.3:
                speed_name = "Normal"
            elif game_speed == 0.1:
                speed_name = "Fast"
            else:
                speed_name = "Turbo"
            speed_color = Colors.YELLOW if speed_name == "Slow" else Colors.GREEN if speed_name == "Normal" else Colors.RED
            
            # Round information with colors
            round_info = (
                colorize("Round ", Colors.CYAN + Colors.BOLD) + 
                colorize(f"{round_num}", Colors.WHITE + Colors.BOLD) + 
                colorize("/", Colors.CYAN) + 
                colorize(f"{num_rounds}", Colors.WHITE) + 
                colorize(" | Food remaining: ", Colors.CYAN + Colors.BOLD) +
                colorize(str(len(world.food_positions) + len(world.premium_food_positions)), Colors.WHITE + Colors.BOLD) +
                colorize(" | Speed: ", Colors.CYAN + Colors.BOLD) + 
                colorize(f"{speed_name}", speed_color + Colors.BOLD)
            )
            print(round_info)
            
            # Legend for spectators
            print(colorize("Legend: ", Colors.CYAN) + "F=food(1pt), " + colorize("P", Colors.MAGENTA + Colors.BOLD) + "=premium(3pts), " + colorize("yellow background", Colors.YELLOW + Colors.BOLD) + " = carrying")
            
            # Controls information
            controls = colorize("Controls: ", Colors.CYAN)
            controls += colorize("1", Colors.YELLOW) + "=Slow, "
            controls += colorize("2", Colors.GREEN) + "=Normal, "
            controls += colorize("3", Colors.RED) + "=Fast, "
            controls += colorize("q", Colors.WHITE + Colors.BOLD) + "=Quit"
            print(controls)
            
            # Prepare score key
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
            
            # Game world with score key
            world_display = world.render().split('\n')
            max_score_lines = len(world_display) - 2  # Exclude border lines
            
            # Print each line with score key
            print(world_display[0])  # Top border
            for i in range(1, len(world_display)-1):
                line = world_display[i]
                if i <= len(score_key) and i <= max_score_lines:
                    # Add padding between map and score
                    print(f"{line}    {score_key[i-1]}")
                else:
                    print(line)
            print(world_display[-1])  # Bottom border
            
            # Update game state
            world.update()
            
            # Wait for specified time while checking for keyboard input
            start_time = time.time()
            while time.time() - start_time < game_speed:
                if is_data():
                    key = sys.stdin.read(1)
                    if key == 'q':
                        running = False
                        break
                    elif key in speed_options:
                        game_speed = speed_options[key]
                        # Update display immediately when speed changes
                        break
                time.sleep(0.05)
            
            # Move to next round if still running
            if running:
                round_num += 1
    
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    
    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        
    # Game over - announce winner with colors
    print("\n" + colorize("GAME OVER!", Colors.RED + Colors.BOLD))
    if len(world.food_positions) == 0 and not any(ant.has_food for ant in world.ants):
        print(colorize("All food has been collected and returned to the nest!", Colors.GREEN + Colors.BOLD))
    
    # Find winner with tiebreaker (primary: food collected, secondary: distance traveled)
    # Sort by food collected (primary) and then by distance traveled (secondary) for tiebreaker
    # This guarantees a single winner even with tied food collection
    sorted_ants = sorted(world.ants, key=lambda ant: (ant.food_collected, ant.distance_traveled), reverse=True)
    winner = sorted_ants[0]  # First ant in the sorted list is the winner
    winner_color = assign_color_to_ant(winner.symbol)
    
    # Display winner with fancy formatting
    winner_text = (
        "\n" + colorize("WINNER", Colors.YELLOW + Colors.BOLD) + " is " +
        "Ant " + colorize(winner.symbol, winner_color + Colors.BOLD) + 
        " with " + colorize(str(winner.food_collected), Colors.WHITE + Colors.BOLD) + 
        " food collected!"
    )
    print(winner_text)
    
    # Add tiebreaker info if there was a tie in food
    tied_food = [ant for ant in world.ants if ant.food_collected == winner.food_collected and ant != winner]
    if tied_food:
        tiebreaker_text = (
            "Tiebreaker: " + colorize(winner.symbol, winner_color) + 
            " traveled " + colorize(str(winner.distance_traveled), Colors.WHITE + Colors.BOLD) +
            " squares"
        )
        print(tiebreaker_text)
    
    # Display final scores with colors
    print("\n" + colorize("FINAL SCORES:", Colors.CYAN + Colors.BOLD))
    
    # Show medal indicators for top 3
    for i, ant in enumerate(sorted_ants):
        ant_color = assign_color_to_ant(ant.symbol)
        
        # Special formatting for top 3
        if i == 0:
            medal = colorize("🥇 ", Colors.YELLOW + Colors.BOLD)  # Gold
        elif i == 1:
            medal = colorize("🥈 ", Colors.WHITE + Colors.BOLD)   # Silver
        elif i == 2:
            medal = colorize("🥉 ", Colors.RED + Colors.BOLD)     # Bronze
        else:
            medal = "   "  # Spacing for non-medalists
        
        # Include distance traveled as tiebreaker info
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
