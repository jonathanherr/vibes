import math
import argparse
from PIL import Image
import numpy as np
import os

# --- Configuration ---

class Config:
    # Image and Layout
    image_path: str = "input.png" # Placeholder, will be set by args
    output_gcode_path: str = "output.gcode" # Placeholder
    num_cols: int = 20          # Number of scales horizontally
    num_rows: int = 15          # Number of scales vertically
    stagger_offset_factor: float = 0.5 # 0.5 for standard staggering

    # Scale Geometry (in mm)
    scale_width: float = 15.0
    scale_height: float = 20.0
    scale_corner_radius: float = 3.0 # Radius for rounded corners
    scale_base_thickness: float = 1.2 # Thickness before image relief
    hole_diameter: float = 2.5
    hole_offset_x: float = 3.0  # Offset from scale centerline
    hole_offset_y: float = 3.0  # Offset down from top edge

    # Image Mapping
    max_relief_height: float = 0.6 # Max additional Z height for black pixels
    relief_layers: int = 2 # How many top layers get the relief height

    # Print Settings
    layer_height: float = 0.2
    line_width: float = 0.4 # Assumed nozzle diameter/line width
    print_speed: float = 2400  # mm/min (G1 movements)
    travel_speed: float = 4000  # mm/min (G0 movements)
    nozzle_temp: int = 210
    bed_temp: int = 60
    filament_diameter: float = 1.75
    retraction_amount: float = 1.0
    retraction_speed: float = 2400 # mm/min
    z_hop: float = 0.4 # Z lift during travel moves

    # --- Calculated Internal ---
    _extrusion_multiplier: float = 1.0 # Can be adjusted for flow rate
    _extrusion_per_mm: float = 0.0 # Will be calculated

    def calculate_extrusion(self):
        """Calculate extrusion amount per mm of linear movement."""
        area = math.pi * (self.filament_diameter / 2)**2
        self._extrusion_per_mm = (self.layer_height * self.line_width / area) * self._extrusion_multiplier

# --- Helper Functions ---

def generate_rounded_rect_points(cx, cy, width, height, radius, segments=10):
    """Generates points for a rounded rectangle centered at (cx, cy)."""
    points = []
    w = width / 2 - radius
    h = height / 2 - radius

    # Top right corner
    for i in range(segments + 1):
        angle = math.pi / 2 * (i / segments)
        points.append((cx + w + radius * math.cos(angle), cy + h + radius * math.sin(angle)))
    # Top left corner
    for i in range(segments + 1):
        angle = math.pi / 2 + math.pi / 2 * (i / segments)
        points.append((cx - w + radius * math.cos(angle), cy + h + radius * math.sin(angle)))
    # Bottom left corner
    for i in range(segments + 1):
        angle = math.pi + math.pi / 2 * (i / segments)
        points.append((cx - w + radius * math.cos(angle), cy - h + radius * math.sin(angle)))
    # Bottom right corner
    for i in range(segments + 1):
        angle = 3 * math.pi / 2 + math.pi / 2 * (i / segments)
        points.append((cx + w + radius * math.cos(angle), cy - h + radius * math.sin(angle)))

    # Close the loop by adding the first point again if needed (often handled by caller)
    # points.append(points[0])
    return points

def generate_circle_points(cx, cy, radius, segments=12):
    """Generates points for a circle centered at (cx, cy)."""
    points = []
    for i in range(segments):
        angle = 2 * math.pi * (i / segments)
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    points.append(points[0]) # Close the circle
    return points

def gcode_move(x, y, z=None, feedrate=None):
    """Format a G0 or G1 move command."""
    cmd = "G0" if feedrate is None else "G1"
    if x is not None:
        cmd += f" X{x:.3f}"
    if y is not None:
        cmd += f" Y{y:.3f}"
    if z is not None:
        cmd += f" Z{z:.3f}"
    if feedrate is not None:
        cmd += f" F{feedrate}"
    return cmd + "\n"

def gcode_extrude_move(x, y, z, e, feedrate):
    """Format a G1 move command with extrusion."""
    return f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} E{e:.5f} F{feedrate}\n"

