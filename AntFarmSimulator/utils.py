import os
import random

# ANSI color codes
class Colors:
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Styles
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # Reset
    RESET = "\033[0m"

# Define a list of color schemes for ants
ANT_COLOR_SCHEMES = [
    Colors.RED,                                 # 0
    Colors.GREEN,                               # 1
    Colors.YELLOW,                              # 2
    Colors.BLUE,                                # 3
    Colors.MAGENTA,                             # 4
    Colors.CYAN,                                # 5
    Colors.RED + Colors.BOLD,                   # 6
    Colors.GREEN + Colors.BOLD,                 # 7
    Colors.YELLOW + Colors.BOLD,                # 8
    Colors.BLUE + Colors.BOLD,                  # 9
    Colors.MAGENTA + Colors.BOLD,               # 10
    Colors.CYAN + Colors.BOLD,                  # 11
    Colors.RED + Colors.UNDERLINE,              # 12
    Colors.GREEN + Colors.UNDERLINE,            # 13
    Colors.YELLOW + Colors.UNDERLINE,           # 14
    Colors.BLUE + Colors.UNDERLINE,             # 15
    Colors.MAGENTA + Colors.UNDERLINE,          # 16
    Colors.CYAN + Colors.UNDERLINE,             # 17
    Colors.RED + Colors.BOLD + Colors.UNDERLINE,    # 18
    Colors.GREEN + Colors.BOLD + Colors.UNDERLINE,  # 19
    Colors.YELLOW + Colors.BOLD + Colors.UNDERLINE, # 20
    Colors.BLUE + Colors.BOLD + Colors.UNDERLINE,   # 21
    Colors.MAGENTA + Colors.BOLD + Colors.UNDERLINE,# 22
    Colors.CYAN + Colors.BOLD + Colors.UNDERLINE,   # 23
    Colors.WHITE + Colors.BOLD,                 # 24
    Colors.WHITE + Colors.UNDERLINE             # 25
]

# Color assignment for game elements - pre-define A-Z for compatibility
ANT_COLORS = {
    'A': ANT_COLOR_SCHEMES[0],
    'B': ANT_COLOR_SCHEMES[1],
    'C': ANT_COLOR_SCHEMES[2],
    'D': ANT_COLOR_SCHEMES[3],
    'E': ANT_COLOR_SCHEMES[4],
    'F': ANT_COLOR_SCHEMES[5],
    'G': ANT_COLOR_SCHEMES[6],
    'H': ANT_COLOR_SCHEMES[7],
    'I': ANT_COLOR_SCHEMES[8],
    'J': ANT_COLOR_SCHEMES[9],
    'K': ANT_COLOR_SCHEMES[10],
    'L': ANT_COLOR_SCHEMES[11],
    'M': ANT_COLOR_SCHEMES[12],
    'N': ANT_COLOR_SCHEMES[13],
    'O': ANT_COLOR_SCHEMES[14],
    'P': ANT_COLOR_SCHEMES[15],
    'Q': ANT_COLOR_SCHEMES[16],
    'R': ANT_COLOR_SCHEMES[17],
    'S': ANT_COLOR_SCHEMES[18],
    'T': ANT_COLOR_SCHEMES[19],
    'U': ANT_COLOR_SCHEMES[20],
    'V': ANT_COLOR_SCHEMES[21],
    'W': ANT_COLOR_SCHEMES[22],
    'X': ANT_COLOR_SCHEMES[23],
    'Y': ANT_COLOR_SCHEMES[24],
    'Z': ANT_COLOR_SCHEMES[25]
}

# Function to assign colors to custom labels
def assign_color_to_ant(symbol):
    """Get a color for a custom ant symbol"""
    if symbol in ANT_COLORS:
        return ANT_COLORS[symbol]
    
    # For symbols not in the predefined map, calculate a color
    # We'll use the ordinal value of the character to pick from our schemes
    color_index = ord(symbol) % len(ANT_COLOR_SCHEMES)
    return ANT_COLOR_SCHEMES[color_index]

# Other game element colors
NEST_COLOR = Colors.BG_BLUE + Colors.WHITE + Colors.BOLD
FOOD_COLOR = Colors.BG_GREEN + Colors.WHITE
BORDER_COLOR = Colors.WHITE + Colors.BOLD
OBSTACLE_COLOR = Colors.BG_BLACK + Colors.WHITE
# Color for ants carrying food (high contrast)
CARRYING_ANT_COLOR = Colors.BG_YELLOW + Colors.BLACK + Colors.BOLD

# Vintage Antfarm Frame Colors
FRAME_COLOR = Colors.YELLOW + Colors.BOLD
FRAME_ACCENT_COLOR = Colors.RED + Colors.BOLD
FRAME_LABEL_COLOR = Colors.WHITE + Colors.BOLD

def colorize(text, color_code):
    """Add color to text using ANSI escape sequences"""
    return f"{color_code}{text}{Colors.RESET}"

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def manhattan_distance(x1, y1, x2, y2):
    """Calculate Manhattan distance between two points"""
    return abs(x2 - x1) + abs(y2 - y1)
