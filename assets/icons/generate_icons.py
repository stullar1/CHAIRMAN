"""
Generate app icons for CHAIRMAN
Creates .ico (Windows) and .icns (macOS) with a professional barber-themed design
"""

import math
import struct
import zlib
from pathlib import Path


def create_chairman_icon_png(size: int = 256) -> bytes:
    """Create a professional CHAIRMAN app icon with scissors design."""
    # Colors
    bg_color = (26, 26, 26)  # Dark background #1A1A1A
    accent_color = (88, 101, 242)  # Brand blue #5865F2
    highlight_color = (114, 137, 218)  # Lighter blue
    white = (255, 255, 255)

    # Create pixel data
    pixels = []
    center = size // 2
    radius = size // 2 - size // 10

    for y in range(size):
        row = []
        for x in range(size):
            # Distance from center
            dx = x - center
            dy = y - center
            dist = math.sqrt(dx * dx + dy * dy)

            # Default to transparent/dark
            r, g, b = bg_color

            # Rounded square background
            corner_radius = size // 5
            in_bounds = True

            # Check corners
            corners = [
                (corner_radius, corner_radius),
                (size - corner_radius - 1, corner_radius),
                (corner_radius, size - corner_radius - 1),
                (size - corner_radius - 1, size - corner_radius - 1)
            ]

            for cx, cy in corners:
                if x < corner_radius and y < corner_radius:
                    if math.sqrt((x - corner_radius) ** 2 + (y - corner_radius) ** 2) > corner_radius:
                        in_bounds = False
                elif x >= size - corner_radius and y < corner_radius:
                    if math.sqrt((x - (size - corner_radius - 1)) ** 2 + (y - corner_radius) ** 2) > corner_radius:
                        in_bounds = False
                elif x < corner_radius and y >= size - corner_radius:
                    if math.sqrt((x - corner_radius) ** 2 + (y - (size - corner_radius - 1)) ** 2) > corner_radius:
                        in_bounds = False
                elif x >= size - corner_radius and y >= size - corner_radius:
                    if math.sqrt((x - (size - corner_radius - 1)) ** 2 + (y - (size - corner_radius - 1)) ** 2) > corner_radius:
                        in_bounds = False

            if not in_bounds:
                row.append(bg_color)
                continue

            # Gradient background
            gradient_factor = 1.0 - (y / size) * 0.15
            r = int(bg_color[0] * gradient_factor)
            g = int(bg_color[1] * gradient_factor)
            b = int(bg_color[2] * gradient_factor)

            # Draw a stylized "C" letter
            c_center_x = center
            c_center_y = center
            c_outer_radius = size * 0.35
            c_inner_radius = size * 0.22
            c_thickness = c_outer_radius - c_inner_radius

            # Distance from C center
            c_dx = x - c_center_x
            c_dy = y - c_center_y
            c_dist = math.sqrt(c_dx * c_dx + c_dy * c_dy)

            # Angle (for the C opening)
            angle = math.atan2(c_dy, c_dx)
            angle_deg = math.degrees(angle)

            # C shape - ring with opening on the right
            if c_inner_radius <= c_dist <= c_outer_radius:
                # Opening on the right side (between -45 and 45 degrees)
                if not (-50 <= angle_deg <= 50):
                    # Gradient on the C
                    t = (c_dist - c_inner_radius) / c_thickness
                    r = int(accent_color[0] + (highlight_color[0] - accent_color[0]) * (1 - t) * 0.3)
                    g = int(accent_color[1] + (highlight_color[1] - accent_color[1]) * (1 - t) * 0.3)
                    b = int(accent_color[2] + (highlight_color[2] - accent_color[2]) * (1 - t) * 0.3)

            # Add scissor blades as accent
            blade_length = size * 0.18
            blade_width = size * 0.04

            # Top blade (coming from the C opening)
            blade1_start_x = c_center_x + c_outer_radius * 0.7
            blade1_start_y = c_center_y - size * 0.08
            blade1_angle = math.radians(25)

            # Check if point is on blade 1
            bx = x - blade1_start_x
            by = y - blade1_start_y
            # Rotate point to blade coordinate system
            rot_x = bx * math.cos(-blade1_angle) - by * math.sin(-blade1_angle)
            rot_y = bx * math.sin(-blade1_angle) + by * math.cos(-blade1_angle)

            if 0 <= rot_x <= blade_length and abs(rot_y) <= blade_width:
                # Blade gradient
                t = rot_x / blade_length
                r = int(white[0] * (0.8 + 0.2 * t))
                g = int(white[1] * (0.8 + 0.2 * t))
                b = int(white[2] * (0.8 + 0.2 * t))

            # Bottom blade
            blade2_start_x = c_center_x + c_outer_radius * 0.7
            blade2_start_y = c_center_y + size * 0.08
            blade2_angle = math.radians(-25)

            bx = x - blade2_start_x
            by = y - blade2_start_y
            rot_x = bx * math.cos(-blade2_angle) - by * math.sin(-blade2_angle)
            rot_y = bx * math.sin(-blade2_angle) + by * math.cos(-blade2_angle)

            if 0 <= rot_x <= blade_length and abs(rot_y) <= blade_width:
                t = rot_x / blade_length
                r = int(white[0] * (0.8 + 0.2 * t))
                g = int(white[1] * (0.8 + 0.2 * t))
                b = int(white[2] * (0.8 + 0.2 * t))

            # Scissor pivot point (small circle)
            pivot_x = c_center_x + c_outer_radius * 0.65
            pivot_y = c_center_y
            pivot_radius = size * 0.035

            if math.sqrt((x - pivot_x) ** 2 + (y - pivot_y) ** 2) <= pivot_radius:
                r, g, b = accent_color

            row.append((r, g, b))
        pixels.append(row)

    # Convert to PNG
    return _pixels_to_png(pixels, size)