def gcode_retract(e_current, config):
    """Generate retraction G-code."""
    e_new = e_current - config.retraction_amount
    return f"G1 E{e_new:.5f} F{config.retraction_speed}\n", e_new

def gcode_unretract(e_current, config):
    """Generate un-retraction (prime) G-code."""
    e_new = e_current + config.retraction_amount
    # No F needed typically for unretract G1, uses last retract speed or default
    return f"G1 E{e_new:.5f} F{config.retraction_speed}\n", e_new

# --- Main G-code Generation Logic ---

def generate_gcode(config: Config):
    """Generates the G-code file."""
    config.calculate_extrusion() # Calculate extrusion factor

    print("Loading and preparing image...")
    try:
        img = Image.open(config.image_path).convert('L') # Open and convert to grayscale
        # Resize image to match scale grid, using LANCZOS for better quality
        img_resized = img.resize((config.num_cols, config.num_rows), Image.Resampling.LANCZOS)
        pixel_data = np.array(img_resized)
        print(f"Image loaded and resized to {config.num_cols}x{config.num_rows} pixels.")
    except FileNotFoundError:
        print(f"Error: Image file not found at '{config.image_path}'")
        return
    except Exception as e:
        print(f"Error processing image: {e}")
        return

    gcode = []
    current_e = 0.0
    current_z = 0.0

    # --- G-code Preamble ---
    print("Generating G-code preamble...")
    gcode.append("; Generated by Image Scale Mail Generator\n")
    gcode.append("; Image: {}\n".format(os.path.basename(config.image_path)))
    gcode.append("; Scales: {}x{}\n".format(config.num_cols, config.num_rows))
    gcode.append("; Layer Height: {}\n".format(config.layer_height))
    gcode.append("; Relief Height: {}\n".format(config.max_relief_height))
    gcode.append("\n")
    gcode.append("M140 S{}\n".format(config.bed_temp))      # Set Bed Temp
    gcode.append("M104 S{}\n".format(config.nozzle_temp))   # Set Nozzle Temp (No Wait)
    gcode.append("G90\n")                                  # Absolute Positioning
    gcode.append("G21\n")                                  # Metric Units
    gcode.append("G28\n")                                  # Home All Axes
    gcode.append("M190 S{}\n".format(config.bed_temp))      # Wait for Bed Temp
    gcode.append("M109 S{}\n".format(config.nozzle_temp))   # Wait for Nozzle Temp
    gcode.append("G92 E0\n")                               # Reset Extruder
    gcode.append("G1 Z5.0 F3000\n")                        # Move Z up
    # Optional: Add a prime line here if desired
    gcode.append("G92 E0\n")                               # Reset Extruder again after prime
    gcode.append("\n; --- Start Printing Scales ---\n")

    # --- Scale Printing Loop ---
    num_base_layers = max(1, int(config.scale_base_thickness / config.layer_height))
    total_layers = num_base_layers + config.relief_layers

    print(f"Printing {config.num_rows} rows and {config.num_cols} columns.")
    print(f"Base layers: {num_base_layers}, Relief layers: {config.relief_layers}")

    # Calculate overall bounding box to center the print (optional)
    total_width = config.num_cols * config.scale_width * (1 - (1 - config.stagger_offset_factor) * 0.5) # Approximate
    total_height = config.num_rows * (config.scale_height * 0.75) # Rough estimate for overlap
    offset_x = 50 # Center offset X (adjust based on printer bed size)
    offset_y = 50 # Center offset Y

    last_x, last_y = 0, 0 # Keep track of last position for distance calculation

    for r in range(config.num_rows):
        print(f"Processing Row {r+1}/{config.num_rows}")
        for c in range(config.num_cols):
            # Calculate scale center position
            stagger = (config.scale_width * config.stagger_offset_factor) if r % 2 != 0 else 0
            center_x = offset_x + stagger + c * config.scale_width + config.scale_width / 2
            # Adjust Y position for overlap (simple vertical overlap)
            center_y = offset_y + r * (config.scale_height * 0.7) + config.scale_height / 2 # Adjust 0.7 for desired overlap

            # Get pixel value (0-255, 0=black, 255=white)
            # Image origin is top-left, numpy array is [row, col]
            pixel_val = pixel_data[r, c]

            # Map pixel value to Z offset (inverted: black=max height)
            # Normalize pixel value (0.0 to 1.0)
            norm_pixel = pixel_val / 255.0
            # Calculate Z offset (higher value for darker pixels)
            z_relief_offset = config.max_relief_height * (1.0 - norm_pixel)

            # --- Print Single Scale ---
            gcode.append(f"; Scale R{r} C{c} | Pixel: {pixel_val} | Z-Offset: {z_relief_offset:.3f}\n")

            # Define scale geometry points
            scale_outline = generate_rounded_rect_points(
                center_x, center_y, config.scale_width, config.scale_height, config.scale_corner_radius
            )
            hole_radius = config.hole_diameter / 2
            hole1_center_x = center_x - config.hole_offset_x
            hole2_center_x = center_x + config.hole_offset_x
            hole_center_y = center_y + config.scale_height / 2 - config.hole_offset_y
            hole1_points = generate_circle_points(hole1_center_x, hole_center_y, hole_radius)
            hole2_points = generate_circle_points(hole2_center_x, hole_center_y, hole_radius)

            # Travel to start point of the scale (first layer)
            start_x, start_y = scale_outline[0]
            current_z = config.layer_height # Z for the first layer
            gcode.append(f"; Travel to scale start R{r} C{c}\n")
            # Retract before travel
            retract_gcode, current_e = gcode_retract(current_e, config)
            gcode.append(retract_gcode)
            # Z-Hop up
            gcode.append(gcode_move(x=None, y=None, z=current_z + config.z_hop, feedrate=config.travel_speed))
            # Move to perimeter start
            gcode.append(gcode_move(x=start_x, y=start_y, z=None, feedrate=config.travel_speed))
            # Z-Hop down
            gcode.append(gcode_move(x=None, y=None, z=current_z, feedrate=config.travel_speed))
            # Unretract after travel
            unretract_gcode, current_e = gcode_unretract(current_e, config)
            gcode.append(unretract_gcode)

            # --- Print Layers ---
            for layer_num in range(total_layers):
                layer_z = (layer_num + 1) * config.layer_height
                is_relief_layer = layer_num >= num_base_layers
                current_layer_relief = z_relief_offset if is_relief_layer else 0.0
                target_z = layer_z + current_layer_relief

                gcode.append(f"; Layer {layer_num+1}/{total_layers} at Z={target_z:.3f}\n")

                # Print Scale Outline
                last_layer_x, last_layer_y = start_x, start_y
                for px, py in scale_outline[1:] + [scale_outline[0]]: # Loop back to start
                    dist = math.sqrt((px - last_layer_x)**2 + (py - last_layer_y)**2)
                    current_e += dist * config._extrusion_per_mm
                    gcode.append(gcode_extrude_move(px, py, target_z, current_e, config.print_speed))
                    last_layer_x, last_layer_y = px, py

                # Print Holes (as perimeters within the scale) - simple approach
                # Travel to hole 1 start (no retraction needed if close)
                h1_start_x, h1_start_y = hole1_points[0]
                gcode.append(gcode_move(x=h1_start_x, y=h1_start_y, z=target_z, feedrate=config.travel_speed)) # Move inside
                # Print hole 1 perimeter
                last_layer_x, last_layer_y = h1_start_x, h1_start_y
                for px, py in hole1_points[1:]:
                    dist = math.sqrt((px - last_layer_x)**2 + (py - last_layer_y)**2)
                    current_e += dist * config._extrusion_per_mm
                    gcode.append(gcode_extrude_move(px, py, target_z, current_e, config.print_speed))
                    last_layer_x, last_layer_y = px, py

                # Travel to hole 2 start
                h2_start_x, h2_start_y = hole2_points[0]
                gcode.append(gcode_move(x=h2_start_x, y=h2_start_y, z=target_z, feedrate=config.travel_speed)) # Move inside
                # Print hole 2 perimeter
                last_layer_x, last_layer_y = h2_start_x, h2_start_y
                for px, py in hole2_points[1:]:
                    dist = math.sqrt((px - last_layer_x)**2 + (py - last_layer_y)**2)
                    current_e += dist * config._extrusion_per_mm
                    gcode.append(gcode_extrude_move(px, py, target_z, current_e, config.print_speed))
                    last_layer_x, last_layer_y = px, py

                # TODO: Add simple infill for relief layers if desired (e.g., zig-zag)
                # This part is complex to do well without a full slicer logic.
                # For now, only perimeters are printed.

            # Update last position after finishing the scale
            # For simplicity, use the last point of the last hole printed
            last_x, last_y = last_layer_x, last_layer_y
            current_z = target_z # Update current Z

    # --- G-code Postamble ---
    print("Generating G-code postamble...")
    gcode.append("\n; --- End Print ---\n")
    # Retract filament
    retract_gcode, current_e = gcode_retract(current_e, config)
    gcode.append(retract_gcode)
    gcode.append("G91\n") # Relative positioning
    gcode.append("G1 Z10 F3000\n") # Move Z up 10mm
    gcode.append("G90\n") # Absolute positioning
    gcode.append("G1 X10 Y200 F{}\n".format(config.travel_speed)) # Present Print
    gcode.append("M104 S0\n")                                    # Turn off nozzle heater
    gcode.append("M140 S0\n")                                    # Turn off bed heater
    gcode.append("M84\n")                                        # Disable motors
    gcode.append("M107\n")                                       # Turn off fan
    gcode.append("; End of G-code\n")

    # --- Write G-code to File ---
    print(f"Writing G-code to {config.output_gcode_path}...")
    try:
        with open(config.output_gcode_path, 'w') as f:
            f.writelines(gcode)
        print("G-code generation complete.")
    except Exception as e:
        print(f"Error writing G-code file: {e}")

