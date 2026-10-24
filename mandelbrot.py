import socket
import struct
import math
import time

class MinecraftRCON:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect(('localhost', 25575))
        packet = struct.pack('<ii', 1, 3) + b'YOUR_PASSWORD\x00\x00'
        self.sock.send(struct.pack('<i', len(packet)) + packet)
        self.sock.recv(4096)

    def command(self, cmd):
        packet = struct.pack('<ii', 1, 2) + cmd.encode() + b'\x00\x00'
        self.sock.send(struct.pack('<i', len(packet)) + packet)
        response = self.sock.recv(4096)
        time.sleep(0.01)
        return response

def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def generate_ulam_spiral_coordinates(size):
    spiral = {}
    x, z = 0, 0
    direction = 0
    steps = 1
    step_count = 0
    segment_passed = 0

    max_num = size * size
    for n in range(1, max_num + 1):
        spiral[n] = (x, z)

        if direction == 0:
            x += 1
        elif direction == 1:
            z += 1
        elif direction == 2:
            x -= 1
        elif direction == 3:
            z -= 1

        step_count += 1

        if step_count == steps:
            step_count = 0
            direction = (direction + 1) % 4
            segment_passed += 1

            if segment_passed == 2:
                steps += 1
                segment_passed = 0

    return spiral

def generate_spiral_with_connections(size, scale=1):
    spiral = generate_ulam_spiral_coordinates(size)

    primes = []
    max_num = size * size
    for n in range(1, max_num + 1):
        if is_prime(n):
            primes.append((n, spiral[n]))

    prime_coords = set()
    connection_coords = set()
    all_coords = set()

    previous_coord = None

    for i, (n, coord) in enumerate(primes):
        x, z = coord

        scaled_x = x * scale
        scaled_z = z * scale

        prime_coords.add((scaled_x, scaled_z))
        all_coords.add((scaled_x, scaled_z))

        if previous_coord is not None:
            prev_x, prev_z = previous_coord
            prev_x *= scale
            prev_z *= scale

            dx = scaled_x - prev_x
            dz = scaled_z - prev_z
            distance = max(abs(dx), abs(dz))

            if distance > 0:
                for j in range(distance + 1):
                    t = j / distance
                    line_x = int(prev_x + dx * t)
                    line_z = int(prev_z + dz * t)
                    connection_coords.add((line_x, line_z))
                    all_coords.add((line_x, line_z))

        previous_coord = (x, z)

    return prime_coords, connection_coords, all_coords

try:
    mc = MinecraftRCON()
except:
    exit(1)

center_x, center_y, center_z = 0, 70, 0

SPIRAL_SIZE = 100
SCALE = 2

prime_coords, connection_coords, all_coords = generate_spiral_with_connections(SPIRAL_SIZE, SCALE)

mc.command(f"setblock {center_x} {center_y} {center_z} diamond_block")

for x, z in connection_coords:
    block_x = center_x + x
    block_z = center_z + z
    mc.command(f"setblock {block_x} {center_y} {block_z} light_gray_concrete")

for x, z in prime_coords:
    block_x = center_x + x
    block_z = center_z + z
    mc.command(f"setblock {block_x} {center_y} {block_z} redstone_block")

border_radius = SPIRAL_SIZE * SCALE // 2 + 2
for i in range(-border_radius, border_radius + 1):
    mc.command(f"setblock {center_x+i} {center_y} {center_z-border_radius} gold_block")
    mc.command(f"setblock {center_x+i} {center_y} {center_z+border_radius} gold_block")
    mc.command(f"setblock {center_x-border_radius} {center_y} {center_z+i} gold_block")
    mc.command(f"setblock {center_x+border_radius} {center_y} {center_z+i} gold_block")

legend_y = center_y + 1
legend_z = center_z - border_radius - 3
mc.command(f"setblock {center_x} {legend_y} {legend_z} oak_sign")
mc.command(f"data merge block {center_x} {legend_y} {legend_z} " +
           '{Text1:\'{"text":"' + str(SPIRAL_SIZE) + 'x' + str(SPIRAL_SIZE) + '"}\',' +
           'Text2:\'{"text":"Ulam Spiral"}\',' +
           'Text3:\'{"text":"Red=Prime"}\',' +
           'Text4:\'{"text":"' + str(len(prime_coords)) + ' primes"}\'}')

total_numbers = SPIRAL_SIZE * SPIRAL_SIZE
prime_count = len(prime_coords)
prime_percent = (prime_count / total_numbers) * 100

largest_prime = total_numbers
while not is_prime(largest_prime):
    largest_prime -= 1

print(f"Spiral size: {SPIRAL_SIZE}x{SPIRAL_SIZE}")
print(f"Scale factor: {SCALE}x")
print(f"Display area: {SPIRAL_SIZE*SCALE}x{SPIRAL_SIZE*SCALE} blocks")
print(f"Numbers in spiral: {total_numbers}")
print(f"Prime numbers found: {prime_count}")
print(f"Prime percentage: {prime_percent:.2f}%")
print(f"Largest prime in spiral: {largest_prime}")
print(f"Total blocks placed: {len(all_coords)}")
print(f"Connection blocks: {len(connection_coords)}")
print(f"Prime blocks: {prime_count}")
print("Ulam spiral drawn and left in place")