def _pixels_to_png(pixels: list, size: int) -> bytes:
    """Convert pixel array to PNG format."""
    # PNG header
    signature = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr_chunk = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)

    # IDAT chunk
    raw_data = b''
    for row in pixels:
        raw_data += b'\x00'  # Filter byte
        for r, g, b in row:
            raw_data += bytes([max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))])

    compressed = zlib.compress(raw_data, 9)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    idat_chunk = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)

    # IEND chunk
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)

    return signature + ihdr_chunk + idat_chunk + iend_chunk


def create_ico(sizes: list[int] = None) -> bytes:
    """Create a Windows .ico file with multiple sizes."""
    if sizes is None:
        sizes = [16, 32, 48, 256]

    images = []
    for size in sizes:
        png_data = create_chairman_icon_png(size)
        images.append((size, png_data))

    # ICO header
    ico_header = struct.pack('<HHH', 0, 1, len(images))

    # Calculate offsets
    header_size = 6 + len(images) * 16
    offset = header_size

    directory = b''
    image_data = b''

    for size, png_data in images:
        width = size if size < 256 else 0
        height = size if size < 256 else 0
        directory += struct.pack(
            '<BBBBHHII',
            width, height, 0, 0, 1, 32, len(png_data), offset
        )
        image_data += png_data
        offset += len(png_data)

    return ico_header + directory + image_data


def create_icns(sizes: list[int] = None) -> bytes:
    """Create a macOS .icns file with multiple sizes."""
    if sizes is None:
        sizes = [16, 32, 128, 256, 512]

    type_codes = {
        16: b'icp4', 32: b'icp5', 64: b'icp6',
        128: b'ic07', 256: b'ic08', 512: b'ic09', 1024: b'ic10',
    }

    icons_data = b''
    for size in sizes:
        if size in type_codes:
            png_data = create_chairman_icon_png(size)
            type_code = type_codes[size]
            icons_data += type_code + struct.pack('>I', len(png_data) + 8) + png_data

    total_length = 8 + len(icons_data)
    return b'icns' + struct.pack('>I', total_length) + icons_data


def main():
    """Generate icon files."""
    icons_dir = Path(__file__).parent

    print("Generating CHAIRMAN app icons...")

    # Generate Windows ICO
    ico_path = icons_dir / 'app_icon.ico'
    ico_data = create_ico([16, 32, 48, 256])
    with open(ico_path, 'wb') as f:
        f.write(ico_data)
    print(f"  Created: {ico_path}")

    # Generate macOS ICNS
    icns_path = icons_dir / 'app_icon.icns'
    icns_data = create_icns([16, 32, 128, 256, 512])
    with open(icns_path, 'wb') as f:
        f.write(icns_data)
    print(f"  Created: {icns_path}")

    print("\nDone! Icons feature a stylized 'C' with scissors motif.")


if __name__ == '__main__':
    main()