# --- Command Line Interface ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert an image into G-code for articulated scale mail armor relief.")
    parser.add_argument("image_path", help="Path to the input image file (e.g., image.png)")
    parser.add_argument("-o", "--output", default="output.gcode", help="Path to the output G-code file (default: output.gcode)")
    parser.add_argument("--cols", type=int, default=20, help="Number of scale columns")
    parser.add_argument("--rows", type=int, default=15, help="Number of scale rows")
    parser.add_argument("--sw", "--scale-width", type=float, default=15.0, dest="scale_width", help="Width of a single scale (mm)")
    parser.add_argument("--sh", "--scale-height", type=float, default=20.0, dest="scale_height", help="Height of a single scale (mm)")
    parser.add_argument("--lh", "--layer-height", type=float, default=0.2, dest="layer_height", help="Print layer height (mm)")
    parser.add_argument("--relief", type=float, default=0.6, dest="max_relief_height", help="Maximum relief height for black pixels (mm)")
    parser.add_argument("--base", type=float, default=1.2, dest="scale_base_thickness", help="Base thickness of the scale before relief (mm)")
    parser.add_argument("--temp", type=int, default=210, dest="nozzle_temp", help="Nozzle temperature (°C)")
    parser.add_argument("--bed", type=int, default=60, dest="bed_temp", help="Bed temperature (°C)")
    parser.add_argument("--speed", type=int, default=2400, dest="print_speed", help="Printing speed (mm/min)")

    args = parser.parse_args()

    # Create a Config object and override defaults with parsed arguments
    config = Config()
    config.image_path = args.image_path
    config.output_gcode_path = args.output
    config.num_cols = args.cols
    config.num_rows = args.rows
    config.scale_width = args.scale_width
    config.scale_height = args.scale_height
    config.layer_height = args.layer_height
    config.max_relief_height = args.max_relief_height
    config.scale_base_thickness = args.scale_base_thickness
    config.nozzle_temp = args.nozzle_temp
    config.bed_temp = args.bed_temp
    config.print_speed = args.print_speed
    # You can add more arguments for other Config parameters if needed

    generate_gcode(config)
