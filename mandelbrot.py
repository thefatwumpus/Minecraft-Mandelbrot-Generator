import socket
import struct
import math
import time

class MinecraftRCON:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect(('localhost', 25575))
        packet = struct.pack('<ii', 1, 3) + b'python\x00\x00'
        self.sock.send(struct.pack('<i', len(packet)) + packet)
        self.sock.recv(4096)
    
    def command(self, cmd):
        packet = struct.pack('<ii', 1, 2) + cmd.encode() + b'\x00\x00'
        self.sock.send(struct.pack('<i', len(packet)) + packet)
        return self.sock.recv(4096)

def mandelbrot(c, max_iter):
    """Calculate if point escapes the Mandelbrot set"""
    z = 0
    for n in range(max_iter):
        if abs(z) > 2:
            return n  # Escaped after n iterations
        z = z*z + c
    return max_iter  # Never escaped

def get_block_color(iter_count, max_iter):
    """Choose block color based on escape speed"""
    if iter_count == max_iter:
        return "black_wool"  # Never escaped
    
    colors = [
        "white_wool", "orange_wool", "magenta_wool", "light_blue_wool",
        "yellow_wool", "lime_wool", "pink_wool", "gray_wool",
        "light_gray_wool", "cyan_wool", "purple_wool", "blue_wool", 
        "brown_wool", "green_wool", "red_wool", "black_wool"
    ]
    return colors[iter_count % len(colors)]

mc = MinecraftRCON()

print(" MANDELBROT FRACTAL GENERATOR")
print("======================================")
print()

center_x, center_y, center_z = 0, 70, 0
print(f"Drawing at: X={center_x}, Y={center_y}, Z={center_z}")
print()

patterns = [
    # (width, height, max_iter, scale, block_type, description)
    (200, 200, 30, 0.015, "wool", "GIANT Mandelbrot - Full View"),      # Much larger scale
    (300, 300, 40, 0.010, "wool", "MASSIVE View - Huge Area"),         # Even bigger
    (400, 400, 50, 0.007, "wool", "COLOSSAL - Epic Scale"),            # Massive
    (150, 150, 100, 0.002, "wool", "Detailed Zoom - Seahorse Valley"), # One zoomed-in for contrast
]

previous_pattern_points = None

for pattern_idx, (width, height, max_iter, scale, block_type, description) in enumerate(patterns):
    print()
    print(f" PATTERN {pattern_idx + 1}: {description}")
    print(f" Size: {width}x{height} ({width*height} total blocks)")
    print(f" Iterations: {max_iter}, Scale: {scale}")
    print(f" Minecraft Area: {width} x {height} blocks")
    print(f" Block: {block_type}")
    
    # REMOVE previous pattern if it exists
    if previous_pattern_points is not None:
        print(" Removing previous pattern...")
        points_removed = 0
        for block_x, block_z in previous_pattern_points:
            mc.command(f"setblock {block_x} {center_y} {block_z} air")
            points_removed += 1
            if points_removed % 200 == 0:  # Increased for larger areas
                time.sleep(0.1)
        print(f" Removed {points_removed} blocks")
        time.sleep(1)
    
    # Mark center
    mc.command(f"setblock {center_x} {center_y} {center_z} diamond_block")
    mc.command(f"say Drawing: {description}")
    
    print(f" Generating MASSIVE {width}x{height} Mandelbrot...")
    print(" This may take several minutes for the largest patterns...")
    
    start_x = center_x - width // 2
    start_z = center_z - height // 2
    
    current_pattern_points = set()
    blocks_placed = 0
    start_time = time.time()
    
    # Generate Mandelbrot pattern
    for x in range(width):
        for z in range(height):
            # Convert to complex coordinates with expanded scale
            real = (x - width/2) * scale
            imag = (z - height/2) * scale
            c = complex(real, imag)
            
            # Calculate Mandelbrot
            iter_count = mandelbrot(c, max_iter)
            
            # Get block color
            if block_type == "wool":
                color_name = get_block_color(iter_count, max_iter)
                full_block_type = color_name
            else:
                full_block_type = block_type
            
            # Calculate world coordinates - Y is fixed at 70
            world_x = start_x + x
            world_z = start_z + z
            
            # Store point for later removal
            current_pattern_points.add((world_x, world_z))
            
            # Place block at Y=70
            mc.command(f"setblock {world_x} {center_y} {world_z} {full_block_type}")
            blocks_placed += 1
            
            # Progress updates - less frequent for huge patterns
            if blocks_placed % 250 == 0:  # Reduced frequency for performance
                elapsed = time.time() - start_time
                percent = (blocks_placed / (width * height)) * 100
                print(f" Progress: {blocks_placed}/{width*height} ({percent:.1f}%) - {elapsed:.1f}s")
                time.sleep(0.05)  # Shorter delay
    
    total_time = time.time() - start_time
    print(f" Pattern {pattern_idx + 1} complete!")
    print(f" Time: {total_time:.1f}s, Blocks: {blocks_placed}")
    print(f" Area covered: {width} x {height} blocks")
    
    previous_pattern_points = current_pattern_points
    
    # Wait for user before replacing with next pattern (except for final pattern)
    if pattern_idx < len(patterns) - 1:
        print()
        print(f" Next pattern will be {patterns[pattern_idx + 1][0]}x{patterns[pattern_idx + 1][1]} blocks")
        input(" Press Enter to REMOVE this pattern and draw next one...")
    else:
        print()
        print(" MANDELBROT COMPLETE")
        print(" You now have a choice:")
        print(" 1. Keep this pattern (it will remain visible)")
        print(" 2. Remove this pattern (clean up everything)")
        print()
        
        while True:
            choice = input(" Enter 'keep' or 'remove': ").lower().strip()
            if choice in ['keep', 'remove']:
                break
            print(" Please enter 'keep' or 'remove'")
        
        if choice == 'remove':
            print(" Removing final pattern...")
            points_removed = 0
            for block_x, block_z in previous_pattern_points:
                mc.command(f"setblock {block_x} {center_y} {block_z} air")
                points_removed += 1
                if points_removed % 200 == 0:
                    time.sleep(0.1)
            mc.command(f"setblock {center_x} {center_y} {center_z} air")  
            mc.command("say Massive Mandelbrot cleaned up!")
            print(f" Final pattern removed! ({points_removed} blocks)")
        else:
            mc.command("say Massive Mandelbrot complete! Epic fractal saved!")
            print(" Final pattern kept! Enjoy your EPIC fractal!")

print()
print(" PROGRAM DONE ")
if 'choice' in locals() and choice == 'keep':
    print(f" Mandelbrot fractal remains at (0, {center_y}, 0)")
    print(f" It spans approximately {patterns[-1][0]} x {patterns[-1][1]} blocks")
else:
    print(" Everything has been cleaned up")
